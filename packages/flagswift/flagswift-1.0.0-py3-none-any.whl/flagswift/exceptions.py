"""
FlagSwift Exceptions
"""


class FlagSwiftError(Exception):
    """Base exception for FlagSwift SDK"""
    pass


class AuthenticationError(FlagSwiftError):
    """Raised when API key is invalid or unauthorized"""
    pass


class NetworkError(FlagSwiftError):
    """Raised when network requests fail"""
    pass