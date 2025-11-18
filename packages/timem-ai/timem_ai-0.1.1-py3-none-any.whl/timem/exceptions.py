"""
TiMEM SDK Exceptions

Custom exception classes for the TiMEM SDK.
"""


class TiMEMError(Exception):
    """Base exception for TiMEM SDK."""
    pass


class AuthenticationError(TiMEMError):
    """Raised when authentication fails."""
    pass


class APIError(TiMEMError):
    """Raised when API returns an error."""
    
    def __init__(self, message: str, status_code: int = None):
        super().__init__(message)
        self.status_code = status_code


class ValidationError(TiMEMError):
    """Raised when request validation fails."""
    pass


class ConnectionError(TiMEMError):
    """Raised when connection to TiMEM server fails."""
    pass


class TimeoutError(TiMEMError):
    """Raised when request times out."""
    pass


class CircuitBreakerError(TiMEMError):
    """Raised when circuit breaker is open."""
    pass


class RateLimitError(TiMEMError):
    """Raised when rate limit is exceeded."""
    pass