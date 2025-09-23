"""SQLAlchemy models describing artists and their availabilities."""

from __future__ import annotations

from datetime import datetime
from typing import List
from uuid import UUID, uuid4

from sqlalchemy import DateTime, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.types import Uuid

from backend.db import Base


class Artist(Base):
    """Persistent representation of an artist."""

    __tablename__ = "artists"

    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True, default=uuid4)
    name: Mapped[str] = mapped_column(String(length=255), nullable=False)

    availabilities: Mapped[List["Availability"]] = relationship(
        back_populates="artist",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )


class Availability(Base):
    """Availability slot linked to an artist."""

    __tablename__ = "availabilities"

    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True, default=uuid4)
    artist_id: Mapped[UUID] = mapped_column(
        ForeignKey("artists.id", ondelete="CASCADE"),
        nullable=False,
    )
    start: Mapped[datetime] = mapped_column(DateTime(timezone=False), nullable=False)
    end: Mapped[datetime] = mapped_column(DateTime(timezone=False), nullable=False)

    artist: Mapped[Artist] = relationship(back_populates="availabilities")


__all__ = ["Artist", "Availability"]
