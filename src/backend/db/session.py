"""Helpers to configure SQLAlchemy engine and sessions."""

from __future__ import annotations

from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from backend.config import Settings


def create_engine_from_settings(settings: Settings) -> Engine:
    """Instantiate a SQLAlchemy engine based on runtime settings."""

    connect_args: dict[str, object] = {}
    engine_kwargs: dict[str, object] = {"future": True}

    if settings.database_url.startswith("sqlite"):  # pragma: no branch - deterministic
        connect_args["check_same_thread"] = False
        if settings.database_url.endswith(":memory:"):
            engine_kwargs["poolclass"] = StaticPool

    engine = create_engine(
        settings.database_url,
        echo=settings.sqlalchemy_echo,
        connect_args=connect_args,
        **engine_kwargs,
    )
    return engine


def create_session_factory(engine: Engine) -> sessionmaker[Session]:
    """Return a configured `sessionmaker` bound to the provided engine."""

    return sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)


def run_migrations(engine: Engine) -> None:
    """Execute database migrations.

    While Alembic integration is being wired into the delivery pipeline we
    simply delegate to `Base.metadata.create_all`, keeping the call idempotent
    so it can safely run at application startup.
    """

    from . import Base  # Local import to avoid circular dependency

    Base.metadata.create_all(bind=engine)
