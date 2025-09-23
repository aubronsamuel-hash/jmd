"""Domain services for audit trail, retention and GDPR workflows."""

from __future__ import annotations

import base64
import csv
import json
import hmac
from dataclasses import dataclass
from datetime import date, datetime, timedelta, timezone
from enum import Enum, StrEnum
from io import StringIO
from typing import Any, Iterable, Mapping
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from backend.models import (
    AuditLog as AuditLogModel,
    AuditRetentionEvent as AuditRetentionEventModel,
    AuditRetentionPolicy as AuditRetentionPolicyModel,
    RgpdRequest as RgpdRequestModel,
    RgpdRequestHistory as RgpdRequestHistoryModel,
)


class AuditError(Exception):
    """Base class for audit service related errors."""


class AuditLogNotFound(AuditError):
    """Raised when a requested audit log entry is missing."""


class RetentionPolicyError(AuditError):
    """Raised when a retention policy is missing or inconsistent."""


class RgpdRequestNotFound(AuditError):
    """Raised when a GDPR request cannot be located."""


class AuditModule(StrEnum):
    """Modules contributing audit events."""

    PLANNING = "planning"
    ARTISTS = "artists"
    PAYROLL = "payroll"
    MATERIAL = "material"
    NOTIFICATIONS = "notifications"
    INTEGRATIONS = "integrations"
    RGPD = "rgpd"
    RETENTION = "retention"


class AuditEventType(StrEnum):
    """Catalog of supported audit events."""

    ARTIST_CREATED = "artist.created"
    ARTIST_UPDATED = "artist.updated"
    ARTIST_DELETED = "artist.deleted"
    PLANNING_CREATED = "planning.created"
    PLANNING_NOTIFIED = "planning.notified"
    STORAGE_PUBLISHED = "storage.published"
    RGPD_REQUEST_REGISTERED = "rgpd.request.registered"
    RGPD_REQUEST_COMPLETED = "rgpd.request.completed"
    RETENTION_POLICY_UPDATED = "audit.retention.policy_updated"
    RETENTION_EXECUTED = "audit.retention.executed"


class AuditExportFormat(StrEnum):
    """Export formats supported by the audit trail."""

    JSON = "json"
    CSV = "csv"


class AuditLogFilter(BaseModel):
    """Filtering options exposed on the audit API."""

    model_config = ConfigDict(extra="forbid")

    organization_id: str | None = Field(default=None, description="Filtre organisation")
    module: AuditModule | None = Field(default=None, description="Filtre module")
    actor_id: str | None = Field(default=None, description="Filtre utilisateur")
    event_type: AuditEventType | None = Field(
        default=None, description="Filtre type d'evenement"
    )
    start_at: datetime | None = Field(
        default=None, description="Date debut (incluse)", alias="start_at"
    )
    end_at: datetime | None = Field(
        default=None, description="Date fin (incluse)", alias="end_at"
    )


class AuditLogEntry(BaseModel):
    """Immutable representation of an audit log record."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    id: UUID
    organization_id: str
    module: AuditModule
    event_type: AuditEventType
    action: str
    actor_type: str | None
    actor_id: str | None
    target_type: str | None
    target_id: str | None
    payload_version: int
    payload: dict[str, Any]
    signature: str
    created_at: datetime
    archived_at: datetime | None
    archive_reference: str | None


class AuditLogCollection(BaseModel):
    """Response returned by the listing endpoint."""

    model_config = ConfigDict(extra="forbid")

    items: list[AuditLogEntry]
    count: int


class AuditExport(BaseModel):
    """Encoded export bundle with signature."""

    model_config = ConfigDict(extra="forbid")

    format: AuditExportFormat
    filename: str
    content_type: str
    generated_at: datetime
    data_base64: str
    signature: str
    filters: AuditLogFilter


class RetentionPolicy(BaseModel):
    """Retention policy exposed through the API."""

    model_config = ConfigDict(extra="forbid")

    organization_id: str
    retention_days: int
    archive_after_days: int
    updated_at: datetime


class RetentionSummary(BaseModel):
    """Summary returned after executing a retention job."""

    model_config = ConfigDict(extra="forbid")

    organization_id: str
    executed_at: datetime
    purged_count: int
    archived_count: int
    anonymized_count: int
    details: dict[str, Any]


class RgpdRequestType(StrEnum):
    """Data subject request types."""

    ACCESS = "access"
    RECTIFICATION = "rectification"
    ERASURE = "erasure"


class RgpdRequestStatus(StrEnum):
    """Workflow status for GDPR requests."""

    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"


class RgpdRequestCreate(BaseModel):
    """Payload used to register a new GDPR request."""

    model_config = ConfigDict(extra="forbid")

    request_type: RgpdRequestType = Field(..., description="Type de demande")
    requester: str = Field(..., description="Demandeur ou source")
    subject_reference: str = Field(
        ..., description="Identifiant de la personne concernee"
    )
    organization_id: str | None = Field(
        default=None, description="Organisation cible"
    )
    notes: str | None = Field(default=None, description="Notes complementaires")


class RgpdRequestComplete(BaseModel):
    """Payload used to complete a GDPR request."""

    model_config = ConfigDict(extra="forbid")

    processor: str = Field(..., description="Operateur ayant traite la demande")
    resolution_notes: str | None = Field(
        default=None, description="Trace de la reponse transmise"
    )


class RgpdRequestRecord(BaseModel):
    """Representation of a GDPR request."""

    model_config = ConfigDict(extra="forbid")

    id: UUID
    organization_id: str
    request_type: RgpdRequestType
    status: RgpdRequestStatus
    requester: str
    subject_reference: str
    submitted_at: datetime
    due_at: datetime
    processed_at: datetime | None
    completed_at: datetime | None
    processor: str | None
    resolution_notes: str | None


def _ensure_timezone(value: datetime) -> datetime:
    """Return a timezone aware datetime in UTC."""

    if value.tzinfo is None:
        return value.replace(tzinfo=timezone.utc)
    return value.astimezone(timezone.utc)


@dataclass(frozen=True)
class _ExportContent:
    content: bytes
    signature: str
    filename: str
    content_type: str


class AuditTrailService:
    """High level facade orchestrating audit persistence and exports."""

    def __init__(
        self,
        *,
        signature_secret: str,
        default_organization: str,
        default_retention_days: int,
        default_archive_days: int,
        rgpd_sla_days: int,
    ) -> None:
        self._secret = signature_secret.encode("utf-8")
        self._default_org = default_organization
        self._default_retention_days = max(default_retention_days, 1)
        self._default_archive_days = max(min(default_archive_days, self._default_retention_days), 1)
        self._rgpd_sla_days = max(rgpd_sla_days, 1)

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------
    @staticmethod
    def _normalize_payload(payload: Mapping[str, Any] | None) -> dict[str, Any]:
        def _transform(value: Any) -> Any:
            if isinstance(value, BaseModel):
                return _transform(value.model_dump())
            if isinstance(value, UUID):
                return str(value)
            if isinstance(value, Enum):
                return value.value
            if isinstance(value, date) and not isinstance(value, datetime):
                return value.isoformat()
            if isinstance(value, datetime):
                return _ensure_timezone(value).isoformat()
            if isinstance(value, Mapping):
                return {key: _transform(item) for key, item in value.items()}
            if isinstance(value, Iterable) and not isinstance(value, (str, bytes)):
                return [_transform(item) for item in value]
            return value

        if not payload:
            return {}
        return {key: _transform(val) for key, val in payload.items()}

    def _sign(self, data: Mapping[str, Any]) -> str:
        canonical = json.dumps(data, sort_keys=True, separators=(",", ":"))
        digest = hmac.new(self._secret, canonical.encode("utf-8"), "sha256")
        return digest.hexdigest()

    @staticmethod
    def _entry_from_model(model: AuditLogModel) -> AuditLogEntry:
        return AuditLogEntry(
            id=model.id,
            organization_id=model.organization_id,
            module=AuditModule(model.module),
            event_type=AuditEventType(model.event_type),
            action=model.action,
            actor_type=model.actor_type,
            actor_id=model.actor_id,
            target_type=model.target_type,
            target_id=model.target_id,
            payload_version=model.payload_version,
            payload=model.payload,
            signature=model.signature,
            created_at=_ensure_timezone(model.created_at),
            archived_at=_ensure_timezone(model.archived_at)
            if model.archived_at
            else None,
            archive_reference=model.archive_reference,
        )

    # ------------------------------------------------------------------
    # Audit log operations
    # ------------------------------------------------------------------
    def log_event(
        self,
        session: Session,
        *,
        event_type: AuditEventType,
        module: AuditModule,
        action: str,
        organization_id: str | None = None,
        actor_type: str | None = None,
        actor_id: str | None = None,
        target_type: str | None = None,
        target_id: str | None = None,
        payload: Mapping[str, Any] | None = None,
        payload_version: int = 1,
        commit: bool = False,
    ) -> AuditLogEntry:
        org = organization_id or self._default_org
        normalized_payload = self._normalize_payload(payload)
        created_at_utc = datetime.now(timezone.utc)
        signature_payload = {
            "organization_id": org,
            "module": module.value,
            "event_type": event_type.value,
            "action": action,
            "actor_type": actor_type,
            "actor_id": actor_id,
            "target_type": target_type,
            "target_id": target_id,
            "payload_version": payload_version,
            "payload": normalized_payload,
            "created_at": created_at_utc.isoformat(),
        }
        signature = self._sign(signature_payload)
        model = AuditLogModel(
            organization_id=org,
            module=module.value,
            event_type=event_type.value,
            action=action,
            actor_type=actor_type,
            actor_id=actor_id,
            target_type=target_type,
            target_id=target_id,
            payload_version=payload_version,
            payload=normalized_payload,
            signature=signature,
            created_at=created_at_utc.replace(tzinfo=None),
        )
        session.add(model)
        session.flush()
        if commit:
            session.commit()
        return self._entry_from_model(model)

    def list_logs(self, session: Session, filters: AuditLogFilter) -> AuditLogCollection:
        stmt = select(AuditLogModel).order_by(AuditLogModel.created_at.desc())
        if filters.organization_id:
            stmt = stmt.where(AuditLogModel.organization_id == filters.organization_id)
        if filters.module:
            stmt = stmt.where(AuditLogModel.module == filters.module.value)
        if filters.actor_id:
            stmt = stmt.where(AuditLogModel.actor_id == filters.actor_id)
        if filters.event_type:
            stmt = stmt.where(AuditLogModel.event_type == filters.event_type.value)
        if filters.start_at:
            stmt = stmt.where(AuditLogModel.created_at >= _ensure_timezone(filters.start_at))
        if filters.end_at:
            stmt = stmt.where(AuditLogModel.created_at <= _ensure_timezone(filters.end_at))
        items = [self._entry_from_model(model) for model in session.scalars(stmt).all()]
        return AuditLogCollection(items=items, count=len(items))

    def export_logs(
        self,
        session: Session,
        filters: AuditLogFilter,
        export_format: AuditExportFormat,
    ) -> AuditExport:
        collection = self.list_logs(session, filters)
        generated_at = datetime.now(timezone.utc)
        if export_format is AuditExportFormat.JSON:
            content = json.dumps(
                [entry.model_dump() for entry in collection.items],
                ensure_ascii=False,
                separators=(",", ":"),
            ).encode("utf-8")
            filename = f"audit-logs-{generated_at.strftime('%Y%m%d%H%M%S')}.json"
            content_type = "application/json"
        else:
            csv_buffer = StringIO()
            writer = csv.DictWriter(
                csv_buffer,
                fieldnames=[
                    "id",
                    "created_at",
                    "organization_id",
                    "module",
                    "event_type",
                    "action",
                    "actor_id",
                    "actor_type",
                    "target_id",
                    "target_type",
                    "payload_version",
                    "payload",
                    "signature",
                ],
            )
            writer.writeheader()
            for entry in collection.items:
                writer.writerow(
                    {
                        "id": str(entry.id),
                        "created_at": entry.created_at.isoformat(),
                        "organization_id": entry.organization_id,
                        "module": entry.module.value,
                        "event_type": entry.event_type.value,
                        "action": entry.action,
                        "actor_id": entry.actor_id or "",
                        "actor_type": entry.actor_type or "",
                        "target_id": entry.target_id or "",
                        "target_type": entry.target_type or "",
                        "payload_version": entry.payload_version,
                        "payload": json.dumps(entry.payload, ensure_ascii=False),
                        "signature": entry.signature,
                    }
                )
            content = csv_buffer.getvalue().encode("utf-8")
            filename = f"audit-logs-{generated_at.strftime('%Y%m%d%H%M%S')}.csv"
            content_type = "text/csv"
        signature = self._sign(
            {
                "generated_at": generated_at.isoformat(),
                "format": export_format.value,
                "digest": hmac.new(
                    self._secret, content, "sha256"
                ).hexdigest(),
            }
        )
        encoded = base64.b64encode(content).decode("ascii")
        return AuditExport(
            format=export_format,
            filename=filename,
            content_type=content_type,
            generated_at=generated_at,
            data_base64=encoded,
            signature=signature,
            filters=filters,
        )

    # ------------------------------------------------------------------
    # Retention policies
    # ------------------------------------------------------------------
    def get_retention_policy(
        self, session: Session, organization_id: str | None = None
    ) -> RetentionPolicy:
        org = organization_id or self._default_org
        stmt = select(AuditRetentionPolicyModel).where(
            AuditRetentionPolicyModel.organization_id == org
        )
        model = session.execute(stmt).scalar_one_or_none()
        if model is None:
            return RetentionPolicy(
                organization_id=org,
                retention_days=self._default_retention_days,
                archive_after_days=self._default_archive_days,
                updated_at=datetime.now(timezone.utc),
            )
        return RetentionPolicy(
            organization_id=model.organization_id,
            retention_days=model.retention_days,
            archive_after_days=model.archive_after_days,
            updated_at=_ensure_timezone(model.updated_at),
        )

    def configure_retention_policy(
        self,
        session: Session,
        *,
        organization_id: str,
        retention_days: int,
        archive_after_days: int,
        commit: bool = False,
    ) -> RetentionPolicy:
        if retention_days < 1:
            raise RetentionPolicyError("Retention must be strictly positive")
        if archive_after_days < 1 or archive_after_days > retention_days:
            raise RetentionPolicyError(
                "Archive delay must be positive and less or equal to retention"
            )
        stmt = select(AuditRetentionPolicyModel).where(
            AuditRetentionPolicyModel.organization_id == organization_id
        )
        model = session.execute(stmt).scalar_one_or_none()
        now = datetime.now(timezone.utc)
        if model is None:
            model = AuditRetentionPolicyModel(
                organization_id=organization_id,
                retention_days=retention_days,
                archive_after_days=archive_after_days,
                updated_at=now.replace(tzinfo=None),
            )
            session.add(model)
        else:
            model.retention_days = retention_days
            model.archive_after_days = archive_after_days
            model.updated_at = now.replace(tzinfo=None)
        session.flush()
        if commit:
            session.commit()
        self.log_event(
            session,
            event_type=AuditEventType.RETENTION_POLICY_UPDATED,
            module=AuditModule.RETENTION,
            action="policy.update",
            organization_id=organization_id,
            payload={
                "retention_days": retention_days,
                "archive_after_days": archive_after_days,
            },
        )
        return RetentionPolicy(
            organization_id=model.organization_id,
            retention_days=model.retention_days,
            archive_after_days=model.archive_after_days,
            updated_at=_ensure_timezone(model.updated_at),
        )

    def run_retention_job(
        self,
        session: Session,
        *,
        organization_id: str,
        reference_time: datetime | None = None,
        commit: bool = False,
    ) -> RetentionSummary:
        policy = self.get_retention_policy(session, organization_id)
        reference = _ensure_timezone(reference_time or datetime.now(timezone.utc))
        reference_naive = reference.replace(tzinfo=None)
        archive_before = reference - timedelta(days=policy.archive_after_days)
        purge_before = reference - timedelta(days=policy.retention_days)
        archive_cutoff = archive_before.replace(tzinfo=None)
        purge_cutoff = purge_before.replace(tzinfo=None)
        archived_count = 0
        stmt = select(AuditLogModel).where(
            AuditLogModel.organization_id == organization_id,
            AuditLogModel.created_at <= archive_cutoff,
            AuditLogModel.archived_at.is_(None),
        )
        for log in session.scalars(stmt):
            log.archived_at = reference_naive
            log.archive_reference = f"archive-{reference.strftime('%Y%m%d%H%M%S')}"
            archived_count += 1
        purge_stmt = (
            delete(AuditLogModel)
            .where(AuditLogModel.organization_id == organization_id)
            .where(AuditLogModel.created_at < purge_cutoff)
        )
        purge_result = session.execute(purge_stmt)
        purged_count = purge_result.rowcount or 0
        event_model = AuditRetentionEventModel(
            organization_id=organization_id,
            executed_at=reference_naive,
            purged_count=purged_count,
            archived_count=archived_count,
            anonymized_count=0,
            details={
                "archive_before": archive_before.isoformat(),
                "purge_before": purge_before.isoformat(),
            },
        )
        session.add(event_model)
        session.flush()
        summary = RetentionSummary(
            organization_id=organization_id,
            executed_at=reference,
            purged_count=purged_count,
            archived_count=archived_count,
            anonymized_count=0,
            details=event_model.details,
        )
        self.log_event(
            session,
            event_type=AuditEventType.RETENTION_EXECUTED,
            module=AuditModule.RETENTION,
            action="job.run",
            organization_id=organization_id,
            payload=summary.model_dump(),
        )
        if commit:
            session.commit()
        return summary

    # ------------------------------------------------------------------
    # GDPR workflows
    # ------------------------------------------------------------------
    def register_rgpd_request(
        self,
        session: Session,
        payload: RgpdRequestCreate,
        *,
        commit: bool = False,
    ) -> RgpdRequestRecord:
        org = payload.organization_id or self._default_org
        submitted_at = datetime.now(timezone.utc)
        due_at = submitted_at + timedelta(days=self._rgpd_sla_days)
        model = RgpdRequestModel(
            organization_id=org,
            request_type=payload.request_type.value,
            status=RgpdRequestStatus.PENDING.value,
            requester=payload.requester,
            subject_reference=payload.subject_reference,
            submitted_at=submitted_at.replace(tzinfo=None),
            due_at=due_at.replace(tzinfo=None),
        )
        session.add(model)
        session.flush()
        history = RgpdRequestHistoryModel(
            request_id=model.id,
            status=model.status,
            notes=payload.notes,
        )
        session.add(history)
        session.flush()
        record = RgpdRequestRecord(
            id=model.id,
            organization_id=model.organization_id,
            request_type=RgpdRequestType(model.request_type),
            status=RgpdRequestStatus(model.status),
            requester=model.requester,
            subject_reference=model.subject_reference,
            submitted_at=_ensure_timezone(model.submitted_at),
            due_at=_ensure_timezone(model.due_at),
            processed_at=None,
            completed_at=None,
            processor=None,
            resolution_notes=None,
        )
        self.log_event(
            session,
            event_type=AuditEventType.RGPD_REQUEST_REGISTERED,
            module=AuditModule.RGPD,
            action="request.created",
            organization_id=org,
            target_type="rgpd_request",
            target_id=str(model.id),
            payload=record.model_dump(),
        )
        if commit:
            session.commit()
        return record

    def complete_rgpd_request(
        self,
        session: Session,
        request_id: UUID,
        payload: RgpdRequestComplete,
        *,
        commit: bool = False,
    ) -> RgpdRequestRecord:
        model = session.get(RgpdRequestModel, request_id)
        if model is None:
            raise RgpdRequestNotFound(str(request_id))
        now = datetime.now(timezone.utc)
        model.status = RgpdRequestStatus.COMPLETED.value
        model.processed_at = now.replace(tzinfo=None)
        model.completed_at = now.replace(tzinfo=None)
        model.processor = payload.processor
        model.resolution_notes = payload.resolution_notes
        history = RgpdRequestHistoryModel(
            request_id=model.id,
            status=model.status,
            notes=payload.resolution_notes,
        )
        session.add(history)
        session.flush()
        record = RgpdRequestRecord(
            id=model.id,
            organization_id=model.organization_id,
            request_type=RgpdRequestType(model.request_type),
            status=RgpdRequestStatus(model.status),
            requester=model.requester,
            subject_reference=model.subject_reference,
            submitted_at=_ensure_timezone(model.submitted_at),
            due_at=_ensure_timezone(model.due_at),
            processed_at=_ensure_timezone(model.processed_at)
            if model.processed_at
            else None,
            completed_at=_ensure_timezone(model.completed_at)
            if model.completed_at
            else None,
            processor=model.processor,
            resolution_notes=model.resolution_notes,
        )
        self.log_event(
            session,
            event_type=AuditEventType.RGPD_REQUEST_COMPLETED,
            module=AuditModule.RGPD,
            action="request.completed",
            organization_id=model.organization_id,
            target_type="rgpd_request",
            target_id=str(model.id),
            payload=record.model_dump(),
        )
        if commit:
            session.commit()
        return record

    def list_rgpd_requests(
        self, session: Session, organization_id: str | None = None
    ) -> list[RgpdRequestRecord]:
        org = organization_id or self._default_org
        stmt = select(RgpdRequestModel).where(RgpdRequestModel.organization_id == org)
        results = []
        for model in session.scalars(stmt):
            results.append(
                RgpdRequestRecord(
                    id=model.id,
                    organization_id=model.organization_id,
                    request_type=RgpdRequestType(model.request_type),
                    status=RgpdRequestStatus(model.status),
                    requester=model.requester,
                    subject_reference=model.subject_reference,
                    submitted_at=_ensure_timezone(model.submitted_at),
                    due_at=_ensure_timezone(model.due_at),
                    processed_at=_ensure_timezone(model.processed_at)
                    if model.processed_at
                    else None,
                    completed_at=_ensure_timezone(model.completed_at)
                    if model.completed_at
                    else None,
                    processor=model.processor,
                    resolution_notes=model.resolution_notes,
                )
            )
        return results


__all__ = [
    "AuditError",
    "AuditEventType",
    "AuditExport",
    "AuditExportFormat",
    "AuditLogCollection",
    "AuditLogEntry",
    "AuditLogFilter",
    "AuditModule",
    "AuditTrailService",
    "RetentionPolicy",
    "RetentionPolicyError",
    "RetentionSummary",
    "RgpdRequestComplete",
    "RgpdRequestCreate",
    "RgpdRequestNotFound",
    "RgpdRequestRecord",
    "RgpdRequestStatus",
    "RgpdRequestType",
]
