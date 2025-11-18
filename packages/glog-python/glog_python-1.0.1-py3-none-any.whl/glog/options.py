"""Configuration options for logger"""

from typing import List
from .level import Level


class OutputPath:
    """Standard output paths"""
    STDOUT = "stdout"
    STDERR = "stderr"


class Encoding:
    """Log encoding formats"""
    CONSOLE = "console"
    JSON = "json"


class Options:
    """Logger configuration options"""
    
    def __init__(
        self,
        output_paths: List[str] = None,
        error_output_paths: List[str] = None,
        encoding: str = Encoding.CONSOLE,
        level: Level = Level.INFO,
        caller_skip: int = 0,
    ):
        self.output_paths = output_paths or []
        self.error_output_paths = error_output_paths or []
        self.encoding = encoding
        self.level = level
        self.caller_skip = caller_skip
    
    def with_stdout_output_path(self) -> "Options":
        """Add stdout to output paths"""
        if OutputPath.STDOUT not in self.output_paths:
            self.output_paths.append(OutputPath.STDOUT)
        return self
    
    def with_stderr_error_output_path(self) -> "Options":
        """Add stderr to error output paths"""
        if OutputPath.STDERR not in self.error_output_paths:
            self.error_output_paths.append(OutputPath.STDERR)
        return self
    
    def with_output_path(self, path: str) -> "Options":
        """Add custom output path"""
        if path not in self.output_paths:
            self.output_paths.append(path)
        return self
    
    def with_console_encoding(self) -> "Options":
        """Set console encoding"""
        self.encoding = Encoding.CONSOLE
        return self
    
    def with_json_encoding(self) -> "Options":
        """Set JSON encoding"""
        self.encoding = Encoding.JSON
        return self
    
    def with_level(self, level: Level) -> "Options":
        """Set log level"""
        self.level = level
        return self
    
    def with_caller_skip(self, skip: int) -> "Options":
        """Set caller skip frames"""
        self.caller_skip = skip
        return self
