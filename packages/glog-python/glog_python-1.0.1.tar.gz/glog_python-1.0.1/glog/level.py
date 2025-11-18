"""Log levels compatible with glog"""

from enum import IntEnum


class Level(IntEnum):
    """Logging priority levels"""
    
    DEBUG = -1
    INFO = 0
    WARN = 1
    ERROR = 2
    DPANIC = 3
    PANIC = 4
    FATAL = 5
    
    def __str__(self):
        """Returns lowercase ASCII representation"""
        return self.name.lower()
    
    def capital_string(self):
        """Returns uppercase ASCII representation"""
        return self.name.upper()
    
    @classmethod
    def from_string(cls, text: str) -> "Level":
        """Parse level from string"""
        text_upper = text.upper()
        if text_upper in ("DEBUG", ""):
            return cls.DEBUG
        elif text_upper == "INFO":
            return cls.INFO
        elif text_upper == "WARN":
            return cls.WARN
        elif text_upper == "ERROR":
            return cls.ERROR
        elif text_upper == "DPANIC":
            return cls.DPANIC
        elif text_upper == "PANIC":
            return cls.PANIC
        elif text_upper == "FATAL":
            return cls.FATAL
        else:
            raise ValueError(f"Unrecognized level: {text}")
    
    def enabled(self, lvl: "Level") -> bool:
        """Check if given level is at or above this level"""
        return lvl >= self
