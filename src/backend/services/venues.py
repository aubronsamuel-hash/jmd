from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from ..models import Venue
from ..rbac import Permission
from ..schemas import VenueCreate, VenueUpdate
from .access import ensure_permission, resolve_context
from .exceptions import DomainError


def _normalise_name(value: str) -> str:
    return value.strip()


def _get_venue_for_org(session: Session, organization_id: str, venue_id: str) -> Venue:
    venue = session.get(Venue, venue_id)
    if venue is None or venue.organization_id != organization_id:
        raise DomainError("Venue not found", status_code=404)
    return venue


def create_venue(session: Session, token_value: str, payload: VenueCreate) -> Venue:
    context = resolve_context(session, token_value)
    ensure_permission(context, Permission.MANAGE_VENUES)

    name = _normalise_name(payload.name)
    if not name:
        raise DomainError("Venue name cannot be empty", status_code=422)

    existing = session.scalar(
        select(Venue)
        .where(Venue.organization_id == context.membership.organization_id)
        .where(Venue.name == name)
    )
    if existing:
        raise DomainError("Venue with this name already exists", status_code=409)

    venue = Venue(
        organization_id=context.membership.organization_id,
        name=name,
        address=payload.address,
        city=payload.city,
        country=payload.country,
        postal_code=payload.postal_code,
        capacity=payload.capacity,
        notes=payload.notes,
    )
    session.add(venue)
    session.flush()
    session.commit()
    session.refresh(venue)
    return venue


def list_venues(session: Session, token_value: str) -> list[Venue]:
    context = resolve_context(session, token_value)
    ensure_permission(context, Permission.VIEW_VENUES)

    result = session.scalars(
        select(Venue)
        .where(Venue.organization_id == context.membership.organization_id)
        .order_by(Venue.name)
    )
    return list(result)


def get_venue(session: Session, token_value: str, venue_id: str) -> Venue:
    context = resolve_context(session, token_value)
    ensure_permission(context, Permission.VIEW_VENUES)
    return _get_venue_for_org(session, context.membership.organization_id, venue_id)


def update_venue(session: Session, token_value: str, venue_id: str, payload: VenueUpdate) -> Venue:
    context = resolve_context(session, token_value)
    ensure_permission(context, Permission.MANAGE_VENUES)

    venue = _get_venue_for_org(session, context.membership.organization_id, venue_id)
    data = payload.model_dump(exclude_unset=True)

    if "name" in data:
        name = _normalise_name(data["name"])
        if not name:
            raise DomainError("Venue name cannot be empty", status_code=422)
        duplicate = session.scalar(
            select(Venue)
            .where(Venue.organization_id == context.membership.organization_id)
            .where(Venue.name == name)
            .where(Venue.id != venue.id)
        )
        if duplicate:
            raise DomainError("Venue with this name already exists", status_code=409)
        venue.name = name

    for field in ["address", "city", "country", "postal_code", "capacity", "notes"]:
        if field in data:
            setattr(venue, field, data[field])

    session.add(venue)
    session.commit()
    session.refresh(venue)
    return venue


def delete_venue(session: Session, token_value: str, venue_id: str) -> None:
    context = resolve_context(session, token_value)
    ensure_permission(context, Permission.MANAGE_VENUES)

    venue = _get_venue_for_org(session, context.membership.organization_id, venue_id)
    session.delete(venue)
    session.commit()
