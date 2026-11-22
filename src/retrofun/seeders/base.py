# src/retrofun/seeders/base.py
"""Shared utilities and context managers for data import seeders."""

import contextlib
from collections.abc import Generator
from datetime import UTC, datetime
from pathlib import Path

from sqlalchemy.orm import Session

from retrofun.db import SessionLocal


@contextlib.contextmanager
def get_db_session() -> Generator[Session]:
    """
    Context manager that yields a SQLAlchemy session wrapped in a transaction.
    Automatically commits on success and rolls back on exception.
    """
    with SessionLocal() as session, session.begin():
        yield session


def get_data_dir() -> Path:
    """Resolves the path to the raw_data directory at the project root."""
    # scripts/base.py -> parents[0] is scripts, [1] is retrofun, [2] is src, [3] is root
    return Path(__file__).parents[3] / "raw_data"


def parse_timestamp(ts_str: str) -> datetime:
    """Parses a standard CSV timestamp string into a UTC-aware datetime."""
    naive_dt = datetime.strptime(ts_str, "%Y-%m-%d %H:%M:%S")
    return naive_dt.replace(tzinfo=UTC)
