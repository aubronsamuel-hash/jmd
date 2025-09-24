from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from ..models import MissionTag
from ..rbac import Permission
from ..schemas import MissionTagCreate, MissionTagUpdate
from .access import ensure_permission, resolve_context
from .exceptions import DomainError


def _normalise_slug(value: str) -> str:
    return "-".join(part for part in value.strip().lower().replace("_", "-").split() if part)


def _normalise_label(value: str) -> str:
    return value.strip()


def _get_tag_for_org(session: Session, organization_id: str, tag_id: str) -> MissionTag:
    tag = session.get(MissionTag, tag_id)
    if tag is None or tag.organization_id != organization_id:
        raise DomainError("Tag not found", status_code=404)
    return tag


def create_tag(session: Session, token_value: str, payload: MissionTagCreate) -> MissionTag:
    context = resolve_context(session, token_value)
    ensure_permission(context, Permission.MANAGE_MISSION_TAGS)

    slug = _normalise_slug(payload.slug)
    if not slug:
        raise DomainError("Tag slug cannot be empty", status_code=422)

    label = _normalise_label(payload.label)
    if not label:
        raise DomainError("Tag label cannot be empty", status_code=422)

    existing = session.scalar(
        select(MissionTag)
        .where(MissionTag.organization_id == context.membership.organization_id)
        .where(MissionTag.slug == slug)
    )
    if existing:
        raise DomainError("Tag with this slug already exists", status_code=409)

    tag = MissionTag(
        organization_id=context.membership.organization_id,
        slug=slug,
        label=label,
    )
    session.add(tag)
    session.flush()
    session.commit()
    session.refresh(tag)
    return tag


def list_tags(session: Session, token_value: str) -> list[MissionTag]:
    context = resolve_context(session, token_value)
    ensure_permission(context, Permission.VIEW_MISSION_TAGS)

    result = session.scalars(
        select(MissionTag)
        .where(MissionTag.organization_id == context.membership.organization_id)
        .order_by(MissionTag.slug)
    )
    return list(result)


def get_tag(session: Session, token_value: str, tag_id: str) -> MissionTag:
    context = resolve_context(session, token_value)
    ensure_permission(context, Permission.VIEW_MISSION_TAGS)
    return _get_tag_for_org(session, context.membership.organization_id, tag_id)


def update_tag(session: Session, token_value: str, tag_id: str, payload: MissionTagUpdate) -> MissionTag:
    context = resolve_context(session, token_value)
    ensure_permission(context, Permission.MANAGE_MISSION_TAGS)

    tag = _get_tag_for_org(session, context.membership.organization_id, tag_id)
    data = payload.model_dump(exclude_unset=True)

    if "slug" in data:
        slug = _normalise_slug(data["slug"])
        if not slug:
            raise DomainError("Tag slug cannot be empty", status_code=422)
        duplicate = session.scalar(
            select(MissionTag)
            .where(MissionTag.organization_id == context.membership.organization_id)
            .where(MissionTag.slug == slug)
            .where(MissionTag.id != tag.id)
        )
        if duplicate:
            raise DomainError("Tag with this slug already exists", status_code=409)
        tag.slug = slug

    if "label" in data:
        label = _normalise_label(data["label"])
        if not label:
            raise DomainError("Tag label cannot be empty", status_code=422)
        tag.label = label

    session.add(tag)
    session.commit()
    session.refresh(tag)
    return tag


def delete_tag(session: Session, token_value: str, tag_id: str) -> None:
    context = resolve_context(session, token_value)
    ensure_permission(context, Permission.MANAGE_MISSION_TAGS)

    tag = _get_tag_for_org(session, context.membership.organization_id, tag_id)
    session.delete(tag)
    session.commit()
