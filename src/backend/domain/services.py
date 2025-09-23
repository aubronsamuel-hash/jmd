"""Domain services supporting planning persistence and retrieval."""

from __future__ import annotations

from datetime import date
from typing import Iterable, List
from uuid import UUID, uuid4

from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from backend.models import Artist as ArtistModel
from backend.models import Availability as AvailabilityModel
from backend.models import Planning as PlanningModel
from backend.models import PlanningAssignment as PlanningAssignmentModel

from .artists import Artist, ArtistCreate, ArtistUpdate, Availability
from .planning import PlanningAssignment, PlanningCreate, PlanningResponse


class ArtistError(Exception):
    """Base error for artist related operations."""


class ArtistNotFoundError(ArtistError):
    """Raised when attempting to access an artist that does not exist."""


class ArtistConflictError(ArtistError):
    """Raised when trying to create an artist with conflicting information."""


class PlanningError(Exception):
    """Raised when the planning cannot be generated from the provided payload."""


class PlanningNotFoundError(PlanningError):
    """Raised when attempting to access a planning that does not exist."""


def _to_artist_schema(artist: ArtistModel) -> Artist:
    """Map an ORM artist model to its API representation."""

    ordered_slots = sorted(artist.availabilities, key=lambda slot: slot.start)
    return Artist(
        id=artist.id,
        name=artist.name,
        availabilities=[
            Availability(start=slot.start, end=slot.end) for slot in ordered_slots
        ],
    )


def _load_artist(session: Session, artist_id: UUID) -> ArtistModel:
    """Load an artist along with its availabilities or raise if missing."""

    stmt = (
        select(ArtistModel)
        .options(joinedload(ArtistModel.availabilities))
        .where(ArtistModel.id == artist_id)
    )
    artist = session.execute(stmt).unique().scalar_one_or_none()
    if artist is None:
        raise ArtistNotFoundError(f"Artist {artist_id} not found")
    return artist


def _replace_availabilities(
    session: Session, artist: ArtistModel, availabilities: Iterable[Availability]
) -> None:
    """Replace the set of availabilities linked to an artist."""

    deduplicated = list({(slot.start, slot.end): slot for slot in availabilities}.values())
    artist.availabilities.clear()
    session.flush()

    for slot in deduplicated:
        artist.availabilities.append(
            AvailabilityModel(start=slot.start, end=slot.end)
        )
    session.flush()


def _select_slot_for_artist(artist: Artist, event_date: date) -> Availability | None:
    """Return the first availability of the artist matching the requested date."""

    matching_slots: List[Availability] = [
        slot for slot in sorted(artist.availabilities, key=lambda item: item.start)
        if slot.start.date() == event_date
    ]
    if not matching_slots:
        return None
    return matching_slots[0]


def _upsert_artist(session: Session, artist_schema: Artist) -> ArtistModel:
    """Ensure the artist exists in the database and return its model instance."""

    artist = session.get(ArtistModel, artist_schema.id)
    if artist is None:
        artist = ArtistModel(id=artist_schema.id, name=artist_schema.name)
        session.add(artist)
    else:
        artist.name = artist_schema.name
    return artist


def _sync_availabilities(
    session: Session, artist: ArtistModel, availabilities: Iterable[Availability]
) -> None:
    """Persist availability slots if they are missing for the artist."""

    existing = {(slot.start, slot.end): slot for slot in artist.availabilities}
    for availability_schema in availabilities:
        key = (availability_schema.start, availability_schema.end)
        if key in existing:
            continue
        artist.availabilities.append(
            AvailabilityModel(start=availability_schema.start, end=availability_schema.end)
        )
    session.flush()


def _find_availability(
    session: Session, artist_id: UUID, slot: Availability
) -> AvailabilityModel:
    """Retrieve the persisted availability matching the provided slot."""

    stmt = select(AvailabilityModel).where(
        AvailabilityModel.artist_id == artist_id,
        AvailabilityModel.start == slot.start,
        AvailabilityModel.end == slot.end,
    )
    availability = session.execute(stmt).scalar_one_or_none()
    if availability is None:
        availability = AvailabilityModel(
            artist_id=artist_id, start=slot.start, end=slot.end
        )
        session.add(availability)
        session.flush()
    return availability


def create_artist(session: Session, payload: ArtistCreate) -> Artist:
    """Persist a new artist and return its representation."""

    artist_id = payload.id or uuid4()
    if session.get(ArtistModel, artist_id) is not None:
        raise ArtistConflictError(f"Artist {artist_id} already exists")

    artist = ArtistModel(id=artist_id, name=payload.name)
    session.add(artist)
    session.flush()
    _replace_availabilities(session, artist, payload.availabilities)
    session.commit()
    loaded = _load_artist(session, artist_id)
    return _to_artist_schema(loaded)


def list_artists(session: Session) -> List[Artist]:
    """Return the collection of persisted artists ordered by name."""

    stmt = select(ArtistModel).options(joinedload(ArtistModel.availabilities)).order_by(
        ArtistModel.name
    )
    artists = session.execute(stmt).unique().scalars().all()
    return [_to_artist_schema(artist) for artist in artists]


def get_artist(session: Session, artist_id: UUID) -> Artist:
    """Return a single artist from its identifier."""

    artist = _load_artist(session, artist_id)
    return _to_artist_schema(artist)


def update_artist(session: Session, artist_id: UUID, payload: ArtistUpdate) -> Artist:
    """Update an existing artist and return the refreshed representation."""

    artist = _load_artist(session, artist_id)
    artist.name = payload.name
    _replace_availabilities(session, artist, payload.availabilities)
    session.commit()
    refreshed = _load_artist(session, artist_id)
    return _to_artist_schema(refreshed)


def delete_artist(session: Session, artist_id: UUID) -> None:
    """Delete an artist and its availabilities from persistence."""

    artist = session.get(ArtistModel, artist_id)
    if artist is None:
        raise ArtistNotFoundError(f"Artist {artist_id} not found")
    session.delete(artist)
    session.commit()


def _load_planning(session: Session, planning_id: UUID) -> PlanningModel:
    """Load a planning with assignments and availability slots eagerly."""

    stmt = (
        select(PlanningModel)
        .options(
            joinedload(PlanningModel.assignments).joinedload(
                PlanningAssignmentModel.availability
            )
        )
        .where(PlanningModel.id == planning_id)
    )
    planning = session.execute(stmt).unique().scalar_one_or_none()
    if planning is None:
        raise PlanningNotFoundError(f"Planning {planning_id} not found")
    return planning


def _to_planning_response(planning: PlanningModel) -> PlanningResponse:
    """Map a planning ORM model back to its API schema representation."""

    ordered_assignments = sorted(
        planning.assignments,
        key=lambda item: (item.availability.start, item.artist_id),
    )
    api_assignments = [
        PlanningAssignment(
            artist_id=assignment.artist_id,
            slot=Availability(
                start=assignment.availability.start,
                end=assignment.availability.end,
            ),
        )
        for assignment in ordered_assignments
    ]
    return PlanningResponse(
        planning_id=planning.id,
        event_date=planning.event_date,
        assignments=api_assignments,
    )


def create_planning(session: Session, payload: PlanningCreate) -> PlanningResponse:
    """Generate and persist a planning for the provided payload."""

    assignments: List[PlanningAssignment] = []
    for artist_schema in payload.artists:
        slot = _select_slot_for_artist(artist_schema, payload.event_date)
        if slot is None:
            raise PlanningError(
                f"Artist '{artist_schema.name}' has no availability for "
                f"{payload.event_date.isoformat()}"
            )
        assignments.append(PlanningAssignment(artist_id=artist_schema.id, slot=slot))

    for artist_schema in payload.artists:
        artist_model = _upsert_artist(session, artist_schema)
        _sync_availabilities(session, artist_model, artist_schema.availabilities)

    planning_model = PlanningModel(id=uuid4(), event_date=payload.event_date)
    session.add(planning_model)
    session.flush()

    for assignment in assignments:
        availability_model = _find_availability(session, assignment.artist_id, assignment.slot)
        planning_model.assignments.append(
            PlanningAssignmentModel(
                artist_id=assignment.artist_id,
                availability_id=availability_model.id,
            )
        )

    session.commit()
    persisted = _load_planning(session, planning_model.id)
    return _to_planning_response(persisted)


def list_plannings(session: Session) -> List[PlanningResponse]:
    """Return all persisted plannings ordered by creation date descending."""

    stmt = (
        select(PlanningModel)
        .options(
            joinedload(PlanningModel.assignments).joinedload(
                PlanningAssignmentModel.availability
            )
        )
        .order_by(PlanningModel.created_at.desc())
    )
    plannings = session.execute(stmt).unique().scalars().all()
    return [_to_planning_response(planning) for planning in plannings]


def get_planning(session: Session, planning_id: UUID) -> PlanningResponse:
    """Return a single planning from its identifier."""

    planning = _load_planning(session, planning_id)
    return _to_planning_response(planning)


__all__ = [
    "ArtistError",
    "ArtistNotFoundError",
    "ArtistConflictError",
    "create_artist",
    "list_artists",
    "get_artist",
    "update_artist",
    "delete_artist",
    "PlanningError",
    "PlanningNotFoundError",
    "create_planning",
    "list_plannings",
    "get_planning",
]
