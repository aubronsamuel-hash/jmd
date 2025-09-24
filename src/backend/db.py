from __future__ import annotations

from collections.abc import Generator
from contextlib import contextmanager
from typing import Any

from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker
from sqlalchemy.pool import StaticPool

from .config import Settings


class Base(DeclarativeBase):
    """Declarative base for ORM models."""


def _sqlite_connect_args(url: str) -> dict[str, Any]:
    if url.startswith("sqlite"):  # in-memory or file sqlite
        return {"check_same_thread": False}
    return {}


def build_engine(settings: Settings) -> Engine:
    """Create a SQLAlchemy engine based on the provided settings."""

    connect_args = _sqlite_connect_args(settings.database_url)
    if settings.database_url.startswith("sqlite"):
        return create_engine(
            settings.database_url,
            connect_args=connect_args,
            poolclass=StaticPool,
            future=True,
        )
    return create_engine(settings.database_url, future=True)


def build_session_factory(engine: Engine) -> sessionmaker[Session]:
    """Return a session factory bound to the engine."""

    return sessionmaker(bind=engine, expire_on_commit=False, class_=Session, future=True)


@contextmanager
def session_scope(session_factory: sessionmaker[Session]) -> Generator[Session, None, None]:
    """Provide a transactional scope around a series of operations."""

    session = session_factory()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()
