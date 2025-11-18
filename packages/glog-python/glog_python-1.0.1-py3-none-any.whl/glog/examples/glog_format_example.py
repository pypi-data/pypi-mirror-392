"""Example matching the exact glog format"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../.."))

import glog
from glog import Level, Options


def setup_logger():
    """Setup logger with console format"""
    options = Options(level=Level.INFO)
    options.with_console_encoding().with_stdout_output_path()
    glog.set_default_logger_config(options)


def example_plugin_logs():
    """Example logs matching the plugin format"""
    print("=== Plugin-style Logs ===\n")
    
    # Create a named logger for Runner
    logger = glog.default_logger().named("Runner")
    
    # Add trace_id and plugin name as fields
    trace_id = "59d428f7843866bd2863561f23c0c657"
    plugin_name = "Plugin langchain_ollama_python"
    
    logger_with_context = logger.with_field(trace_id, "").with_field(plugin_name, "")
    
    # Log messages
    logger_with_context.info("🚀 Initializing Ollama model: gemma3:27b")
    logger_with_context.info("📤 Sending prompt to model...")
    logger_with_context.info("✅ Model response received (10 chars)")
    
    print()


def example_with_context_logger():
    """Example using context logger for cleaner API"""
    print("=== Using Context Logger ===\n")
    
    # Setup context
    logger = glog.default_logger().named("Runner")
    glog.to_context(logger)
    
    # Add trace_id
    trace_id = "59d428f7843866bd2863561f23c0c657"
    glog.add_trace_id(trace_id)
    
    # Add plugin name
    glog.add_field("Plugin langchain_ollama_python", "")
    
    # Extract and log
    log = glog.extract_entry()
    log.info("🚀 Initializing Ollama model: gemma3:27b")
    log.info("📤 Sending prompt to model...")
    log.info("✅ Model response received (10 chars)")
    
    print()


def example_request_tracing():
    """Example of request tracing with multiple fields"""
    print("=== Request Tracing ===\n")
    
    logger = glog.default_logger().named("API")
    
    # Simulate a request with trace_id and other metadata
    trace_id = "a1b2c3d4e5f6g7h8"
    request_id = "req-12345"
    user_id = "user-789"
    
    log = logger.with_field(trace_id, "").with_field(request_id, "").with_field(user_id, "")
    
    log.info("Request received")
    log.info("Validating request parameters")
    log.info("Processing request")
    log.info("Request completed successfully")
    
    print()


def example_different_levels():
    """Example with different log levels"""
    print("=== Different Log Levels ===\n")
    
    logger = glog.default_logger().named("Service")
    trace_id = "trace-xyz-123"
    
    log = logger.with_field(trace_id, "")
    
    log.debug("Debug: Detailed information for debugging")
    log.info("Info: Service started successfully")
    log.warn("Warn: High memory usage detected")
    log.error("Error: Failed to connect to database")
    
    print()


def example_with_error():
    """Example with error logging"""
    print("=== Error Logging ===\n")
    
    logger = glog.default_logger().named("Database")
    trace_id = "error-trace-456"
    
    try:
        # Simulate an error
        result = 1 / 0
    except Exception as e:
        log = logger.with_field(trace_id, "").with_error(e)
        log.error("Database operation failed")
    
    print()


def example_formatted_logging():
    """Example with formatted messages"""
    print("=== Formatted Logging ===\n")
    
    logger = glog.default_logger().named("Worker")
    trace_id = "worker-trace-789"
    
    log = logger.with_field(trace_id, "")
    
    model_name = "gemma3:27b"
    log.infof("🚀 Initializing Ollama model: %s", model_name)
    
    char_count = 10
    log.infof("✅ Model response received (%d chars)", char_count)
    
    duration_ms = 1093
    log.infof("⏱️  Request completed in %d ms", duration_ms)
    
    print()


if __name__ == "__main__":
    setup_logger()
    
    example_plugin_logs()
    example_with_context_logger()
    example_request_tracing()
    example_different_levels()
    example_with_error()
    example_formatted_logging()
