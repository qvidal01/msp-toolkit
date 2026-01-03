"""
Database helpers for MSP Toolkit.

Provides SQLAlchemy engine/session management with SQLite defaults.
"""

from __future__ import annotations

from collections.abc import Iterator
from contextlib import contextmanager
from functools import lru_cache
from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import declarative_base, sessionmaker

Base = declarative_base()


def _build_sqlite_url(path: str) -> str:
    if path == ":memory:":
        return "sqlite:///:memory:"

    db_path = Path(path)
    db_path.parent.mkdir(parents=True, exist_ok=True)
    return f"sqlite:///{db_path}"


@lru_cache(maxsize=8)
def get_engine(db_type: str, db_path: str | None) -> Engine:
    """Create (or reuse cached) SQLAlchemy engine."""
    if db_type != "sqlite":
        raise ValueError(f"Unsupported database type: {db_type}")

    url = _build_sqlite_url(db_path or "data/msp-toolkit.db")
    return create_engine(url, echo=False, future=True)


def get_session_factory(engine: Engine) -> sessionmaker:
    """Return a session factory bound to the provided engine."""
    return sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)


@contextmanager
def session_scope(engine: Engine) -> Iterator:
    """
    Provide a transactional scope around a series of operations.

    Commits on success, rolls back on failure.
    """
    Session = get_session_factory(engine)
    session = Session()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


def init_db(engine: Engine) -> None:
    """Create all tables if they don't exist."""
    Base.metadata.create_all(bind=engine)
