"""FastAPI application entrypoint."""

from datetime import date, datetime
from typing import Annotated, Any, Iterator
from uuid import UUID

from fastapi import (
    Body,
    Depends,
    FastAPI,
    HTTPException,
    Query,
    Request,
    Response,
    status,
)
from pydantic import BaseModel, ConfigDict, Field, model_validator
from sqlalchemy.orm import Session, sessionmaker

from .config import get_settings
from .db import create_engine_from_settings, create_session_factory, run_migrations
from .domain import (
    AnalyticsDashboard,
    AnalyticsExport,
    AnalyticsExportFormat,
    AnalyticsFilter,
    AuditEventType,
    AuditExport,
    AuditExportFormat,
    AuditLogCollection,
    AuditLogFilter,
    AuditModule,
    AuditTrailService,
    Artist,
    ArtistConflictError,
    ArtistCreate,
    ArtistNotFoundError,
    ArtistUpdate,
    RetentionPolicy,
    RetentionPolicyError,
    RetentionSummary,
    PlanningCreate,
    PlanningError,
    PlanningNotFoundError,
    PlanningResponse,
    RgpdRequestComplete,
    RgpdRequestCreate,
    RgpdRequestNotFound,
    RgpdRequestRecord,
    create_artist,
    create_planning,
    delete_artist,
    generate_analytics_export,
    get_analytics_dashboard,
    get_artist,
    get_planning,
    list_artists,
    list_plannings,
    update_artist,
)
from .integrations import (
    CalendarSyncError,
    CalendarSyncService,
    InMemoryCalendarConnector,
    InMemoryStorageConnector,
    StorageError,
    StorageGateway,
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


def _audit_service_dependency(request: Request) -> AuditTrailService:
    """Return the audit service configured on the FastAPI app."""

    audit_service = getattr(request.app.state, "audit_service", None)
    if audit_service is None:  # pragma: no cover - configuration guard
        raise RuntimeError("Audit service is not configured")
    return audit_service


AuditServiceDependency = Annotated[AuditTrailService, Depends(_audit_service_dependency)]


class RetentionPolicyUpdateRequest(BaseModel):
    """Request payload used to adjust retention policies."""

    model_config = ConfigDict(extra="forbid")

    retention_days: int = Field(..., ge=1, description="Nombre de jours de retention")
    archive_after_days: int = Field(
        ..., ge=1, description="Nombre de jours avant archivage"
    )


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
    calendar_connectors = [
        InMemoryCalendarConnector(name=name)
        for name in settings.calendar_connectors
    ]
    calendar_service = CalendarSyncService(
        connectors=calendar_connectors,
        calendar_name=settings.calendar_name,
    )
    app.state.calendar_service = calendar_service
    storage_connectors = [
        InMemoryStorageConnector(name=name)
        for name in settings.storage_connectors
    ]
    storage_gateway = StorageGateway(connectors=storage_connectors)
    app.state.storage_gateway = storage_gateway
    audit_service = AuditTrailService(
        signature_secret=settings.audit_signature_secret,
        default_organization=settings.audit_default_organization,
        default_retention_days=settings.audit_retention_days,
        default_archive_days=settings.audit_archive_days,
        rgpd_sla_days=settings.audit_rgpd_sla_days,
    )
    app.state.audit_service = audit_service

    @app.post(
        f"{settings.api_prefix}/artists",
        response_model=Artist,
        status_code=status.HTTP_201_CREATED,
        tags=["artists"],
    )
    async def post_artist(
        payload: ArtistCreate,
        session: SessionDependency,
        audit_service: AuditServiceDependency,
    ) -> Artist:
        """Create a new artist and persist its availabilities."""

        try:
            artist = create_artist(session=session, payload=payload)
        except ArtistConflictError as exc:
            session.rollback()
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc
        audit_service.log_event(
            session=session,
            event_type=AuditEventType.ARTIST_CREATED,
            module=AuditModule.ARTISTS,
            action="artist.create",
            target_type="artist",
            target_id=str(artist.id),
            payload=artist.model_dump(),
        )
        session.commit()
        return artist

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
        audit_service: AuditServiceDependency,
    ) -> Artist:
        """Update an existing artist and replace its availabilities."""

        try:
            artist = update_artist(
                session=session, artist_id=artist_id, payload=payload
            )
        except ArtistNotFoundError as exc:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
        audit_service.log_event(
            session=session,
            event_type=AuditEventType.ARTIST_UPDATED,
            module=AuditModule.ARTISTS,
            action="artist.update",
            target_type="artist",
            target_id=str(artist.id),
            payload=artist.model_dump(),
        )
        session.commit()
        return artist

    @app.delete(
        f"{settings.api_prefix}/artists/{{artist_id}}",
        status_code=status.HTTP_204_NO_CONTENT,
        tags=["artists"],
    )
    async def delete_artist_item(
        artist_id: UUID,
        session: SessionDependency,
        audit_service: AuditServiceDependency,
    ) -> Response:
        """Remove an artist and its availabilities from persistence."""

        try:
            delete_artist(session=session, artist_id=artist_id)
        except ArtistNotFoundError as exc:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
        audit_service.log_event(
            session=session,
            event_type=AuditEventType.ARTIST_DELETED,
            module=AuditModule.ARTISTS,
            action="artist.delete",
            target_type="artist",
            target_id=str(artist_id),
            payload={"artist_id": str(artist_id)},
        )
        session.commit()
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
        audit_service: AuditServiceDependency,
    ) -> PlanningResponse:
        """Create a planning from the provided payload."""

        try:
            planning_response = create_planning(session=session, payload=payload)
        except PlanningError as exc:
            session.rollback()
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
        audit_service.log_event(
            session=session,
            event_type=AuditEventType.PLANNING_CREATED,
            module=AuditModule.PLANNING,
            action="planning.create",
            target_type="planning",
            target_id=str(planning_response.planning_id),
            payload=planning_response.model_dump(),
        )
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
            audit_service.log_event(
                session=session,
                event_type=AuditEventType.PLANNING_NOTIFIED,
                module=AuditModule.NOTIFICATIONS,
                action="planning.notify",
                target_type="planning",
                target_id=str(planning_response.planning_id),
                payload={
                    "channels": report.channels,
                    "event": report.event.value,
                },
            )
        try:
            calendar_service.synchronize_planning(
                planning=planning_response, artists=payload.artists
            )
        except CalendarSyncError as exc:  # pragma: no cover - defensive branch
            response.headers["X-Calendar-Error"] = ",".join(exc.errors.keys())
        else:
            response.headers["X-Calendar-Targets"] = ",".join(
                connector.name for connector in calendar_service.connectors
            )
        try:
            storage_results = storage_gateway.publish_planning_document(
                planning=planning_response, artists=payload.artists
            )
        except StorageError as exc:  # pragma: no cover - defensive branch
            response.headers["X-Storage-Error"] = ",".join(exc.errors.keys())
        else:
            response.headers["X-Storage-Targets"] = ",".join(
                dict.fromkeys(result.connector for result in storage_results)
            )
            audit_service.log_event(
                session=session,
                event_type=AuditEventType.STORAGE_PUBLISHED,
                module=AuditModule.INTEGRATIONS,
                action="planning.storage.publish",
                target_type="planning",
                target_id=str(planning_response.planning_id),
                payload={
                    "targets": [result.connector for result in storage_results],
                },
            )
        session.commit()
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

    @app.get(
        f"{settings.api_prefix}/analytics/dashboard",
        response_model=AnalyticsDashboard,
        tags=["analytics"],
    )
    async def get_analytics_dashboard_item(
        session: SessionDependency,
        project: str | None = Query(default=None, description="Filtre projet"),
        location: str | None = Query(default=None, description="Filtre lieu"),
        team: str | None = Query(default=None, description="Filtre equipe"),
        start_date: date | None = Query(
            default=None, description="Date de debut (incluse)", alias="start_date"
        ),
        end_date: date | None = Query(
            default=None, description="Date de fin (incluse)", alias="end_date"
        ),
    ) -> AnalyticsDashboard:
        """Expose KPIs, heatmaps and curves for the analytics dashboard."""

        filters = AnalyticsFilter(
            project=project,
            location=location,
            team=team,
            start_date=start_date,
            end_date=end_date,
        )
        return get_analytics_dashboard(session=session, filters=filters)

    @app.get(
        f"{settings.api_prefix}/analytics/exports",
        response_model=AnalyticsExport,
        tags=["analytics"],
    )
    async def get_analytics_export_item(
        session: SessionDependency,
        export_format: AnalyticsExportFormat = Query(
            default=AnalyticsExportFormat.CSV,
            alias="format",
            description="Format d'export desire",
        ),
        project: str | None = Query(default=None, description="Filtre projet"),
        location: str | None = Query(default=None, description="Filtre lieu"),
        team: str | None = Query(default=None, description="Filtre equipe"),
        start_date: date | None = Query(
            default=None, description="Date de debut (incluse)", alias="start_date"
        ),
        end_date: date | None = Query(
            default=None, description="Date de fin (incluse)", alias="end_date"
        ),
    ) -> AnalyticsExport:
        """Generate CSV/PDF/PNG exports for the analytics dashboard."""

        filters = AnalyticsFilter(
            project=project,
            location=location,
            team=team,
            start_date=start_date,
            end_date=end_date,
        )
        return generate_analytics_export(
            session=session, filters=filters, export_format=export_format
        )

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
        audit_service: AuditServiceDependency,
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
        audit_service.log_event(
            session=session,
            event_type=AuditEventType.PLANNING_NOTIFIED,
            module=AuditModule.NOTIFICATIONS,
            action="planning.notify",
            target_type="planning",
            target_id=str(planning_id),
            payload={
                "channels": report.channels,
                "event": report.event.value,
            },
        )
        session.commit()
        return NotificationDispatchResponse(
            event=report.event,
            subject=report.subject,
            body=report.body,
            channels=report.channels,
            metadata=report.metadata,
        )

    @app.get(
        f"{settings.api_prefix}/audit/logs",
        response_model=AuditLogCollection,
        tags=["audit"],
    )
    async def list_audit_logs(
        session: SessionDependency,
        audit_service: AuditServiceDependency,
        organization_id: str | None = Query(default=None, description="Organisation"),
        module: AuditModule | None = Query(default=None, description="Module"),
        actor_id: str | None = Query(default=None, description="Utilisateur"),
        event_type: AuditEventType | None = Query(
            default=None, description="Type d'evenement"
        ),
        start_at: datetime | None = Query(
            default=None, description="Date de debut (ISO8601)", alias="start_at"
        ),
        end_at: datetime | None = Query(
            default=None, description="Date de fin (ISO8601)", alias="end_at"
        ),
    ) -> AuditLogCollection:
        """Return audit logs filtered by the provided criteria."""

        filters = AuditLogFilter(
            organization_id=organization_id,
            module=module,
            actor_id=actor_id,
            event_type=event_type,
            start_at=start_at,
            end_at=end_at,
        )
        return audit_service.list_logs(session=session, filters=filters)

    @app.get(
        f"{settings.api_prefix}/audit/logs/export",
        response_model=AuditExport,
        tags=["audit"],
    )
    async def export_audit_logs(
        session: SessionDependency,
        audit_service: AuditServiceDependency,
        export_format: AuditExportFormat = Query(
            default=AuditExportFormat.JSON,
            alias="format",
            description="Format d'export",
        ),
        organization_id: str | None = Query(default=None, description="Organisation"),
        module: AuditModule | None = Query(default=None, description="Module"),
        actor_id: str | None = Query(default=None, description="Utilisateur"),
        event_type: AuditEventType | None = Query(
            default=None, description="Type d'evenement"
        ),
        start_at: datetime | None = Query(
            default=None, description="Date de debut (ISO8601)", alias="start_at"
        ),
        end_at: datetime | None = Query(
            default=None, description="Date de fin (ISO8601)", alias="end_at"
        ),
    ) -> AuditExport:
        """Export audit logs into the requested format."""

        filters = AuditLogFilter(
            organization_id=organization_id,
            module=module,
            actor_id=actor_id,
            event_type=event_type,
            start_at=start_at,
            end_at=end_at,
        )
        return audit_service.export_logs(
            session=session, filters=filters, export_format=export_format
        )

    @app.get(
        f"{settings.api_prefix}/audit/organizations/{{organization_id}}/retention",
        response_model=RetentionPolicy,
        tags=["audit"],
    )
    async def get_retention_policy_endpoint(
        organization_id: str,
        session: SessionDependency,
        audit_service: AuditServiceDependency,
    ) -> RetentionPolicy:
        """Return the retention policy configured for an organization."""

        return audit_service.get_retention_policy(
            session=session, organization_id=organization_id
        )

    @app.put(
        f"{settings.api_prefix}/audit/organizations/{{organization_id}}/retention",
        response_model=RetentionPolicy,
        tags=["audit"],
    )
    async def update_retention_policy(
        organization_id: str,
        payload: RetentionPolicyUpdateRequest,
        session: SessionDependency,
        audit_service: AuditServiceDependency,
    ) -> RetentionPolicy:
        """Update or create a retention policy for the organization."""

        try:
            policy = audit_service.configure_retention_policy(
                session=session,
                organization_id=organization_id,
                retention_days=payload.retention_days,
                archive_after_days=payload.archive_after_days,
            )
        except RetentionPolicyError as exc:
            session.rollback()
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
        session.commit()
        return policy

    @app.post(
        f"{settings.api_prefix}/audit/organizations/{{organization_id}}/retention/run",
        response_model=RetentionSummary,
        tags=["audit"],
    )
    async def run_retention_job_endpoint(
        organization_id: str,
        session: SessionDependency,
        audit_service: AuditServiceDependency,
    ) -> RetentionSummary:
        """Trigger retention tasks (archive + purge) for the organization."""

        summary = audit_service.run_retention_job(
            session=session, organization_id=organization_id
        )
        session.commit()
        return summary

    @app.post(
        f"{settings.api_prefix}/rgpd/requests",
        response_model=RgpdRequestRecord,
        status_code=status.HTTP_201_CREATED,
        tags=["rgpd"],
    )
    async def register_rgpd_request(
        payload: RgpdRequestCreate,
        session: SessionDependency,
        audit_service: AuditServiceDependency,
    ) -> RgpdRequestRecord:
        """Register a new GDPR data subject request."""

        record = audit_service.register_rgpd_request(session=session, payload=payload)
        session.commit()
        return record

    @app.post(
        f"{settings.api_prefix}/rgpd/requests/{{request_id}}/complete",
        response_model=RgpdRequestRecord,
        tags=["rgpd"],
    )
    async def complete_rgpd_request_endpoint(
        request_id: UUID,
        payload: RgpdRequestComplete,
        session: SessionDependency,
        audit_service: AuditServiceDependency,
    ) -> RgpdRequestRecord:
        """Mark a GDPR request as completed and trace the resolution."""

        try:
            record = audit_service.complete_rgpd_request(
                session=session, request_id=request_id, payload=payload
            )
        except RgpdRequestNotFound as exc:
            session.rollback()
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
        session.commit()
        return record

    @app.get(
        f"{settings.api_prefix}/rgpd/requests",
        response_model=list[RgpdRequestRecord],
        tags=["rgpd"],
    )
    async def list_rgpd_requests_endpoint(
        session: SessionDependency,
        audit_service: AuditServiceDependency,
        organization_id: str | None = Query(
            default=None, description="Organisation concernee"
        ),
    ) -> list[RgpdRequestRecord]:
        """List GDPR requests for the organization."""

        return audit_service.list_rgpd_requests(
            session=session, organization_id=organization_id
        )

    @app.on_event("shutdown")
    def shutdown_engine() -> None:
        engine.dispose()

    return app


app = create_app()

__all__ = ["app", "create_app"]
