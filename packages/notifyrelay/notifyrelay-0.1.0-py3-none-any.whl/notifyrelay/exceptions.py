"""
Custom exceptions for the NotifyRelay client.
"""


class NotifyRelayError(Exception):
    """Base exception for all NotifyRelay errors."""
    pass


class AuthenticationError(NotifyRelayError):
    """Raised when authentication fails."""
    pass


class ConnectionError(NotifyRelayError):
    """Raised when connection to the server fails."""
    pass
