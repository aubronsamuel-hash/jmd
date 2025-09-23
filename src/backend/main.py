"""FastAPI application entrypoint."""

from typing import Annotated, Any, Iterator
from uuid import UUID

from fastapi import Body, Depends, FastAPI, HTTPException, Response, status
from pydantic import BaseModel, ConfigDict, Field, model_validator
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
from .notifications import (
    EmailNotificationChannel,
    NotificationDeliveryError,
    NotificationEventType,
    NotificationService,
    TelegramNotificationChannel,
)


class NotificationDispatchResponse(BaseModel):
    """API response summarizing a notification dispatch."""

    model_config = ConfigDict(extra="forbid")

    event: NotificationEventType
    subject: str
    body: str
    channels: list[str]
    metadata: dict[str, Any]


class PlanningNotificationRequest(BaseModel):
    """Payload used to trigger a notification for a planning event."""

    model_config = ConfigDict(extra="forbid")

    event: NotificationEventType = Field(
        ..., description="Evenement de notification a declencher"
    )

    @model_validator(mode="after")
    def _validate_event(self) -> "PlanningNotificationRequest":
        if self.event is NotificationEventType.TEST:
            raise ValueError(
                "L'evenement de test doit etre utilise via /notifications/test."
            )
        return self


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


SessionDependency = Annotated[Session, Depends(_session_dependency)]


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
    email_channel = EmailNotificationChannel(
        sender=settings.notification_email_sender,
        recipients=settings.notification_email_recipients,
    )
    telegram_channel = TelegramNotificationChannel(
        bot_token=settings.notification_telegram_bot_token,
        chat_ids=settings.notification_telegram_chat_ids,
    )
    notification_service = NotificationService(
        channels=[email_channel, telegram_channel]
    )
    app.state.notification_service = notification_service

    @app.post(
        f"{settings.api_prefix}/artists",
        response_model=Artist,
        status_code=status.HTTP_201_CREATED,
        tags=["artists"],
    )
    async def post_artist(
        payload: ArtistCreate, session: SessionDependency
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
        session: SessionDependency,
    ) -> list[Artist]:
        """Return all persisted artists ordered by name."""

        return list_artists(session=session)

    @app.get(
        f"{settings.api_prefix}/artists/{{artist_id}}",
        response_model=Artist,
        tags=["artists"],
    )
    async def get_artist_item(
        artist_id: UUID, session: SessionDependency
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
        session: SessionDependency,
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
        artist_id: UUID, session: SessionDependency
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
        payload: PlanningCreate,
        response: Response,
        session: SessionDependency,
    ) -> PlanningResponse:
        """Create a planning from the provided payload."""

        try:
            planning_response = create_planning(session=session, payload=payload)
        except PlanningError as exc:
            session.rollback()
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
        try:
            report = notification_service.notify_planning_event(
                planning=planning_response,
                artists=payload.artists,
                event_type=NotificationEventType.PLANNING_CREATED,
            )
        except NotificationDeliveryError as exc:  # pragma: no cover - defensive branch
            response.headers["X-Notification-Error"] = exc.event.value
            response.headers["X-Notification-Error-Channels"] = ",".join(
                f"{name}:{error}" for name, error in exc.errors.items()
            )
        else:
            response.headers["X-Notification-Channels"] = ",".join(report.channels)
        return planning_response

    @app.get(
        f"{settings.api_prefix}/plannings",
        response_model=list[PlanningResponse],
        tags=["planning"],
    )
    async def list_planning_items(
        session: SessionDependency,
    ) -> list[PlanningResponse]:
        """Return the collection of persisted plannings."""

        return list_plannings(session=session)

    @app.get(
        f"{settings.api_prefix}/plannings/{{planning_id}}",
        response_model=PlanningResponse,
        tags=["planning"],
    )
    async def get_planning_item(
        planning_id: UUID, session: SessionDependency
    ) -> PlanningResponse:
        """Return a single planning based on its identifier."""

        try:
            return get_planning(session=session, planning_id=planning_id)
        except PlanningNotFoundError as exc:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc

    @app.post(
        f"{settings.api_prefix}/notifications/test",
        response_model=NotificationDispatchResponse,
        tags=["notifications"],
    )
    async def trigger_test_notification() -> NotificationDispatchResponse:
        """Trigger a test notification across all configured channels."""

        try:
            report = notification_service.send_test_notification()
        except NotificationDeliveryError as exc:  # pragma: no cover - defensive branch
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail={"event": exc.event.value, "errors": exc.errors},
            ) from exc
        return NotificationDispatchResponse(
            event=report.event,
            subject=report.subject,
            body=report.body,
            channels=report.channels,
            metadata=report.metadata,
        )

    @app.post(
        f"{settings.api_prefix}/notifications/plannings/{{planning_id}}/events",
        response_model=NotificationDispatchResponse,
        tags=["notifications"],
    )
    async def trigger_planning_notification(
        planning_id: UUID,
        payload: PlanningNotificationRequest,
        session: SessionDependency,
    ) -> NotificationDispatchResponse:
        """Dispatch a notification for a persisted planning event."""

        try:
            planning = get_planning(session=session, planning_id=planning_id)
        except PlanningNotFoundError as exc:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc

        artists: list[Artist] = []
        seen: set[UUID] = set()
        for assignment in planning.assignments:
            if assignment.artist_id in seen:
                continue
            try:
                artist = get_artist(session=session, artist_id=assignment.artist_id)
            except ArtistNotFoundError:  # pragma: no cover - defensive branch
                continue
            artists.append(artist)
            seen.add(artist.id)

        try:
            report = notification_service.notify_planning_event(
                planning=planning,
                artists=artists,
                event_type=payload.event,
            )
        except NotificationDeliveryError as exc:  # pragma: no cover - defensive branch
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail={"event": exc.event.value, "errors": exc.errors},
            ) from exc
        return NotificationDispatchResponse(
            event=report.event,
            subject=report.subject,
            body=report.body,
            channels=report.channels,
            metadata=report.metadata,
        )

    @app.on_event("shutdown")
    def shutdown_engine() -> None:
        engine.dispose()

    return app


app = create_app()

__all__ = ["app", "create_app"]
