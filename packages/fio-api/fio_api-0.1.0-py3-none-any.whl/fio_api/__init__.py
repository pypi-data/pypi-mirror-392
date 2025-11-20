"""Top level package for the Fio banking API client."""

from __future__ import annotations

from importlib import metadata

from .client import FioClient
from .exceptions import (
    ApiResponseError,
    AuthenticationError,
    FioApiError,
    ParsingError,
    RateLimitError,
    TransportError,
)
from .models import AccountInfo, Statement, Transaction

__all__ = [
    "AccountInfo",
    "ApiResponseError",
    "AuthenticationError",
    "FioApiError",
    "FioClient",
    "ParsingError",
    "RateLimitError",
    "Statement",
    "Transaction",
    "TransportError",
]


def __getattr__(name: str) -> str:
    if name == "__version__":
        return metadata.version("fio-api")
    raise AttributeError(name)
