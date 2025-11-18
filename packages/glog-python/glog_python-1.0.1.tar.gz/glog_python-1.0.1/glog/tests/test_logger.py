"""Unit tests for logger"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../.."))

import unittest
from io import StringIO
from glog import Logger, Level, Options, OutputPath


class TestLogger(unittest.TestCase):
    """Test Logger class"""
    
    def setUp(self):
        """Setup test fixtures"""
        self.options = Options(level=Level.DEBUG)
        self.options.with_stdout_output_path()
    
    def test_basic_logging(self):
        """Test basic logging methods"""
        logger = Logger(self.options)
        
        # Should not raise
        logger.debug("debug message")
        logger.info("info message")
        logger.warn("warn message")
        logger.error("error message")
    
    def test_formatted_logging(self):
        """Test formatted logging"""
        logger = Logger(self.options)
        
        logger.infof("User %s logged in", "Alice")
        logger.debugf("Processing %d items", 42)
        logger.warnf("Value: %s, Count: %d", "test", 10)
    
    def test_with_field(self):
        """Test adding single field"""
        logger = Logger(self.options)
        
        new_logger = logger.with_field("request_id", "req-123")
        self.assertIn("request_id", new_logger.fields)
        self.assertEqual(new_logger.fields["request_id"], "req-123")
        
        # Original logger should not be modified
        self.assertNotIn("request_id", logger.fields)
    
    def test_with_fields(self):
        """Test adding multiple fields"""
        logger = Logger(self.options)
        
        fields = {
            "user_id": 123,
            "method": "POST",
            "path": "/api/users"
        }
        
        new_logger = logger.with_fields(fields)
        self.assertEqual(len(new_logger.fields), 3)
        self.assertEqual(new_logger.fields["user_id"], 123)
        self.assertEqual(new_logger.fields["method"], "POST")
    
    def test_with_error(self):
        """Test adding error field"""
        logger = Logger(self.options)
        
        error = ValueError("test error")
        new_logger = logger.with_error(error)
        
        self.assertIn("error", new_logger.fields)
        self.assertEqual(new_logger.fields["error"], "test error")
    
    def test_with_error_none(self):
        """Test with_error with None"""
        logger = Logger(self.options)
        
        new_logger = logger.with_error(None)
        self.assertNotIn("error", new_logger.fields)
    
    def test_named_logger(self):
        """Test named logger"""
        logger = Logger(self.options)
        
        named = logger.named("api")
        self.assertEqual(named.name, "api")
        
        nested = named.named("users")
        self.assertEqual(nested.name, "api.users")
    
    def test_log_levels(self):
        """Test log level filtering"""
        # Set level to WARN
        options = Options(level=Level.WARN)
        options.with_stdout_output_path()
        logger = Logger(options)
        
        # These should be filtered out (no exception)
        logger.debug("debug")
        logger.info("info")
        
        # These should be logged
        logger.warn("warn")
        logger.error("error")
    
    def test_json_encoding(self):
        """Test JSON encoding"""
        options = Options(level=Level.INFO)
        options.with_json_encoding().with_stdout_output_path()
        
        logger = Logger(options)
        logger.info("test message")
        
        # Should not raise
        logger.with_field("key", "value").info("with field")


class TestLevel(unittest.TestCase):
    """Test Level enum"""
    
    def test_level_values(self):
        """Test level values"""
        self.assertEqual(Level.DEBUG, -1)
        self.assertEqual(Level.INFO, 0)
        self.assertEqual(Level.WARN, 1)
        self.assertEqual(Level.ERROR, 2)
    
    def test_level_string(self):
        """Test level string representation"""
        self.assertEqual(str(Level.DEBUG), "debug")
        self.assertEqual(str(Level.INFO), "info")
        self.assertEqual(str(Level.WARN), "warn")
        self.assertEqual(str(Level.ERROR), "error")
    
    def test_level_capital_string(self):
        """Test level capital string"""
        self.assertEqual(Level.DEBUG.capital_string(), "DEBUG")
        self.assertEqual(Level.INFO.capital_string(), "INFO")
    
    def test_level_from_string(self):
        """Test parsing level from string"""
        self.assertEqual(Level.from_string("debug"), Level.DEBUG)
        self.assertEqual(Level.from_string("INFO"), Level.INFO)
        self.assertEqual(Level.from_string("warn"), Level.WARN)
    
    def test_level_enabled(self):
        """Test level enabled check"""
        self.assertTrue(Level.INFO.enabled(Level.INFO))
        self.assertTrue(Level.INFO.enabled(Level.WARN))
        self.assertTrue(Level.INFO.enabled(Level.ERROR))
        self.assertFalse(Level.INFO.enabled(Level.DEBUG))


class TestOptions(unittest.TestCase):
    """Test Options class"""
    
    def test_default_options(self):
        """Test default options"""
        options = Options()
        self.assertEqual(options.output_paths, [])
        self.assertEqual(options.level, Level.INFO)
    
    def test_with_methods(self):
        """Test with methods"""
        options = Options()
        
        options.with_stdout_output_path()
        self.assertIn(OutputPath.STDOUT, options.output_paths)
        
        options.with_stderr_error_output_path()
        self.assertIn(OutputPath.STDERR, options.error_output_paths)
        
        options.with_level(Level.DEBUG)
        self.assertEqual(options.level, Level.DEBUG)


if __name__ == "__main__":
    unittest.main()
