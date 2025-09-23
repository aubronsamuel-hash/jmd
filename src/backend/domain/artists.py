"""Pydantic schemas describing artists and their availabilities."""

from __future__ import annotations

from datetime import datetime
from typing import List
from uuid import UUID, uuid4

from pydantic import BaseModel, ConfigDict, Field, model_validator


class Availability(BaseModel):
    """Time slot during which an artist is available."""

    model_config = ConfigDict(extra="forbid")

    start: datetime = Field(..., description="Start datetime of the availability window")
    end: datetime = Field(..., description="End datetime of the availability window")

    @model_validator(mode="after")
    def validate_time_window(self) -> "Availability":
        """Ensure the availability slot has a positive duration."""

        if self.end <= self.start:
            raise ValueError("Availability end must be after start")
        return self


class Artist(BaseModel):
    """Basic artist information along with declared availabilities."""

    model_config = ConfigDict(extra="forbid")

    id: UUID = Field(default_factory=uuid4, description="Unique identifier of the artist")
    name: str = Field(..., min_length=1, description="Public name of the artist")
    availabilities: List[Availability] = Field(
        default_factory=list,
        description="Declared availabilities for the artist",
    )


class ArtistCreate(BaseModel):
    """Payload used to create a new artist."""

    model_config = ConfigDict(extra="forbid")

    name: str = Field(..., min_length=1, description="Public name of the artist")
    availabilities: List[Availability] = Field(
        default_factory=list,
        description="Declared availabilities for the artist",
    )
    id: UUID | None = Field(
        default=None,
        description="Optional identifier for the artist. Generated when omitted.",
    )


class ArtistUpdate(BaseModel):
    """Payload used to update an existing artist."""

    model_config = ConfigDict(extra="forbid")

    name: str = Field(..., min_length=1, description="Public name of the artist")
    availabilities: List[Availability] = Field(
        default_factory=list,
        description="Declared availabilities for the artist",
    )


__all__ = ["Artist", "Availability", "ArtistCreate", "ArtistUpdate"]
