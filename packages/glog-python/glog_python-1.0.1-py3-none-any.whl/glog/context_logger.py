"""Context-based logger for request tracing"""

from typing import Any, Dict, Optional
from threading import Lock
from contextvars import ContextVar
from .logger import Logger, default_logger


# Context keys
KEY_TRACE_ID = "trace_id"
KEY_USER_ID = "user_id"
KEY_PATHNAME = "pathname"
KEY_CLIENT_IP = "client_ip"


class ContextLogger:
    """Logger with context-specific fields"""
    
    def __init__(self, logger: Logger):
        self.logger = logger
        self.fields: Dict[str, Any] = {}
        self.top_fields: Dict[str, Any] = {}
        self._lock = Lock()
    
    def add_field(self, key: str, value: Any):
        """Add a field to context logger"""
        with self._lock:
            self.fields[key] = value
    
    def add_fields(self, fields: Dict[str, Any]):
        """Add multiple fields to context logger"""
        with self._lock:
            self.fields.update(fields)
    
    def add_top_field(self, key: str, value: Any):
        """Add a top-level field (like trace_id, user_id)"""
        with self._lock:
            self.top_fields[key] = value
    
    def get_top_field(self, key: str) -> Optional[Any]:
        """Get a top-level field"""
        with self._lock:
            return self.top_fields.get(key)
    
    def extract_logger(self) -> Logger:
        """Extract logger with all accumulated fields"""
        with self._lock:
            all_fields = {}
            all_fields.update(self.top_fields)
            all_fields.update(self.fields)
            return self.logger.with_fields(all_fields)


# Context variable for storing logger
_ctx_logger: ContextVar[Optional[ContextLogger]] = ContextVar("ctx_logger", default=None)


def to_context(logger: Logger) -> ContextLogger:
    """Add logger to context and return context logger"""
    ctx_log = ContextLogger(logger)
    _ctx_logger.set(ctx_log)
    return ctx_log


def _get_context_logger() -> Optional[ContextLogger]:
    """Get context logger if exists"""
    return _ctx_logger.get()


def extract_entry() -> Logger:
    """Extract logger from context with all accumulated fields"""
    ctx_log = _get_context_logger()
    if ctx_log is None:
        logger = default_logger()
    else:
        logger = ctx_log.extract_logger()
    
    # Add trace_id if exists
    trace_id = extract_trace_id()
    if trace_id:
        logger = logger.with_field(KEY_TRACE_ID, trace_id)
    
    return logger


def add_field(key: str, value: Any):
    """Add a field to context logger"""
    ctx_log = _get_context_logger()
    if ctx_log is not None:
        ctx_log.add_field(key, value)


def add_fields(fields: Dict[str, Any]):
    """Add multiple fields to context logger"""
    ctx_log = _get_context_logger()
    if ctx_log is not None:
        ctx_log.add_fields(fields)


def add_top_field(key: str, value: Any):
    """Add a top-level field to context logger"""
    ctx_log = _get_context_logger()
    if ctx_log is not None:
        ctx_log.add_top_field(key, value)


def add_trace_id(trace_id: str):
    """Add trace ID for request tracing"""
    add_top_field(KEY_TRACE_ID, trace_id)


def extract_trace_id() -> str:
    """Extract trace ID from context"""
    ctx_log = _get_context_logger()
    if ctx_log is None:
        return ""
    
    trace_id = ctx_log.get_top_field(KEY_TRACE_ID)
    return trace_id if trace_id else ""


def add_user_id(user_id: int):
    """Add user ID to context"""
    add_top_field(KEY_USER_ID, user_id)


def extract_user_id() -> int:
    """Extract user ID from context"""
    ctx_log = _get_context_logger()
    if ctx_log is None:
        return 0
    
    user_id = ctx_log.get_top_field(KEY_USER_ID)
    return user_id if user_id else 0


def add_pathname(pathname: str):
    """Add pathname to context"""
    add_top_field(KEY_PATHNAME, pathname)


def extract_pathname() -> str:
    """Extract pathname from context"""
    ctx_log = _get_context_logger()
    if ctx_log is None:
        return ""
    
    pathname = ctx_log.get_top_field(KEY_PATHNAME)
    return pathname if pathname else ""
