"""HTTP client for interacting with the public Fio banking API."""

from __future__ import annotations

from datetime import date
from decimal import Decimal
from typing import Any, Mapping

import httpx

from .exceptions import (
    ApiResponseError,
    AuthenticationError,
    RateLimitError,
    TransportError,
)
from .models import AccountInfo, Statement, Transaction

DEFAULT_BASE_URL = "https://fioapi.fio.cz/v1/rest"
_TRANSACTIONS_SUFFIX = "transactions.json"


class FioClient:
    """Small HTTP client for the Fio REST API."""

    def __init__(
        self,
        api_key: str,
        *,
        base_url: str = DEFAULT_BASE_URL,
        timeout: float = 10.0,
        transport: httpx.BaseTransport | None = None,
        client: httpx.Client | None = None,
    ) -> None:
        if not api_key:
            raise ValueError("An API token must be provided")

        self._api_key = api_key
        self._base_url = base_url.rstrip("/")

        if client is None:
            self._client = httpx.Client(
                base_url=self._base_url,
                timeout=timeout,
                headers={"Accept": "application/json"},
                transport=transport,
            )
            self._owns_client = True
        else:
            self._client = client
            self._owns_client = False

    def close(self) -> None:
        """Close the underlying :class:`httpx.Client`."""

        if self._owns_client:
            self._client.close()

    def __enter__(self) -> "FioClient":  # noqa: D105 - context manager boilerplate
        return self

    def __exit__(self, *_: Any) -> None:  # noqa: D105
        self.close()

    def get_account_info(self) -> AccountInfo:
        """Return metadata for the account associated with the token."""

        return self.fetch_last_statement().info

    def get_balance(self) -> Decimal:
        """Return the latest closing balance for the account."""

        return self.fetch_last_statement().info.closing_balance

    def list_transactions(self, start_date: date, end_date: date) -> tuple[Transaction, ...]:
        """Return transactions within the provided inclusive date range."""

        return self.fetch_transactions(start_date, end_date).transactions

    def fetch_transactions(self, start_date: date, end_date: date) -> Statement:
        """Fetch a statement bounded by *start_date* and *end_date*."""

        if start_date > end_date:
            raise ValueError("start_date must be before or equal to end_date")

        path = (
            f"periods/{self._api_key}/{start_date.isoformat()}/{end_date.isoformat()}/"
            f"{_TRANSACTIONS_SUFFIX}"
        )
        return self._fetch_statement(path)

    def download_statement(self, year: int, statement_id: int) -> Statement:
        """Download a numbered statement from a specific *year*."""

        if year < 2000:
            raise ValueError("year must be four digits")
        if statement_id <= 0:
            raise ValueError("statement_id must be a positive integer")

        path = f"by-id/{self._api_key}/{year}/{statement_id}/{_TRANSACTIONS_SUFFIX}"
        return self._fetch_statement(path)

    def fetch_last_statement(self) -> Statement:
        """Fetch movements since the last checkpoint configured by the bank."""

        path = f"last/{self._api_key}/{_TRANSACTIONS_SUFFIX}"
        return self._fetch_statement(path)

    def set_last_transaction_id(self, transaction_id: int) -> None:
        """Update the server-side cursor to a previously downloaded transaction."""

        if transaction_id <= 0:
            raise ValueError("transaction_id must be positive")
        path = f"set-last-id/{self._api_key}/{transaction_id}/"
        self._request(path)

    def set_last_transaction_date(self, last_successful_date: date) -> None:
        """Update the server-side cursor to a date."""

        path = f"set-last-date/{self._api_key}/{last_successful_date.isoformat()}/"
        self._request(path)

    def _fetch_statement(self, path: str) -> Statement:
        payload = self._request_json(path)
        return Statement.from_api(payload)

    def _request(self, path: str) -> httpx.Response:
        try:
            response = self._client.get(path)
        except httpx.TransportError as exc:  # pragma: no cover - defensive branch
            raise TransportError("Failed to communicate with Fio API") from exc

        if response.status_code == httpx.codes.UNAUTHORIZED:
            raise AuthenticationError("The supplied token was rejected")
        if response.status_code == httpx.codes.TOO_MANY_REQUESTS:
            raise RateLimitError("Fio API rate limit reached")
        if response.is_error:
            payload: Mapping[str, Any] | None = None
            try:
                payload = response.json()
            except ValueError:
                payload = None
            raise ApiResponseError(
                response.status_code,
                "Unexpected API response",
                payload,
                body=response.text,
            )

        return response

    def _request_json(self, path: str) -> Mapping[str, Any]:
        response = self._request(path)
        if not response.content:
            raise ApiResponseError(response.status_code, "Empty response body", body=response.text)
        try:
            return response.json()
        except ValueError as exc:
            raise ApiResponseError(
                response.status_code,
                "Response is not valid JSON",
                body=response.text,
            ) from exc
