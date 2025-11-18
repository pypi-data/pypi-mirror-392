"""
Python logging library compatible with glog format
Compatible with Python 3.7+
"""

from .logger import (
    Logger,
    default_logger,
    set_default_logger_config,
    error,
    errorf,
    warn,
    warnf,
    info,
    infof,
    debug,
    debugf,
    with_field,
    with_error,
)

from .level import Level
from .options import Options, OutputPath, Encoding
from .context_logger import (
    to_context,
    extract_entry,
    add_field,
    add_fields,
    add_top_field,
    add_trace_id,
    extract_trace_id,
    add_user_id,
    extract_user_id,
    add_pathname,
    extract_pathname,
)

__version__ = "1.0.0"
__author__ = "gw123"
__description__ = "Python logging library compatible with Go glog format"

__all__ = [
    "Logger",
    "Level",
    "Options",
    "OutputPath",
    "Encoding",
    "default_logger",
    "set_default_logger_config",
    "error",
    "errorf",
    "warn",
    "warnf",
    "info",
    "infof",
    "debug",
    "debugf",
    "with_field",
    "with_error",
    "to_context",
    "extract_entry",
    "add_field",
    "add_fields",
    "add_top_field",
    "add_trace_id",
    "extract_trace_id",
    "add_user_id",
    "extract_user_id",
    "add_pathname",
    "extract_pathname",
]
