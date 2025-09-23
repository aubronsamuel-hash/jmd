"""Domain services supporting planning creation."""

from __future__ import annotations

from datetime import date
from typing import List
from uuid import uuid4

from .artists import Artist, Availability
from .planning import PlanningAssignment, PlanningCreate, PlanningResponse


class PlanningError(Exception):
    """Raised when the planning cannot be generated from the provided payload."""


def _select_slot_for_artist(artist: Artist, event_date: date) -> Availability | None:
    """Return the first availability of the artist matching the requested date."""

    matching_slots: List[Availability] = [
        slot for slot in sorted(artist.availabilities, key=lambda item: item.start)
        if slot.start.date() == event_date
    ]
    if not matching_slots:
        return None
    return matching_slots[0]


def create_planning(payload: PlanningCreate) -> PlanningResponse:
    """Generate a planning by selecting the earliest slot for each artist."""

    assignments: List[PlanningAssignment] = []
    for artist in payload.artists:
        slot = _select_slot_for_artist(artist, payload.event_date)
        if slot is None:
            raise PlanningError(
                f"Artist '{artist.name}' has no availability for {payload.event_date.isoformat()}"
            )
        assignments.append(PlanningAssignment(artist_id=artist.id, slot=slot))

    return PlanningResponse(
        planning_id=uuid4(),
        event_date=payload.event_date,
        assignments=assignments,
    )


__all__ = ["PlanningError", "create_planning"]
