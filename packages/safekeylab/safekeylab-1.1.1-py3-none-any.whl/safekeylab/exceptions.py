"""
SafeKeyLab Exceptions
"""


class SafeKeyLabException(Exception):
    """Base exception for SafeKeyLab SDK"""
    pass


class APIError(SafeKeyLabException):
    """API-related errors"""
    pass


class ValidationError(SafeKeyLabException):
    """Validation errors"""
    pass


class AuthenticationError(SafeKeyLabException):
    """Authentication errors"""
    pass


class RateLimitError(SafeKeyLabException):
    """Rate limit errors"""
    pass


class ConfigurationError(SafeKeyLabException):
    """Configuration errors"""
    pass