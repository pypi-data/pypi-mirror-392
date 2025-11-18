"""Simple usage example matching glog format exactly"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../.."))

import glog
from glog import Level, Options


# Setup logger
options = Options(level=Level.INFO)
options.with_console_encoding().with_stdout_output_path()
glog.set_default_logger_config(options)


def example1_basic():
    """Basic logging"""
    glog.info("Application started")
    glog.warn("High memory usage")
    glog.error("Connection failed")


def example2_with_trace():
    """Logging with trace ID"""
    logger = glog.default_logger().named("Runner")
    
    # Add trace_id as a field
    trace_id = "59d428f7843866bd2863561f23c0c657"
    log = logger.with_field(trace_id, "")
    
    log.info("🚀 Initializing Ollama model: gemma3:27b")
    log.info("📤 Sending prompt to model...")
    log.info("✅ Model response received (10 chars)")


def example3_multiple_fields():
    """Logging with multiple fields"""
    logger = glog.default_logger().named("Runner")
    
    trace_id = "59d428f7843866bd2863561f23c0c657"
    plugin_name = "Plugin langchain_ollama_python"
    
    log = logger.with_field(trace_id, "").with_field(plugin_name, "")
    
    log.info("🚀 Initializing Ollama model: gemma3:27b")
    log.info("📤 Sending prompt to model...")
    log.info("✅ Model response received (10 chars)")


def example4_context_logger():
    """Using context logger for cleaner code"""
    logger = glog.default_logger().named("API")
    glog.to_context(logger)
    
    # Add trace_id to context
    glog.add_trace_id("a1b2c3d4e5f6g7h8")
    
    # All subsequent logs will include the trace_id
    log = glog.extract_entry()
    log.info("Request received")
    
    # Add more fields
    glog.add_field("user_id", "123")
    glog.add_field("method", "POST")
    
    log = glog.extract_entry()
    log.info("Processing request")
    log.info("Request completed")


def example5_formatted():
    """Formatted logging"""
    logger = glog.default_logger().named("Worker")
    trace_id = "worker-123"
    
    log = logger.with_field(trace_id, "")
    
    log.infof("Processing %d items", 100)
    log.infof("Completed in %d ms", 1234)


if __name__ == "__main__":
    print("Example 1: Basic logging")
    print("-" * 50)
    example1_basic()
    
    print("\nExample 2: With trace ID")
    print("-" * 50)
    example2_with_trace()
    
    print("\nExample 3: Multiple fields")
    print("-" * 50)
    example3_multiple_fields()
    
    print("\nExample 4: Context logger")
    print("-" * 50)
    example4_context_logger()
    
    print("\nExample 5: Formatted logging")
    print("-" * 50)
    example5_formatted()
