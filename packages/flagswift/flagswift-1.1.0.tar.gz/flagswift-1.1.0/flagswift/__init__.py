"""
FlagSwift Python SDK
Official Python client for FlagSwift feature flags
"""

from .client import FlagSwift, FlagSwiftConfig
from .exceptions import FlagSwiftError, AuthenticationError, NetworkError

__version__ = "1.1.0"
__all__ = [
    "FlagSwift",
    "FlagSwiftConfig",
    "FlagSwiftError",
    "AuthenticationError",
    "NetworkError",
]