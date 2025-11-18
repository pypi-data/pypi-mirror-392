"\"\"\"Constants shared across the Samsung TV client package.\"\"\""
from __future__ import annotations

from typing import Mapping

JSONRPC_VERSION = "2.0"
DEFAULT_PORT = 1516
DEFAULT_HEADERS: Mapping[str, str] = {
    "Accept": "application/json",
    "Content-Type": "application/json",
}

__all__ = [
    "JSONRPC_VERSION",
    "DEFAULT_PORT",
    "DEFAULT_HEADERS",
]
