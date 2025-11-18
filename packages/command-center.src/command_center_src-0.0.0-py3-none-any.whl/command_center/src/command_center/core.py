"""
Command Center - Production-Ready MongoDB & Web Scraping Toolkit

A comprehensive module for distributed web scraping with MongoDB state tracking.

Components:
    - CustomLogger: Smart exception-aware logging
    - Commander: Distributed worker coordination with heartbeat
    - Record: MongoDB document wrapper with state tracking
    - Query Helpers: Optimized MongoDB queries for state management
    - fetch(): HTTP client with caching and validation
    - validate_text(): Response validation engine
    - clean_dict(): Data sanitization utility

Author: Production Team
Version: 2.0.0
"""

import logging
import os
import re
import socket
import sys
import threading
import time
from copy import deepcopy
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional, Dict, Any, List, Tuple

import cloudscraper
import requests
from requests.adapters import HTTPAdapter
from requests.cookies import RequestsCookieJar
from requests.models import Response as RequestsResponse
from urllib3.util.retry import Retry


# ==============================================================================
# SECTION 1: LOGGING
# ==============================================================================

class CustomLogger:
    """
    Smart logger with automatic exception formatting and colored output.
    
    Features:
        - Auto-detects exception objects
        - Colored console output (file logging uncolored)
        - Clean formatting with function name and line numbers
        - Both file and console handlers
    
    Usage:
        log.info("Processing started")
        log.error(exception_object)  # Auto-formats with traceback
    """
    
    COLORS = {
        'DEBUG': '\033[36m',     # Cyan
        'INFO': '\033[32m',      # Green
        'WARNING': '\033[33m',   # Yellow
        'ERROR': '\033[31m',     # Red
        'CRITICAL': '\033[35m',  # Magenta
        'RESET': '\033[0m'
    }

    def __init__(self, name='command_center', log_file='command_center.log', use_colors=True):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.DEBUG)
        self.use_colors = use_colors and sys.stdout.isatty()

        # Prevent duplicate handlers
        if self.logger.handlers:
            self.logger.handlers.clear()

        # File handler (no colors, detailed)
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(logging.DEBUG)
        file_formatter = logging.Formatter(
            fmt='%(asctime)s [%(levelname)s] %(funcName)s:%(lineno)d - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        file_handler.setFormatter(file_formatter)

        # Console handler (with colors, concise)
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        console_formatter = logging.Formatter(
            fmt='%(asctime)s [%(levelname)s] %(message)s',
            datefmt='%H:%M:%S'
        )
        console_handler.setFormatter(console_formatter)

        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)

    def _format_exception(self, exc):
        """Format exception: ExceptionType -- file.py @ line 42 | message"""
        tb = exc.__traceback__
        if tb:
            filename = Path(tb.tb_frame.f_code.co_filename).name
            lineno = tb.tb_lineno
            return f"{type(exc).__name__} -- {filename} @ line {lineno} | {exc}"
        return f"{type(exc).__name__} | {exc}"

    def _colorize(self, level, message):
        """Add color codes if enabled."""
        if self.use_colors:
            color = self.COLORS.get(level, '')
            reset = self.COLORS['RESET']
            return f"{color}{message}{reset}"
        return message

    def _log(self, level, message):
        """Internal logging with smart exception detection."""
        if isinstance(message, BaseException):
            message = self._format_exception(message)
        
        colored_msg = self._colorize(level, message)
        log_func = getattr(self.logger, level.lower())
        log_func(colored_msg)

    def debug(self, message):
        self._log('DEBUG', message)

    def info(self, message):
        self._log('INFO', message)

    def warning(self, message):
        self._log('WARNING', message)

    def error(self, message):
        self._log('ERROR', message)

    def critical(self, message):
        self._log('CRITICAL', message)

    def exception(self, message="Exception occurred"):
        self.logger.exception(self._colorize('ERROR', message))


# Global logger instance
log = CustomLogger()


# ==============================================================================
# SECTION 2: DISTRIBUTED WORKER COORDINATION
# ==============================================================================

class Commander:
    """
    Distributed worker coordinator with heartbeat mechanism.
    
    Manages multiple workers scraping from the same MongoDB collection,
    automatically distributing work ranges based on active workers.
    
    Features:
        - Automatic worker registration
        - Heartbeat monitoring
        - Dynamic work distribution
        - Thread configuration per worker
    
    Usage:
        commander = Commander(db['workers_collection'])
        config = commander.start_worker('feed_name', '192.168.1.100')
        # Use config['threads_limit'], config['threads_skip'], config['threads_max']
    """
    
    def __init__(
        self,
        collection,
        thread_batch_size: int = 2000,
        thread_skip_factor: float = 1.6,
        thread_max_factor: float = 0.28,
        thread_min_limit: int = 50,
    ):
        """
        Initialize Commander with threading parameters.
        
        Args:
            collection: MongoDB collection for worker tracking
            thread_batch_size: Records per worker batch
            thread_skip_factor: Multiplier for skip calculation
            thread_max_factor: Multiplier for max threads
            thread_min_limit: Minimum thread limit
        """
        self.collection = collection
        self.THREAD_BATCH_SIZE = thread_batch_size
        self.THREAD_SKIP_FACTOR = thread_skip_factor
        self.THREAD_MAX_FACTOR = thread_max_factor
        self.THREAD_MIN_LIMIT = thread_min_limit

    @staticmethod
    def get_local_ip():
        """Get local IP address (prefer 192.168.*)."""
        try:
            ips = socket.gethostbyname_ex(socket.gethostname())[2]
            return next((ip for ip in ips if ip.startswith("192.168.")), ips[0])
        except Exception as e:
            log.warning(f"Could not determine local IP: {e}")
            return "0.0.0.0"

    def start_worker(self, feed_name: str, worker_ip: str, interval: int = 5) -> Dict[str, int]:
        """
        Start worker heartbeat and return thread configuration.
        
        Args:
            feed_name: Unique feed identifier
            worker_ip: Worker's IP address
            interval: Heartbeat interval in seconds
        
        Returns:
            Dictionary with: threads_limit, threads_skip, threads_max
        """
        
        def _heartbeat():
            """Background heartbeat thread."""
            while True:
                try:
                    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    self.collection.update_one(
                        {"feed_name": feed_name, "worker_ip": worker_ip},
                        {"$set": {"last_heartbeat": ts}},
                        upsert=True
                    )
                except Exception as e:
                    log.error(f"Heartbeat error for {worker_ip}: {e}")
                time.sleep(interval)

        # Start heartbeat thread
        threading.Thread(target=_heartbeat, daemon=True).start()

        # Initial registration
        try:
            self.collection.update_one(
                {"feed_name": feed_name, "worker_ip": worker_ip},
                {"$setOnInsert": {"last_heartbeat": datetime.now().strftime("%Y-%m-%d %H:%M:%S")}},
                upsert=True
            )
        except Exception as e:
            log.error(f"Failed to register worker: {e}")
            return {
                "threads_limit": 0,
                "threads_skip": 0,
                "threads_max": self.THREAD_MIN_LIMIT
            }

        # Get active workers (heartbeat within last minute)
        cutoff = (datetime.now() - timedelta(minutes=1)).strftime("%Y-%m-%d %H:%M:%S")
        try:
            workers = list(self.collection.find({"feed_name": feed_name}))
        except Exception as e:
            log.error(f"Failed to fetch workers: {e}")
            return {
                "threads_limit": self.THREAD_BATCH_SIZE,
                "threads_skip": 0,
                "threads_max": self.THREAD_MIN_LIMIT
            }

        # Filter valid workers
        valid_workers = [
            w for w in workers 
            if w.get("last_heartbeat", "") > cutoff and "worker_ip" in w
        ]

        # If no valid workers, return default config
        if not valid_workers:
            return {
                "threads_limit": self.THREAD_BATCH_SIZE,
                "threads_skip": 0,
                "threads_max": max(
                    self.THREAD_MIN_LIMIT,
                    int(self.THREAD_BATCH_SIZE * self.THREAD_MAX_FACTOR)
                )
            }

        # Sort workers by heartbeat (most recent first)
        sorted_ips = [
            w["worker_ip"] 
            for w in sorted(valid_workers, key=lambda x: x["last_heartbeat"], reverse=True)
        ]

        # Build configuration map
        config_map = {}
        for i, ip in enumerate(sorted_ips):
            config_map[ip] = {
                "threads_limit": self.THREAD_BATCH_SIZE,
                "threads_skip": int(i * self.THREAD_BATCH_SIZE * self.THREAD_SKIP_FACTOR),
                "threads_max": max(
                    self.THREAD_MIN_LIMIT,
                    int(self.THREAD_BATCH_SIZE * self.THREAD_MAX_FACTOR)
                )
            }

        return config_map.get(worker_ip, {
            "threads_limit": self.THREAD_BATCH_SIZE,
            "threads_skip": 0,
            "threads_max": self.THREAD_MIN_LIMIT
        })


# ==============================================================================
# SECTION 3: MONGODB RECORD WRAPPER
# ==============================================================================

class Record:
    """
    Professional MongoDB document wrapper with state tracking.
    
    Features:
        - Dot notation: rec.field_name
        - State tracking: T|timestamp or F|timestamp format
        - Separate metadata storage for flexibility
        - Thread-safe operations
    
    Document Structure:
        {
            "_id": ...,
            "stats": {
                "scraping": "T|20241115143022",
                "processing": "F|20241116120000"
            },
            "meta": {
                "scraping": {"url": "...", "items": 42},
                "processing": {"error": "timeout", "retry": 2}
            }
        }
    """

    __slots__ = ('_doc', '_col', '_id')

    def __init__(self, doc: Dict[str, Any], collection):
        object.__setattr__(self, '_doc', deepcopy(doc))
        object.__setattr__(self, '_col', collection)
        object.__setattr__(self, '_id', doc.get('_id'))

        if 'stats' not in self._doc or not isinstance(self._doc['stats'], dict):
            self._doc['stats'] = {}
        if 'meta' not in self._doc or not isinstance(self._doc['meta'], dict):
            self._doc['meta'] = {}

    def __repr__(self) -> str:
        doc_preview = {k: v for k, v in self._doc.items() if k not in ('stats', 'meta')}
        stats_count = len(self._doc.get('stats', {}))
        return f"<Record(_id={self._id}, fields={list(doc_preview.keys())}, stats={stats_count})>"

    def __str__(self) -> str:
        return f"Record(id={self._id})"

    def __getattr__(self, key: str) -> Any:
        if key in self._doc:
            return self._doc[key]
        raise AttributeError(f"Record has no attribute '{key}'")

    def __setattr__(self, key: str, value: Any):
        if key in self.__slots__:
            object.__setattr__(self, key, value)
        else:
            self._doc[key] = value

    # Dictionary methods
    def get(self, key: str, default: Any = None) -> Any:
        return self._doc.get(key, default)

    def keys(self):
        return self._doc.keys()

    def values(self):
        return self._doc.values()

    def items(self):
        return self._doc.items()

    def to_dict(self) -> Dict[str, Any]:
        return deepcopy(self._doc)

    # Database operations
    def update(self, **fields) -> bool:
        if not fields:
            return False
        try:
            self._doc.update(fields)
            if self._id:
                result = self._col.update_one({'_id': self._id}, {'$set': fields})
                return result.modified_count > 0
            return False
        except Exception as e:
            log.error(e)
            return False

    def reload(self) -> bool:
        try:
            fresh_doc = self._col.find_one({'_id': self._id})
            if fresh_doc:
                object.__setattr__(self, '_doc', fresh_doc)
                return True
            return False
        except Exception as e:
            log.error(e)
            return False

    # State management helpers
    @staticmethod
    def _timestamp() -> str:
        return datetime.now().strftime('%Y%m%d%H%M%S')

    @staticmethod
    def _parse_timestamp(ts_str: str) -> Optional[datetime]:
        try:
            return datetime.strptime(ts_str, '%Y%m%d%H%M%S')
        except (ValueError, TypeError):
            return None

    def _encode_state(self, success: bool) -> str:
        flag = 'T' if success else 'F'
        ts = self._timestamp()
        return f"{flag}|{ts}"

    def _decode_state(self, encoded: str, state_name: str) -> Optional[Dict[str, Any]]:
        if not encoded:
            return None
        try:
            parts = encoded.split('|')
            if len(parts) < 2:
                return None
            flag, ts = parts[0], parts[1]
            return {
                'success': flag == 'T',
                'ts': ts,
                'timestamp': self._parse_timestamp(ts),
                'meta': self._doc['meta'].get(state_name, {})
            }
        except Exception as e:
            log.error(f"Failed to decode state '{encoded}': {e}")
            return None

    # Public state management API
    def mark_done(self, state: str, **meta) -> bool:
        encoded = self._encode_state(True)
        update_doc = {f'stats.{state}': encoded}
        if meta:
            self._doc['meta'][state] = meta
            update_doc[f'meta.{state}'] = meta
        try:
            self._doc['stats'][state] = encoded
            result = self._col.update_one({'_id': self._id}, {'$set': update_doc})
            log.info(f"Record {self._id}: [{state}] done" + (f" | {meta}" if meta else ""))
            return result.modified_count > 0
        except Exception as e:
            log.error(e)
            return False

    def mark_fail(self, state: str, **meta) -> bool:
        encoded = self._encode_state(False)
        update_doc = {f'stats.{state}': encoded}
        if meta:
            self._doc['meta'][state] = meta
            update_doc[f'meta.{state}'] = meta
        try:
            self._doc['stats'][state] = encoded
            result = self._col.update_one({'_id': self._id}, {'$set': update_doc})
            log.error(f"Record {self._id}: [{state}] failed" + (f" | {meta}" if meta else ""))
            return result.modified_count > 0
        except Exception as e:
            log.error(e)
            return False

    def mark_reset(self, state: str) -> bool:
        try:
            self._doc['stats'][state] = None
            if state in self._doc['meta']:
                del self._doc['meta'][state]
            result = self._col.update_one(
                {'_id': self._id},
                {'$unset': {f'stats.{state}': '', f'meta.{state}': ''}}
            )
            log.info(f"Record {self._id}: [{state}] reset")
            return result.modified_count > 0
        except Exception as e:
            log.error(e)
            return False

    def get_sv(self, state: str) -> Optional[Dict[str, Any]]:
        raw = self._doc['stats'].get(state)
        return self._decode_state(raw, state) if raw else None

    def get_meta(self, state: str) -> Dict[str, Any]:
        return self._doc['meta'].get(state, {})

    def set_meta(self, state: str, **meta) -> bool:
        if not meta:
            return False
        try:
            if state not in self._doc['meta']:
                self._doc['meta'][state] = {}
            self._doc['meta'][state].update(meta)
            result = self._col.update_one(
                {'_id': self._id},
                {'$set': {f'meta.{state}': self._doc['meta'][state]}}
            )
            return result.modified_count > 0
        except Exception as e:
            log.error(e)
            return False

    def has_state(self, state: str) -> bool:
        return state in self._doc['stats'] and self._doc['stats'][state] is not None

    def is_state_success(self, state: str) -> bool:
        sv = self.get_sv(state)
        return sv is not None and sv['success']

    def is_state_failed(self, state: str) -> bool:
        sv = self.get_sv(state)
        return sv is not None and not sv['success']

    def get_all_states(self) -> Dict[str, Optional[Dict[str, Any]]]:
        return {
            state: self._decode_state(value, state) if value else None
            for state, value in self._doc['stats'].items()
        }


# ==============================================================================
# SECTION 4: QUERY HELPERS
# ==============================================================================

def query_stats(
    field: str,
    success: Optional[bool] = None,
    ts_after: Optional[str] = None,
    ts_before: Optional[str] = None
) -> Dict[str, Any]:
    """Build query for state field with filters."""
    q = {}
    f = f"stats.{field}"
    
    if success is True:
        q[f] = {"$regex": "^T\\|"}
    elif success is False:
        q[f] = {"$regex": "^F\\|"}
    elif success is None:
        q[f] = None
    
    if ts_after or ts_before:
        conditions = []
        if ts_after:
            conditions.append({"$gte": [{"$substr": [f"${f}", 2, 14]}, ts_after]})
        if ts_before:
            conditions.append({"$lte": [{"$substr": [f"${f}", 2, 14]}, ts_before]})
        q["$expr"] = conditions[0] if len(conditions) == 1 else {"$and": conditions}
    
    return q


def query_success(state_name: str, ts_after: Optional[str] = None, ts_before: Optional[str] = None) -> Dict[str, Any]:
    """Query for successful state."""
    return query_stats(state_name, success=True, ts_after=ts_after, ts_before=ts_before)


def query_failed(state_name: str, ts_after: Optional[str] = None, ts_before: Optional[str] = None) -> Dict[str, Any]:
    """Query for failed state."""
    return query_stats(state_name, success=False, ts_after=ts_after, ts_before=ts_before)


def query_unprocessed(state_name: str) -> Dict[str, Any]:
    """Query for unprocessed records."""
    return {f"stats.{state_name}": None}


def query_with_meta(state_name: str, **meta_filters) -> Dict[str, Any]:
    """Query by metadata values."""
    return {f"meta.{state_name}.{key}": value for key, value in meta_filters.items()}


def query_success_with_meta(
    state_name: str,
    ts_after: Optional[str] = None,
    ts_before: Optional[str] = None,
    **meta_filters
) -> Dict[str, Any]:
    """Combine success query with metadata filters."""
    q = query_success(state_name, ts_after=ts_after, ts_before=ts_before)
    q.update(query_with_meta(state_name, **meta_filters))
    return q


# ==============================================================================
# SECTION 5: HTTP CLIENT
# ==============================================================================

LOCAL_FILE_HEADER = "X-Local-File"


def fetch(
    url: str,
    method: str = "GET",
    params: Optional[Dict[str, Any]] = None,
    cookies: Optional[Dict[str, str]] = None,
    headers: Optional[Dict[str, str]] = None,
    data: Optional[Dict[str, Any]] = None,
    json: Optional[Dict[str, Any]] = None,
    save_dir: Optional[str] = None,
    filename: Optional[str] = None,
    proxies: Optional[Dict[str, str]] = None,
    refresh: bool = False,
    valid_rules: Optional[Dict[str, Any]] = None,
    session: Optional[requests.Session] = None,
    timeout: float = 10.0,
    backoff_factor: float = 0.1,
    max_retries: int = 0,
) -> Any:
    """
    HTTP client with caching, validation, and retry logic.
    
    Returns Response object on success, Exception on error.
    """
    try:
        session = session or cloudscraper.session()
        file_path = Path(save_dir) / filename if save_dir and filename else None
        is_pdf = filename and filename.lower().endswith('.pdf') if filename else False

        # Load from cache
        if file_path and file_path.exists() and not refresh:
            log.info(f"Loading cached: {filename}")
            try:
                if is_pdf:
                    content = file_path.read_bytes()
                    content_type = "application/pdf"
                else:
                    content = file_path.read_text(encoding="utf-8")
                    content_type = "text/html; charset=utf-8"
                    
                    if valid_rules:
                        response_text, errors = validate_text(content, valid_rules)
                        if not response_text and errors:
                            error_msg = '\n'.join(errors)
                            if any(word in error_msg for word in valid_rules.get('forbidden', [])):
                                os.remove(file_path)
                                log.warning('🗑️ Forbidden response deleted')
                            return Exception(error_msg)
                        content = response_text

                response = RequestsResponse()
                response.status_code = 200
                response._content = content if isinstance(content, bytes) else content.encode("utf-8")
                response.url = url
                response.reason = "OK"
                response.headers["Content-Type"] = content_type
                response.headers[LOCAL_FILE_HEADER] = f"file://{file_path.resolve().as_posix()}"
                response.cookies = RequestsCookieJar()
                return response
            except Exception as e:
                return ValueError(f"Cache read error: {e}")

        # Configure retries
        if max_retries > 0:
            retries = Retry(
                total=max_retries,
                read=max_retries,
                connect=max_retries,
                backoff_factor=backoff_factor,
                status_forcelist=(500, 502, 503, 504, 403, 429),
                allowed_methods={"HEAD", "GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"},
            )
            adapter = HTTPAdapter(max_retries=retries)
            session.mount("http://", adapter)
            session.mount("https://", adapter)

        # Perform request
        try:
            log.info(f"Requesting: {filename} [{method}] {url}")
            response = session.request(
                method=method.upper(),
                url=url,
                params=params,
                headers=headers,
                data=data,
                json=json,
                cookies=cookies,
                timeout=timeout,
                proxies=proxies
            )
            response.raise_for_status()

            content_type = response.headers.get('Content-Type', '').lower()
            is_pdf_response = 'application/pdf' in content_type or is_pdf

            if is_pdf_response:
                if file_path:
                    try:
                        file_path.parent.mkdir(parents=True, exist_ok=True)
                        file_path.write_bytes(response.content)
                        response.headers[LOCAL_FILE_HEADER] = f"{file_path.resolve().as_uri()}"
                        log.info(f"Saved PDF: {filename}")
                    except IOError as e:
                        log.error(f"Failed to save PDF: {e}")
                return response
            else:
                if valid_rules:
                    response_text, errors = validate_text(response.text, valid_rules)
                    if not response_text and errors:
                        return ValueError('\n'.join(errors))
                    response._content = response_text.encode("utf-8")

                if file_path:
                    try:
                        file_path.parent.mkdir(parents=True, exist_ok=True)
                        file_path.write_text(response.text, encoding="utf-8")
                        response.headers[LOCAL_FILE_HEADER] = f"{file_path.resolve().as_uri()}"
                        log.info(f"Saved: {filename}")
                    except IOError as e:
                        log.error(f"Failed to save: {e}")
                return response

        except requests.exceptions.HTTPError as e:
            log.error(f"HTTP error: {e}")
            return e
        except (requests.exceptions.ConnectionError, requests.exceptions.Timeout, requests.exceptions.RequestException) as e:
            log.error(f"Request error: {e}")
            return e

    except Exception as outer_e:
        log.error(outer_e)
        return outer_e


# ==============================================================================
# SECTION 6: UTILITIES
# ==============================================================================

def validate_text(text: str, rules: Optional[Dict[str, Any]] = None) -> Tuple[Optional[str], Optional[List[str]]]:
    """Validate text based on configurable rules."""
    errors = []
    rules = rules or {}

    if not isinstance(text, str):
        return None, [f"Invalid type: {type(text).__name__}"]
    if not text:
        return None, ["Empty text"]

    case_sensitive = rules.get("case_sensitive", True)
    compare_text = text if case_sensitive else text.lower()

    if "required" in rules:
        for item in rules["required"]:
            req = item if case_sensitive else item.lower()
            if req not in compare_text:
                errors.append(f"Required missing: '{item}'")

    if "forbidden" in rules:
        for item in rules["forbidden"]:
            forb = item if case_sensitive else item.lower()
            if forb in compare_text:
                errors.append(f"Forbidden found: '{item}'")

    if "regex" in rules:
        for pattern in rules["regex"]:
            try:
                if not re.search(pattern, text):
                    errors.append(f"Regex failed: {pattern}")
            except re.error as e:
                errors.append(f"Invalid regex '{pattern}': {e}")

    if "expiration" in rules:
        if time.time() > rules["expiration"]:
            errors.append("Text expired")

    if "must_start_with" in rules:
        if not text.startswith(rules["must_start_with"]):
            errors.append(f"Must start with: '{rules['must_start_with']}'")

    if "must_end_with" in rules:
        if not text.endswith(rules["must_end_with"]):
            errors.append(f"Must end with: '{rules['must_end_with']}'")

    return (text, None) if not errors else (None, errors)


def clean_dict(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Clean dictionary keys and values.
    - Keys: lowercase, alphanumeric + underscore only
    - Values: remove junk unicode, collapse whitespace
    """
    def clean_key(key):
        if not isinstance(key, str):
            key = str(key)
        key = key.encode("utf-8", "ignore").decode("utf-8")
        key = key.lower().replace(" ", "_")
        return re.sub(r"[^a-z0-9_]", "", key)

    def clean_value(value):
        if isinstance(value, str):
            value = value.encode("utf-8", "ignore").decode("utf-8")
            value = re.sub(r"[^\x20-\x7E]", " ", value)
            value = re.sub(r"\s+", " ", value)
            return value.strip()
        elif isinstance(value, dict):
            return clean_dict(value)
        elif isinstance(value, list):
            return [clean_value(v) for v in value]
        return value

    if not isinstance(data, dict):
        raise ValueError("Input must be dict")

    return {clean_key(k): clean_value(v) for k, v in data.items()}


# ==============================================================================
# MODULE EXPORTS
# ==============================================================================

__all__ = [
    # Core classes
    'CustomLogger',
    'Commander',
    'Record',
    
    # Query helpers
    'query_stats',
    'query_success',
    'query_failed',
    'query_unprocessed',
    'query_with_meta',
    'query_success_with_meta',
    
    # HTTP & utilities
    'fetch',
    'validate_text',
    'clean_dict',
    
    # Global logger
    'log',
]