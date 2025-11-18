"""Core logger implementation"""

import sys
import os
import json
import traceback
from datetime import datetime
from typing import Any, Dict, Optional, TextIO, List
from threading import Lock
from .level import Level
from .options import Options, OutputPath, Encoding


class Logger:
    """Logger with field support compatible with glog"""
    
    TIME_FORMAT = "%Y-%m-%d %H:%M:%S.%f"
    
    def __init__(
        self,
        options: Options,
        fields: Dict[str, Any] = None,
        name: str = "",
    ):
        self.options = options
        self.fields = fields or {}
        self.name = name
        self._lock = Lock()
        self._output_files: List[TextIO] = []
        self._error_files: List[TextIO] = []
        self._setup_outputs()
    
    def _setup_outputs(self):
        """Setup output file handles"""
        for path in self.options.output_paths:
            if path == OutputPath.STDOUT:
                self._output_files.append(sys.stdout)
            elif path == OutputPath.STDERR:
                self._output_files.append(sys.stderr)
            else:
                os.makedirs(os.path.dirname(path), exist_ok=True)
                self._output_files.append(open(path, "a", encoding="utf-8"))
        
        for path in self.options.error_output_paths:
            if path == OutputPath.STDOUT:
                self._error_files.append(sys.stdout)
            elif path == OutputPath.STDERR:
                self._error_files.append(sys.stderr)
            else:
                os.makedirs(os.path.dirname(path), exist_ok=True)
                self._error_files.append(open(path, "a", encoding="utf-8"))
    
    def _get_caller_info(self) -> str:
        """Get caller file and line number"""
        stack = traceback.extract_stack()
        # Skip internal frames
        skip = 3 + self.options.caller_skip
        if len(stack) > skip:
            frame = stack[-(skip + 1)]
            # Get only the filename, not the full path
            filename = os.path.basename(frame.filename)
            return f"{filename}:{frame.lineno}"
        return "unknown:0"
    
    def _format_time(self) -> str:
        """Format current time"""
        now = datetime.now()
        return now.strftime(self.TIME_FORMAT)[:-3]  # Trim to milliseconds
    
    def _format_console(self, level: Level, msg: str, caller: str) -> str:
        """Format log message in console format matching glog"""
        time_str = f"[{self._format_time()}]"
        level_str = f"[{level.name.lower()}]"
        name_str = f"[{self.name}]" if self.name else "[]"
        
        parts = [time_str, level_str, name_str, caller]
        
        # Add fields in brackets - only show non-empty values
        if self.fields:
            for k, v in self.fields.items():
                # If value is empty string, just show the key in brackets
                if v == "":
                    parts.append(f"[{k}]")
                else:
                    parts.append(f"[{k}]")
        
        # Add message at the end
        parts.append(msg)
        
        return " ".join(parts)
    
    def _format_json(self, level: Level, msg: str, caller: str) -> str:
        """Format log message in JSON format"""
        log_dict = {
            "ts": self._format_time(),
            "level": level.name.lower(),
            "caller": caller,
            "msg": msg,
        }
        
        if self.name:
            log_dict["logger"] = self.name
        
        if self.fields:
            log_dict.update(self.fields)
        
        return json.dumps(log_dict, ensure_ascii=False)
    
    def _log(self, level: Level, msg: str):
        """Internal log method"""
        if not self.options.level.enabled(level):
            return
        
        caller = self._get_caller_info()
        
        if self.options.encoding == Encoding.JSON:
            formatted = self._format_json(level, msg, caller)
        else:
            formatted = self._format_console(level, msg, caller)
        
        with self._lock:
            # Write to appropriate outputs
            if level >= Level.ERROR:
                for f in self._error_files:
                    f.write(formatted + "\n")
                    f.flush()
            else:
                for f in self._output_files:
                    f.write(formatted + "\n")
                    f.flush()
    
    def with_field(self, key: str, value: Any) -> "Logger":
        """Add a field to logger"""
        new_fields = self.fields.copy()
        new_fields[key] = value
        return Logger(self.options, new_fields, self.name)
    
    def with_fields(self, fields: Dict[str, Any]) -> "Logger":
        """Add multiple fields to logger"""
        new_fields = self.fields.copy()
        new_fields.update(fields)
        return Logger(self.options, new_fields, self.name)
    
    def with_error(self, err: Optional[Exception]) -> "Logger":
        """Add error field to logger"""
        if err is None:
            return self
        return self.with_field("error", str(err))
    
    def named(self, name: str) -> "Logger":
        """Create named logger"""
        full_name = f"{self.name}.{name}" if self.name else name
        return Logger(self.options, self.fields.copy(), full_name)
    
    def debugf(self, format_str: str, *args):
        """Log debug message with formatting"""
        msg = format_str % args if args else format_str
        self._log(Level.DEBUG, msg)
    
    def infof(self, format_str: str, *args):
        """Log info message with formatting"""
        msg = format_str % args if args else format_str
        self._log(Level.INFO, msg)
    
    def warnf(self, format_str: str, *args):
        """Log warning message with formatting"""
        msg = format_str % args if args else format_str
        self._log(Level.WARN, msg)
    
    def warningf(self, format_str: str, *args):
        """Alias for warnf"""
        self.warnf(format_str, *args)
    
    def errorf(self, format_str: str, *args):
        """Log error message with formatting"""
        msg = format_str % args if args else format_str
        self._log(Level.ERROR, msg)
    
    def fatalf(self, format_str: str, *args):
        """Log fatal message and exit"""
        msg = format_str % args if args else format_str
        self._log(Level.FATAL, msg)
        sys.exit(1)
    
    def panicf(self, format_str: str, *args):
        """Log panic message and raise exception"""
        msg = format_str % args if args else format_str
        self._log(Level.PANIC, msg)
        raise RuntimeError(msg)
    
    def debug(self, *args):
        """Log debug message"""
        msg = " ".join(str(arg) for arg in args)
        self._log(Level.DEBUG, msg)
    
    def info(self, *args):
        """Log info message"""
        msg = " ".join(str(arg) for arg in args)
        self._log(Level.INFO, msg)
    
    def warn(self, *args):
        """Log warning message"""
        msg = " ".join(str(arg) for arg in args)
        self._log(Level.WARN, msg)
    
    def warning(self, *args):
        """Alias for warn"""
        self.warn(*args)
    
    def error(self, *args):
        """Log error message"""
        msg = " ".join(str(arg) for arg in args)
        self._log(Level.ERROR, msg)
    
    def fatal(self, *args):
        """Log fatal message and exit"""
        msg = " ".join(str(arg) for arg in args)
        self._log(Level.FATAL, msg)
        sys.exit(1)
    
    def panic(self, *args):
        """Log panic message and raise exception"""
        msg = " ".join(str(arg) for arg in args)
        self._log(Level.PANIC, msg)
        raise RuntimeError(msg)
    
    def __del__(self):
        """Cleanup file handles"""
        for f in self._output_files:
            if f not in (sys.stdout, sys.stderr):
                f.close()
        for f in self._error_files:
            if f not in (sys.stdout, sys.stderr):
                f.close()


# Global default logger
_default_logger: Optional[Logger] = None
_inner_logger: Optional[Logger] = None
_logger_lock = Lock()


def _init_default_loggers():
    """Initialize default loggers"""
    global _default_logger, _inner_logger
    
    options = Options(level=Level.INFO)
    options.with_stdout_output_path().with_stderr_error_output_path()
    
    _default_logger = Logger(options)
    
    inner_options = Options(level=Level.INFO, caller_skip=1)
    inner_options.with_stdout_output_path().with_stderr_error_output_path()
    _inner_logger = Logger(inner_options)


_init_default_loggers()


def default_logger() -> Logger:
    """Get default logger"""
    with _logger_lock:
        return _default_logger


def _get_inner_logger() -> Logger:
    """Get inner logger with caller skip"""
    with _logger_lock:
        return _inner_logger


def set_default_logger_config(options: Options):
    """Set default logger configuration"""
    global _default_logger, _inner_logger
    
    with _logger_lock:
        _default_logger = Logger(options)
        
        inner_options = Options(
            output_paths=options.output_paths.copy(),
            error_output_paths=options.error_output_paths.copy(),
            encoding=options.encoding,
            level=options.level,
            caller_skip=options.caller_skip + 1,
        )
        _inner_logger = Logger(inner_options)


# Package-level convenience functions
def error(msg: str):
    """Log error message"""
    _get_inner_logger().error(msg)


def errorf(format_str: str, *args):
    """Log error message with formatting"""
    _get_inner_logger().errorf(format_str, *args)


def warn(msg: str):
    """Log warning message"""
    _get_inner_logger().warn(msg)


def warnf(format_str: str, *args):
    """Log warning message with formatting"""
    _get_inner_logger().warnf(format_str, *args)


def info(msg: str):
    """Log info message"""
    _get_inner_logger().info(msg)


def infof(format_str: str, *args):
    """Log info message with formatting"""
    _get_inner_logger().infof(format_str, *args)


def debug(msg: str):
    """Log debug message"""
    _get_inner_logger().debug(msg)


def debugf(format_str: str, *args):
    """Log debug message with formatting"""
    _get_inner_logger().debugf(format_str, *args)


def with_field(key: str, value: Any) -> Logger:
    """Create logger with field"""
    return _get_inner_logger().with_field(key, value)


def with_error(err: Optional[Exception]) -> Logger:
    """Create logger with error"""
    return _get_inner_logger().with_error(err)
