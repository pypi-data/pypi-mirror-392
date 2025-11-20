# fio_api

Typed, well-documented client for the public Fio banking API. It focuses on
the JSON variant of the API and wraps the handful of available endpoints with a
small, user friendly class.

## Features

- Fetch statements by explicit date range or by their year/id combination
- Work with strongly typed dataclasses for account metadata and transactions
- Update server-side checkpoints (the "zarážka") via helper methods
- Includes a pytest suite with property-based tests

## Getting started

```bash
uv pip install -e .
```

```python
from datetime import date

from fio_api import FioClient

client = FioClient(api_key="your-token")
statement = client.fetch_transactions(date(2024, 1, 1), date(2024, 1, 31))
print(statement.info.closing_balance)
for transaction in statement.transactions:
    print(transaction.transaction_id, transaction.amount)
```

Use context manager support to ensure the underlying connection pool is
released:

```python
with FioClient(api_key="token") as client:
    print(client.get_balance())
```

## Testing

Install the optional dev dependencies and run the suite:

```bash
uv pip install -e .[dev]
uv run pytest
```

The tests stub the HTTP API via `httpx.MockTransport`, so no network access is
required.

## Examples

Use the bundled helper script to display the latest batch of transactions:

```bash
export FIO_API_KEY=your-token
uv run python -m scripts.show_transactions
```

The script fetches today's transactions (using the `periods/` endpoint) and
prints them in a small table with basic metadata.

## Documentation

The project ships an MkDocs site under `docs/`:

```bash
uv run mkdocs serve   # live reload
uv run mkdocs build   # produce static site
```

The published pages cover an overview, usage guide, and API reference.

> **Disclaimer**
>
> The project is licensed under the MIT License and provided "as is" without
> any warranty or responsibility. Use the code at your own risk.
