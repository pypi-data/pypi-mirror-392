"""Context logger examples for request tracing"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../.."))

import glog
from glog import Level, Options
import uuid


def simulate_request_handler():
    """Simulate handling a web request with context logging"""
    print("=== Request Handler with Context ===")
    
    # Initialize context with logger
    logger = glog.default_logger()
    ctx_logger = glog.to_context(logger)
    
    # Add trace ID for request tracking
    trace_id = str(uuid.uuid4())[:8]
    glog.add_trace_id(trace_id)
    
    # Add request metadata
    glog.add_pathname("/api/users/123")
    glog.add_user_id(123)
    
    # Log with context - all fields are automatically included
    log = glog.extract_entry()
    log.info("Request started")
    
    # Add more fields during processing
    glog.add_field("method", "GET")
    glog.add_field("status", 200)
    
    log = glog.extract_entry()
    log.info("Processing request")
    
    # Simulate some work
    glog.add_field("duration_ms", 45)
    
    log = glog.extract_entry()
    log.info("Request completed")
    
    print()


def simulate_nested_operations():
    """Simulate nested operations with context"""
    print("=== Nested Operations ===")
    
    # Setup context
    logger = glog.default_logger()
    glog.to_context(logger)
    
    trace_id = str(uuid.uuid4())[:8]
    glog.add_trace_id(trace_id)
    
    # Parent operation
    glog.add_field("operation", "user_registration")
    log = glog.extract_entry()
    log.info("Starting user registration")
    
    # Nested operation 1: validate
    glog.add_field("step", "validation")
    log = glog.extract_entry()
    log.info("Validating user data")
    
    # Nested operation 2: save
    glog.add_field("step", "save")
    glog.add_field("db_query_ms", 23)
    log = glog.extract_entry()
    log.info("Saving user to database")
    
    # Nested operation 3: send email
    glog.add_field("step", "notification")
    glog.add_field("email", "user@example.com")
    log = glog.extract_entry()
    log.info("Sending welcome email")
    
    # Complete
    glog.add_fields({
        "step": "complete",
        "total_duration_ms": 156
    })
    log = glog.extract_entry()
    log.info("User registration completed")
    
    print()


def simulate_error_handling():
    """Simulate error handling with context"""
    print("=== Error Handling with Context ===")
    
    logger = glog.default_logger()
    glog.to_context(logger)
    
    trace_id = str(uuid.uuid4())[:8]
    glog.add_trace_id(trace_id)
    glog.add_pathname("/api/orders")
    glog.add_user_id(456)
    
    log = glog.extract_entry()
    log.info("Processing order")
    
    try:
        # Simulate error
        raise ValueError("Invalid payment method")
    except Exception as e:
        glog.add_field("error_type", type(e).__name__)
        log = glog.extract_entry().with_error(e)
        log.error("Order processing failed")
    
    print()


def extract_context_values():
    """Extract values from context"""
    print("=== Extract Context Values ===")
    
    logger = glog.default_logger()
    glog.to_context(logger)
    
    # Set values
    glog.add_trace_id("trace-abc123")
    glog.add_user_id(789)
    glog.add_pathname("/api/profile")
    
    # Extract values
    trace_id = glog.extract_trace_id()
    user_id = glog.extract_user_id()
    pathname = glog.extract_pathname()
    
    print(f"Trace ID: {trace_id}")
    print(f"User ID: {user_id}")
    print(f"Pathname: {pathname}")
    
    log = glog.extract_entry()
    log.info("Context values extracted")
    
    print()


if __name__ == "__main__":
    # Configure logger
    options = Options(level=Level.INFO)
    options.with_console_encoding().with_stdout_output_path()
    glog.set_default_logger_config(options)
    
    simulate_request_handler()
    simulate_nested_operations()
    simulate_error_handling()
    extract_context_values()
