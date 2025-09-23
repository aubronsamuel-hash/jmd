"""SQLAlchemy models representing persisted plannings."""

from __future__ import annotations

from datetime import date, datetime
from typing import List
from uuid import UUID, uuid4

from sqlalchemy import Date, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.types import Uuid

from backend.db import Base
from .artist import Artist, Availability


class Planning(Base):
    """Aggregate storing the generated planning."""

    __tablename__ = "plannings"

    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True, default=uuid4)
    event_date: Mapped[date] = mapped_column(Date, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=False),
        nullable=False,
        default=datetime.utcnow,
    )

    assignments: Mapped[List["PlanningAssignment"]] = relationship(
        back_populates="planning",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )


class PlanningAssignment(Base):
    """Link between a planning, an artist and an availability."""

    __tablename__ = "planning_assignments"

    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True, default=uuid4)
    planning_id: Mapped[UUID] = mapped_column(
        ForeignKey("plannings.id", ondelete="CASCADE"),
        nullable=False,
    )
    artist_id: Mapped[UUID] = mapped_column(
        ForeignKey("artists.id", ondelete="CASCADE"),
        nullable=False,
    )
    availability_id: Mapped[UUID] = mapped_column(
        ForeignKey("availabilities.id", ondelete="CASCADE"),
        nullable=False,
    )

    planning: Mapped[Planning] = relationship(back_populates="assignments")
    artist: Mapped[Artist] = relationship()
    availability: Mapped[Availability] = relationship()


__all__ = ["Planning", "PlanningAssignment"]
