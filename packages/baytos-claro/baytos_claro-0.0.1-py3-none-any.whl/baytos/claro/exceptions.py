"""
Custom exceptions for the Bayt SDK
"""


class BaytAPIError(Exception):
    """Base exception for Bayt API errors"""

    pass


class BaytAuthError(BaytAPIError):
    """Exception raised for authentication errors"""

    pass


class BaytNotFoundError(BaytAPIError):
    """Exception raised when a resource is not found"""

    pass


class BaytRateLimitError(BaytAPIError):
    """Exception raised when rate limit is exceeded"""

    pass


class BaytValidationError(BaytAPIError):
    """Exception raised for validation errors"""

    pass
