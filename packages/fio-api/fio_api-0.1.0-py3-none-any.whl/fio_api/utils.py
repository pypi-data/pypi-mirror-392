"""Utilities shared across :mod:`fio_api`."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from decimal import Decimal, InvalidOperation
from typing import Any

from .exceptions import ParsingError

_EPOCH = datetime(1970, 1, 1, tzinfo=timezone.utc)


def parse_datetime(value: Any) -> datetime | None:
    """Return a timezone-aware datetime from the API payload."""

    if value is None:
        return None

    if isinstance(value, (int, float)):
        milliseconds = int(value)
        return _EPOCH + timedelta(milliseconds=milliseconds)

    text = str(value).strip()
    if not text:
        return None

    normalized = text.replace("+GMT", "")
    normalized = normalized.rstrip("Z")
    for fmt in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%d"):
        try:
            naive = datetime.strptime(normalized, fmt)
            return naive.replace(tzinfo=timezone.utc)
        except ValueError:
            continue

    try:
        parsed = datetime.fromisoformat(normalized)
    except ValueError as exc:
        raise ParsingError(f"Cannot parse datetime value: {text}") from exc

    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    else:
        parsed = parsed.astimezone(timezone.utc)
    return parsed


def parse_decimal(value: Any) -> Decimal | None:
    """Return a :class:`~decimal.Decimal` representation of *value*."""

    if value is None:
        return None

    if isinstance(value, Decimal):
        return value

    text = str(value).strip()
    if not text:
        return None

    try:
        return Decimal(text)
    except InvalidOperation as exc:
        raise ParsingError(f"Cannot parse decimal value: {value}") from exc


def parse_int(value: Any) -> int | None:
    """Return an integer if the value looks like one."""

    if value is None:
        return None

    if isinstance(value, int):
        return value

    text = str(value).strip()
    if not text:
        return None

    try:
        return int(text)
    except ValueError as exc:
        raise ParsingError(f"Cannot parse integer value: {value}") from exc


def parse_string(value: Any) -> str | None:
    """Return a trimmed string or :data:`None`."""

    if value is None:
        return None
    text = str(value).strip()
    return text or None
