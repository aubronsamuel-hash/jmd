"""SQLAlchemy models storing analytics warehouse events."""

from __future__ import annotations

from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import DateTime, ForeignKey, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.types import Uuid

from backend.db import Base


class AnalyticsMissionEvent(Base):
    """Fact table capturing mission level planning validations."""

    __tablename__ = "analytics_mission_events"

    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True, default=uuid4)
    mission_code: Mapped[str] = mapped_column(String(64), nullable=False)
    project_code: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    location_code: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    team_name: Mapped[str] = mapped_column(String(128), nullable=False, index=True)
    start_time: Mapped[datetime] = mapped_column(DateTime(timezone=False), nullable=False, index=True)
    end_time: Mapped[datetime] = mapped_column(DateTime(timezone=False), nullable=False)
    actual_start_time: Mapped[datetime | None] = mapped_column(DateTime(timezone=False), nullable=True)
    actual_end_time: Mapped[datetime | None] = mapped_column(DateTime(timezone=False), nullable=True)
    actual_hours: Mapped[float | None] = mapped_column(Numeric(10, 2), nullable=True)
    status: Mapped[str] = mapped_column(String(32), nullable=False, default="validated")
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=False),
        nullable=False,
        default=datetime.utcnow,
        index=True,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=False), nullable=False, default=datetime.utcnow
    )

    payroll_records: Mapped[list["AnalyticsPayrollRecord"]] = relationship(
        back_populates="mission_event",
        cascade="all, delete-orphan",
    )
    equipment_incidents: Mapped[list["AnalyticsEquipmentIncident"]] = relationship(
        back_populates="mission_event",
        cascade="all, delete-orphan",
    )


class AnalyticsPayrollRecord(Base):
    """Payroll amounts linked to mission events for cost analytics."""

    __tablename__ = "analytics_payroll_records"

    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True, default=uuid4)
    mission_event_id: Mapped[UUID] = mapped_column(
        ForeignKey("analytics_mission_events.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    amount: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False)
    currency: Mapped[str] = mapped_column(String(8), nullable=False, default="EUR")
    recorded_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=False), nullable=False, default=datetime.utcnow, index=True
    )
    source: Mapped[str] = mapped_column(String(64), nullable=False, default="import")

    mission_event: Mapped[AnalyticsMissionEvent] = relationship(
        back_populates="payroll_records"
    )


class AnalyticsEquipmentIncident(Base):
    """Equipment incidents captured for the logistics dashboard."""

    __tablename__ = "analytics_equipment_incidents"

    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True, default=uuid4)
    mission_event_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("analytics_mission_events.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    project_code: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    location_code: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    team_name: Mapped[str] = mapped_column(String(128), nullable=False, index=True)
    occurred_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=False), nullable=False, index=True
    )
    severity: Mapped[str] = mapped_column(String(16), nullable=False, default="medium")
    description: Mapped[str | None] = mapped_column(String(255), nullable=True)

    mission_event: Mapped[AnalyticsMissionEvent | None] = relationship(
        back_populates="equipment_incidents"
    )


__all__ = [
    "AnalyticsMissionEvent",
    "AnalyticsPayrollRecord",
    "AnalyticsEquipmentIncident",
]
