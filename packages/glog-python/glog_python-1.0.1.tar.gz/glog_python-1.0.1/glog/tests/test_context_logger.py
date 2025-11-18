"""Unit tests for context logger"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../.."))

import unittest
from glog import Logger, Level, Options
from glog.context_logger import (
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


class TestContextLogger(unittest.TestCase):
    """Test context logger functionality"""
    
    def setUp(self):
        """Setup test fixtures"""
        options = Options(level=Level.INFO)
        options.with_stdout_output_path()
        self.logger = Logger(options)
    
    def test_to_context(self):
        """Test adding logger to context"""
        ctx_logger = to_context(self.logger)
        self.assertIsNotNone(ctx_logger)
        self.assertEqual(ctx_logger.logger, self.logger)
    
    def test_add_field(self):
        """Test adding single field"""
        to_context(self.logger)
        
        add_field("key1", "value1")
        
        logger = extract_entry()
        self.assertIn("key1", logger.fields)
        self.assertEqual(logger.fields["key1"], "value1")
    
    def test_add_fields(self):
        """Test adding multiple fields"""
        to_context(self.logger)
        
        fields = {
            "key1": "value1",
            "key2": 123,
            "key3": True
        }
        add_fields(fields)
        
        logger = extract_entry()
        self.assertIn("key1", logger.fields)
        self.assertIn("key2", logger.fields)
        self.assertIn("key3", logger.fields)
    
    def test_add_top_field(self):
        """Test adding top-level field"""
        to_context(self.logger)
        
        add_top_field("trace_id", "trace-123")
        
        logger = extract_entry()
        self.assertIn("trace_id", logger.fields)
    
    def test_trace_id(self):
        """Test trace ID operations"""
        to_context(self.logger)
        
        trace_id = "trace-abc-123"
        add_trace_id(trace_id)
        
        extracted = extract_trace_id()
        self.assertEqual(extracted, trace_id)
    
    def test_user_id(self):
        """Test user ID operations"""
        to_context(self.logger)
        
        user_id = 12345
        add_user_id(user_id)
        
        extracted = extract_user_id()
        self.assertEqual(extracted, user_id)
    
    def test_pathname(self):
        """Test pathname operations"""
        to_context(self.logger)
        
        pathname = "/api/users/123"
        add_pathname(pathname)
        
        extracted = extract_pathname()
        self.assertEqual(extracted, pathname)
    
    def test_extract_entry_with_fields(self):
        """Test extracting logger with accumulated fields"""
        to_context(self.logger)
        
        add_trace_id("trace-123")
        add_user_id(456)
        add_pathname("/api/test")
        add_field("method", "GET")
        add_field("status", 200)
        
        logger = extract_entry()
        
        # Check all fields are present
        self.assertIn("trace_id", logger.fields)
        self.assertIn("user_id", logger.fields)
        self.assertIn("pathname", logger.fields)
        self.assertIn("method", logger.fields)
        self.assertIn("status", logger.fields)
    
    def test_extract_without_context(self):
        """Test extracting when no context is set"""
        # Don't call to_context
        
        # Should return default logger without error
        logger = extract_entry()
        self.assertIsNotNone(logger)
    
    def test_extract_trace_id_without_context(self):
        """Test extracting trace ID without context"""
        # Don't call to_context
        
        trace_id = extract_trace_id()
        self.assertEqual(trace_id, "")
    
    def test_extract_user_id_without_context(self):
        """Test extracting user ID without context"""
        # Don't call to_context
        
        user_id = extract_user_id()
        self.assertEqual(user_id, 0)


if __name__ == "__main__":
    unittest.main()
