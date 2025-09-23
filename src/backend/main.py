"""FastAPI application entrypoint."""

from __future__ import annotations

from typing import Iterator
from uuid import UUID

from fastapi import Depends, FastAPI, HTTPException, status
from sqlalchemy.orm import Session, sessionmaker

from .config import get_settings
from .db import create_engine_from_settings, create_session_factory, run_migrations
from .domain import (
    PlanningCreate,
    PlanningError,
    PlanningNotFoundError,
    PlanningResponse,
    create_planning,
    get_planning,
    list_plannings,
)

SessionFactory = sessionmaker[Session]
_session_factory: SessionFactory | None = None


def _session_dependency() -> Iterator[Session]:
    """Yield a database session from the configured factory."""

    if _session_factory is None:  # pragma: no cover - configuration guard
        raise RuntimeError("Database session factory is not configured")
    session = _session_factory()
    try:
        yield session
    finally:
        session.close()


def create_app() -> FastAPI:
    """Instantiate and configure the FastAPI application."""

    settings = get_settings()
    engine = create_engine_from_settings(settings)
    run_migrations(engine)
    session_factory = create_session_factory(engine)
    global _session_factory
    _session_factory = session_factory

    app = FastAPI(title=settings.app_name)
    app.state.db_engine = engine
    app.state.db_session_factory = session_factory

    @app.get(f"{settings.api_prefix}/health", tags=["health"])
    async def healthcheck() -> dict[str, str]:
        """Simple endpoint used by monitoring systems."""

        return {
            "status": "ok",
            "environment": settings.environment,
            "service": settings.app_name,
        }

    @app.post(
        f"{settings.api_prefix}/plannings",
        response_model=PlanningResponse,
        status_code=status.HTTP_201_CREATED,
        tags=["planning"],
    )
    async def post_planning(
        payload: PlanningCreate, session: Session = Depends(_session_dependency)
    ) -> PlanningResponse:
        """Create a planning from the provided payload."""

        try:
            return create_planning(session=session, payload=payload)
        except PlanningError as exc:
            session.rollback()
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc

    @app.get(
        f"{settings.api_prefix}/plannings",
        response_model=list[PlanningResponse],
        tags=["planning"],
    )
    async def list_planning_items(
        session: Session = Depends(_session_dependency),
    ) -> list[PlanningResponse]:
        """Return the collection of persisted plannings."""

        return list_plannings(session=session)

    @app.get(
        f"{settings.api_prefix}/plannings/{{planning_id}}",
        response_model=PlanningResponse,
        tags=["planning"],
    )
    async def get_planning_item(
        planning_id: UUID, session: Session = Depends(_session_dependency)
    ) -> PlanningResponse:
        """Return a single planning based on its identifier."""

        try:
            return get_planning(session=session, planning_id=planning_id)
        except PlanningNotFoundError as exc:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc

    @app.on_event("shutdown")
    def shutdown_engine() -> None:
        engine.dispose()

    return app


app = create_app()

__all__ = ["app", "create_app"]
