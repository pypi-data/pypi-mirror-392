"""
NotifyRelay Python Client

A Python client for the NotifyRelay pub/sub messaging service.
Provides queue-based message retrieval with background polling.
"""

from .client import NotifyRelayClient
from .subscriber import Subscriber
from .exceptions import NotifyRelayError, AuthenticationError, ConnectionError

__version__ = "0.1.0"
__all__ = [
    "NotifyRelayClient",
    "Subscriber",
    "NotifyRelayError",
    "AuthenticationError",
    "ConnectionError",
]
