"""FastAPI application entrypoint."""

from __future__ import annotations

from typing import Iterator
from uuid import UUID

from fastapi import Depends, FastAPI, HTTPException, Response, status
from sqlalchemy.orm import Session, sessionmaker

from .config import get_settings
from .db import create_engine_from_settings, create_session_factory, run_migrations
from .domain import (
    Artist,
    ArtistConflictError,
    ArtistCreate,
    ArtistNotFoundError,
    ArtistUpdate,
    PlanningCreate,
    PlanningError,
    PlanningNotFoundError,
    PlanningResponse,
    create_artist,
    create_planning,
    delete_artist,
    get_artist,
    get_planning,
    list_artists,
    list_plannings,
    update_artist,
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

    @app.post(
        f"{settings.api_prefix}/artists",
        response_model=Artist,
        status_code=status.HTTP_201_CREATED,
        tags=["artists"],
    )
    async def post_artist(
        payload: ArtistCreate, session: Session = Depends(_session_dependency)
    ) -> Artist:
        """Create a new artist and persist its availabilities."""

        try:
            return create_artist(session=session, payload=payload)
        except ArtistConflictError as exc:
            session.rollback()
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc

    @app.get(
        f"{settings.api_prefix}/artists",
        response_model=list[Artist],
        tags=["artists"],
    )
    async def list_artist_items(
        session: Session = Depends(_session_dependency),
    ) -> list[Artist]:
        """Return all persisted artists ordered by name."""

        return list_artists(session=session)

    @app.get(
        f"{settings.api_prefix}/artists/{{artist_id}}",
        response_model=Artist,
        tags=["artists"],
    )
    async def get_artist_item(
        artist_id: UUID, session: Session = Depends(_session_dependency)
    ) -> Artist:
        """Return a single artist by identifier."""

        try:
            return get_artist(session=session, artist_id=artist_id)
        except ArtistNotFoundError as exc:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc

    @app.put(
        f"{settings.api_prefix}/artists/{{artist_id}}",
        response_model=Artist,
        tags=["artists"],
    )
    async def put_artist_item(
        artist_id: UUID,
        payload: ArtistUpdate,
        session: Session = Depends(_session_dependency),
    ) -> Artist:
        """Update an existing artist and replace its availabilities."""

        try:
            return update_artist(session=session, artist_id=artist_id, payload=payload)
        except ArtistNotFoundError as exc:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc

    @app.delete(
        f"{settings.api_prefix}/artists/{{artist_id}}",
        status_code=status.HTTP_204_NO_CONTENT,
        tags=["artists"],
    )
    async def delete_artist_item(
        artist_id: UUID, session: Session = Depends(_session_dependency)
    ) -> Response:
        """Remove an artist and its availabilities from persistence."""

        try:
            delete_artist(session=session, artist_id=artist_id)
        except ArtistNotFoundError as exc:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
        return Response(status_code=status.HTTP_204_NO_CONTENT)

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
