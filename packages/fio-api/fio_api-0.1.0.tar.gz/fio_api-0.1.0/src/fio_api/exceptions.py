"""Exception hierarchy for :mod:`fio_api`."""

from __future__ import annotations

from typing import Any, Mapping


class FioApiError(Exception):
    """Base class for all package specific exceptions."""


class AuthenticationError(FioApiError):
    """Raised when the API rejects the provided token."""


class RateLimitError(FioApiError):
    """Raised when the API enforces its minimum polling interval."""


class ApiResponseError(FioApiError):
    """Raised when the HTTP API returns a non-success response."""

    def __init__(
        self,
        status_code: int,
        message: str,
        payload: Mapping[str, Any] | None = None,
        *,
        body: str | None = None,
    ) -> None:
        super().__init__(message)
        self.status_code = status_code
        self.payload = payload
        self.body = body

    def __str__(self) -> str:  # pragma: no cover - trivial string formatting
        parts = [super().__str__(), f"(status={self.status_code})"]
        if self.payload is not None:
            parts.append(f"payload={self.payload}")
        elif self.body:
            preview = self.body.strip()
            if len(preview) > 200:
                preview = f"{preview[:197]}..."
            parts.append(f"body={preview}")
        return " ".join(parts)


class ParsingError(FioApiError):
    """Raised when it is not possible to interpret the JSON payload."""


class TransportError(FioApiError):
    """Raised for unexpected transport-level errors."""
