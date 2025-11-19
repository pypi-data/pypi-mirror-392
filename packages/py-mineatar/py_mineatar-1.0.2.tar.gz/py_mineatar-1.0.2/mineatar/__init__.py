# mineatar/__init__.py

from .client import MineatarClient, AsyncMineatarClient
from .exceptions import InvalidUUIDError, APIError, RateLimitError

__all__ = [
    "MineatarClient",
    "AsyncMineatarClient",
    "InvalidUUIDError",
    "APIError",
    "RateLimitError",
]

__version__ = "1.0.2"
