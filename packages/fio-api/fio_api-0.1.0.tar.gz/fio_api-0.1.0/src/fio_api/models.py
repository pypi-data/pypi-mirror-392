"""Typed models for the Fio banking API."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from typing import Any, Mapping

from .exceptions import ParsingError
from .utils import parse_datetime, parse_decimal, parse_int, parse_string


@dataclass(frozen=True)
class AccountInfo:
    """Metadata about an account returned together with statements."""

    account_id: str
    bank_id: str
    currency: str
    iban: str
    bic: str
    opening_balance: Decimal
    closing_balance: Decimal
    date_start: datetime
    date_end: datetime
    year: int | None
    statement_number: int | None
    id_from: int | None
    id_to: int | None
    id_last_download: int | None

    @classmethod
    def from_api(cls, payload: Mapping[str, Any]) -> "AccountInfo":
        try:
            account_id = str(payload["accountId"])
            bank_id = str(payload["bankId"])
            currency = str(payload["currency"])
            iban = str(payload["iban"])
            bic = str(payload["bic"])
        except KeyError as exc:
            raise ParsingError("Account info payload is incomplete") from exc

        opening_balance = parse_decimal(payload.get("openingBalance"))
        closing_balance = parse_decimal(payload.get("closingBalance"))
        date_start = parse_datetime(payload.get("dateStart"))
        date_end = parse_datetime(payload.get("dateEnd"))

        if opening_balance is None or closing_balance is None:
            raise ParsingError("Missing opening/closing balance in account info")
        if date_start is None or date_end is None:
            raise ParsingError("Missing date range in account info")

        return cls(
            account_id=account_id,
            bank_id=bank_id,
            currency=currency,
            iban=iban,
            bic=bic,
            opening_balance=opening_balance,
            closing_balance=closing_balance,
            date_start=date_start,
            date_end=date_end,
            year=parse_int(payload.get("yearList")),
            statement_number=parse_int(payload.get("idList")),
            id_from=parse_int(payload.get("idFrom")),
            id_to=parse_int(payload.get("idTo")),
            id_last_download=parse_int(payload.get("idLastDownload")),
        )


@dataclass(frozen=True)
class Transaction:
    """Single transaction belonging to a statement."""

    transaction_id: int
    date: datetime
    amount: Decimal
    currency: str
    counter_account: str | None
    counter_account_name: str | None
    bank_code: str | None
    bank_name: str | None
    constant_symbol: str | None
    variable_symbol: str | None
    specific_symbol: str | None
    user_identification: str | None
    recipient_message: str | None
    transaction_type: str | None
    executor: str | None
    specification: str | None
    comment: str | None
    bic: str | None
    instruction_id: int | None
    payer_reference: str | None

    @classmethod
    def from_api(cls, payload: Mapping[str, Any]) -> "Transaction":
        def column_value(column_name: str) -> Any:
            column = payload.get(column_name)
            if isinstance(column, Mapping):
                return column.get("value")
            return None

        transaction_id = parse_int(column_value("column22"))
        date = parse_datetime(column_value("column0"))
        amount = parse_decimal(column_value("column1"))
        currency = parse_string(column_value("column14"))

        if (
            transaction_id is None
            or date is None
            or amount is None
            or currency is None
        ):
            raise ParsingError("Transaction payload is missing mandatory columns")

        return cls(
            transaction_id=transaction_id,
            date=date,
            amount=amount,
            currency=currency,
            counter_account=parse_string(column_value("column2")),
            counter_account_name=parse_string(column_value("column10")),
            bank_code=parse_string(column_value("column3")),
            bank_name=parse_string(column_value("column12")),
            constant_symbol=parse_string(column_value("column4")),
            variable_symbol=parse_string(column_value("column5")),
            specific_symbol=parse_string(column_value("column6")),
            user_identification=parse_string(column_value("column7")),
            recipient_message=parse_string(column_value("column16")),
            transaction_type=parse_string(column_value("column8")),
            executor=parse_string(column_value("column9")),
            specification=parse_string(column_value("column18")),
            comment=parse_string(column_value("column25")),
            bic=parse_string(column_value("column26")),
            instruction_id=parse_int(column_value("column17")),
            payer_reference=parse_string(column_value("column27")),
        )


@dataclass(frozen=True)
class Statement:
    """A tuple of account metadata and its associated transactions."""

    info: AccountInfo
    transactions: tuple[Transaction, ...]

    @property
    def transaction_count(self) -> int:
        """Return the number of transactions in the statement."""

        return len(self.transactions)

    @classmethod
    def from_api(cls, payload: Mapping[str, Any]) -> "Statement":
        raw_statement = payload.get("accountStatement")
        if not isinstance(raw_statement, Mapping):
            raise ParsingError("Payload does not contain accountStatement section")

        info_payload = raw_statement.get("info")
        if not isinstance(info_payload, Mapping):
            raise ParsingError("Payload does not contain statement info")

        info = AccountInfo.from_api(info_payload)

        transaction_list = raw_statement.get("transactionList", {})
        transactions_payload: Any = None
        if isinstance(transaction_list, Mapping):
            transactions_payload = transaction_list.get("transaction")
        else:
            transactions_payload = transaction_list

        transactions = tuple(
            Transaction.from_api(transaction)
            for transaction in _coerce_transactions(transactions_payload)
        )

        return cls(info=info, transactions=transactions)


def _coerce_transactions(value: Any) -> tuple[Mapping[str, Any], ...]:
    if value is None:
        return ()
    if isinstance(value, Mapping):
        return (value,)
    if isinstance(value, list | tuple):
        mappings = tuple(item for item in value if isinstance(item, Mapping))
        if len(mappings) != len(value):
            raise ParsingError("Transaction list contains invalid entries")
        return mappings
    raise ParsingError("Unexpected transaction list structure")
