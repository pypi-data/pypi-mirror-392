"""Custom exceptions for the Samsung TV client."""
from __future__ import annotations


class SamsungTVError(Exception):
    """Base error for the Samsung TV client."""


class SamsungTVAuthenticationError(SamsungTVError):
    """Raised when an access token is missing or rejected."""


class SamsungTVProtocolError(SamsungTVError):
    """Raised when the JSON-RPC response is invalid."""


class SamsungTVResponseError(SamsungTVError):
    """Raised when the server returns a JSON-RPC error payload."""


__all__ = [
    "SamsungTVError",
    "SamsungTVAuthenticationError",
    "SamsungTVProtocolError",
    "SamsungTVResponseError",
]
