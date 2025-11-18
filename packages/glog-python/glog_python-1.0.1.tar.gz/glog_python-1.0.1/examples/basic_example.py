"""Basic usage examples for glog-python

Install: pip install glog-python
GitHub: https://github.com/gw123/glog-python
"""

import glog
from glog import Level, Options


def basic_logging():
    """Basic logging examples"""
    print("=== Basic Logging ===")
    
    glog.debug("This is a debug message")
    glog.info("This is an info message")
    glog.warn("This is a warning message")
    glog.error("This is an error message")
    
    print()


def formatted_logging():
    """Formatted logging examples"""
    print("=== Formatted Logging ===")
    
    user = "Alice"
    count = 42
    
    glog.infof("User %s logged in", user)
    glog.debugf("Processing %d items", count)
    glog.warnf("User %s has %d pending tasks", user, count)
    
    print()


def with_fields():
    """Logging with fields"""
    print("=== Logging with Fields ===")
    
    logger = glog.with_field("request_id", "req-123")
    logger.info("Processing request")
    
    logger = logger.with_field("user_id", 456)
    logger.info("User authenticated")
    
    logger = logger.with_fields({
        "method": "POST",
        "path": "/api/users",
        "status": 200
    })
    logger.info("Request completed")
    
    print()


def with_error():
    """Logging with error"""
    print("=== Logging with Error ===")
    
    try:
        result = 1 / 0
    except Exception as e:
        glog.with_error(e).error("Division failed")
    
    print()


def custom_logger():
    """Custom logger configuration"""
    print("=== Custom Logger ===")
    
    options = Options(level=Level.DEBUG)
    options.with_stdout_output_path()
    
    glog.set_default_logger_config(options)
    
    glog.debug("Debug is now enabled")
    glog.info("Custom logger configured")
    
    print()


def json_logging():
    """JSON format logging"""
    print("=== JSON Logging ===")
    
    options = Options(level=Level.INFO)
    options.with_json_encoding().with_stdout_output_path()
    
    glog.set_default_logger_config(options)
    
    glog.info("This is JSON formatted")
    glog.with_field("user", "Bob").with_field("action", "login").info("User action")
    
    print()


def named_logger():
    """Named logger example"""
    print("=== Named Logger ===")
    
    # Reset to console
    options = Options(level=Level.INFO)
    options.with_console_encoding().with_stdout_output_path()
    glog.set_default_logger_config(options)
    
    logger = glog.default_logger().named("api").named("users")
    logger.info("User service started")
    logger.warn("High memory usage detected")
    
    print()


if __name__ == "__main__":
    basic_logging()
    formatted_logging()
    with_fields()
    with_error()
    custom_logger()
    json_logging()
    named_logger()
