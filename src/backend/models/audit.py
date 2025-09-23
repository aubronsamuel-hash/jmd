"""ORM models supporting audit trail and compliance workflows."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any
from uuid import UUID, uuid4

from sqlalchemy import CheckConstraint, DateTime, ForeignKey, Integer, String
from sqlalchemy.dialects.sqlite import JSON as SQLiteJSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.types import JSON, Uuid

from backend.db import Base


def _json_type() -> type[JSON[Any]]:
    """Return a JSON type compatible with SQLite and PostgreSQL."""

    # SQLAlchemy automatically maps JSON to SQLite's JSON type when available,
    # but typing helpers ease static analysis by providing an explicit factory.
    return JSON().with_variant(SQLiteJSON(), "sqlite")  # type: ignore[return-value]


class AuditLog(Base):
    """Immutable journal entry capturing a sensitive event."""

    __tablename__ = "audit_logs"

    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True, default=uuid4)
    organization_id: Mapped[str] = mapped_column(String(length=64), nullable=False)
    module: Mapped[str] = mapped_column(String(length=64), nullable=False)
    event_type: Mapped[str] = mapped_column(String(length=128), nullable=False)
    action: Mapped[str] = mapped_column(String(length=64), nullable=False)
    actor_type: Mapped[str | None] = mapped_column(String(length=64), nullable=True)
    actor_id: Mapped[str | None] = mapped_column(String(length=128), nullable=True)
    target_type: Mapped[str | None] = mapped_column(String(length=64), nullable=True)
    target_id: Mapped[str | None] = mapped_column(String(length=128), nullable=True)
    payload_version: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    payload: Mapped[dict[str, Any]] = mapped_column(
        _json_type(), nullable=False, default=dict
    )
    signature: Mapped[str] = mapped_column(String(length=128), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc).replace(tzinfo=None),
    )
    archived_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    archive_reference: Mapped[str | None] = mapped_column(String(length=255), nullable=True)


class AuditRetentionPolicy(Base):
    """Retention and archiving configuration per organization."""

    __tablename__ = "audit_retention_policies"
    __table_args__ = (
        CheckConstraint("retention_days > 0", name="ck_audit_retention_positive"),
        CheckConstraint(
            "archive_after_days > 0",
            name="ck_audit_retention_archive_positive",
        ),
        CheckConstraint(
            "retention_days >= archive_after_days",
            name="ck_audit_retention_windows",
        ),
    )

    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True, default=uuid4)
    organization_id: Mapped[str] = mapped_column(
        String(length=64), nullable=False, unique=True
    )
    retention_days: Mapped[int] = mapped_column(Integer, nullable=False)
    archive_after_days: Mapped[int] = mapped_column(Integer, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc).replace(tzinfo=None),
    )


class AuditRetentionEvent(Base):
    """Execution trace for a retention or purge job."""

    __tablename__ = "audit_retention_events"

    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True, default=uuid4)
    organization_id: Mapped[str] = mapped_column(String(length=64), nullable=False)
    executed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc).replace(tzinfo=None),
    )
    purged_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    archived_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    anonymized_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    details: Mapped[dict[str, Any]] = mapped_column(
        _json_type(), nullable=False, default=dict
    )


class RgpdRequest(Base):
    """Register of GDPR data subject requests."""

    __tablename__ = "rgpd_requests"

    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True, default=uuid4)
    organization_id: Mapped[str] = mapped_column(String(length=64), nullable=False)
    request_type: Mapped[str] = mapped_column(String(length=32), nullable=False)
    status: Mapped[str] = mapped_column(String(length=32), nullable=False)
    requester: Mapped[str] = mapped_column(String(length=128), nullable=False)
    subject_reference: Mapped[str] = mapped_column(String(length=128), nullable=False)
    submitted_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc).replace(tzinfo=None),
    )
    due_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    processed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    completed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    processor: Mapped[str | None] = mapped_column(String(length=128), nullable=True)
    resolution_notes: Mapped[str | None] = mapped_column(String(length=512), nullable=True)
    history: Mapped[list["RgpdRequestHistory"]] = relationship(
        back_populates="request", cascade="all, delete-orphan"
    )


class RgpdRequestHistory(Base):
    """Detailed timeline for GDPR request state transitions."""

    __tablename__ = "rgpd_request_history"

    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True, default=uuid4)
    request_id: Mapped[UUID] = mapped_column(
        ForeignKey("rgpd_requests.id", ondelete="CASCADE"), nullable=False
    )
    status: Mapped[str] = mapped_column(String(length=32), nullable=False)
    changed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc).replace(tzinfo=None),
    )
    notes: Mapped[str | None] = mapped_column(String(length=512), nullable=True)

    request: Mapped[RgpdRequest] = relationship(back_populates="history")


__all__ = [
    "AuditLog",
    "AuditRetentionEvent",
    "AuditRetentionPolicy",
    "RgpdRequest",
    "RgpdRequestHistory",
]
