"""Schemas dedicated to the planning workflow."""

from __future__ import annotations

from datetime import date
from typing import List
from uuid import UUID, uuid4

from pydantic import BaseModel, ConfigDict, Field

from .artists import Artist, Availability


class PlanningAssignment(BaseModel):
    """Assignment of an artist to a concrete availability slot."""

    model_config = ConfigDict(extra="forbid")

    artist_id: UUID = Field(..., description="Identifier of the artist assigned to the slot")
    slot: Availability = Field(..., description="Selected availability slot")


class PlanningCreate(BaseModel):
    """Request payload used when creating a planning."""

    model_config = ConfigDict(extra="forbid")

    event_date: date = Field(..., description="Target date for the planning")
    artists: List[Artist] = Field(..., description="Artists to consider for the planning")


class PlanningResponse(BaseModel):
    """Representation of a generated planning."""

    model_config = ConfigDict(extra="forbid")

    planning_id: UUID = Field(default_factory=uuid4, description="Identifier of the planning instance")
    event_date: date = Field(..., description="Date targeted by the planning")
    assignments: List[PlanningAssignment] = Field(
        default_factory=list,
        description="Assignments generated for the planning",
    )


__all__ = ["PlanningAssignment", "PlanningCreate", "PlanningResponse"]
