from __future__ import annotations

from datetime import time

from sqlalchemy import select
from sqlalchemy.orm import Session

from ..models import MissionTag, MissionTemplate, Venue
from ..rbac import Permission
from ..schemas import MissionTemplateCreate, MissionTemplateUpdate
from .access import ensure_permission, resolve_context
from .exceptions import DomainError


def _normalise_name(value: str) -> str:
    return value.strip()


def _get_template_for_org(session: Session, organization_id: str, template_id: str) -> MissionTemplate:
    template = session.get(MissionTemplate, template_id)
    if template is None or template.organization_id != organization_id:
        raise DomainError("Mission template not found", status_code=404)
    return template


def _load_default_venue(session: Session, organization_id: str, venue_id: str | None) -> Venue | None:
    if venue_id is None:
        return None
    venue = session.get(Venue, venue_id)
    if venue is None or venue.organization_id != organization_id:
        raise DomainError("Venue not found", status_code=404)
    return venue


def _load_tags(session: Session, organization_id: str, tag_ids: list[str]) -> list[MissionTag]:
    if not tag_ids:
        return []
    tags = session.scalars(
        select(MissionTag)
        .where(MissionTag.organization_id == organization_id)
        .where(MissionTag.id.in_(tag_ids))
    )
    resolved = {tag.id: tag for tag in tags}
    missing = [tag_id for tag_id in tag_ids if tag_id not in resolved]
    if missing:
        raise DomainError("Tag not found", status_code=404)
    return [resolved[tag_id] for tag_id in tag_ids]


def _validate_times(start: time | None, end: time | None) -> None:
    if start and end and end <= start:
        raise DomainError("End time must be after start time", status_code=422)


def _validate_team_size(value: int) -> None:
    if value < 1:
        raise DomainError("Team size must be at least 1", status_code=422)


def create_template(session: Session, token_value: str, payload: MissionTemplateCreate) -> MissionTemplate:
    context = resolve_context(session, token_value)
    ensure_permission(context, Permission.MANAGE_MISSION_TEMPLATES)

    name = _normalise_name(payload.name)
    if not name:
        raise DomainError("Mission template name cannot be empty", status_code=422)

    existing = session.scalar(
        select(MissionTemplate)
        .where(MissionTemplate.organization_id == context.membership.organization_id)
        .where(MissionTemplate.name == name)
    )
    if existing:
        raise DomainError("Mission template with this name already exists", status_code=409)

    _validate_team_size(payload.team_size)
    _validate_times(payload.default_start_time, payload.default_end_time)

    default_venue = _load_default_venue(
        session, context.membership.organization_id, payload.default_venue_id
    )
    tags = _load_tags(session, context.membership.organization_id, payload.tag_ids)

    template = MissionTemplate(
        organization_id=context.membership.organization_id,
        name=name,
        description=payload.description,
        team_size=payload.team_size,
        required_skills=payload.required_skills,
        default_start_time=payload.default_start_time,
        default_end_time=payload.default_end_time,
    )
    template.default_venue = default_venue
    template.tags = tags

    session.add(template)
    session.flush()
    session.commit()
    session.refresh(template)
    return template


def list_templates(session: Session, token_value: str) -> list[MissionTemplate]:
    context = resolve_context(session, token_value)
    ensure_permission(context, Permission.VIEW_MISSION_TEMPLATES)

    result = session.scalars(
        select(MissionTemplate)
        .where(MissionTemplate.organization_id == context.membership.organization_id)
        .order_by(MissionTemplate.name)
    )
    return list(result)


def get_template(session: Session, token_value: str, template_id: str) -> MissionTemplate:
    context = resolve_context(session, token_value)
    ensure_permission(context, Permission.VIEW_MISSION_TEMPLATES)
    return _get_template_for_org(session, context.membership.organization_id, template_id)


def update_template(
    session: Session,
    token_value: str,
    template_id: str,
    payload: MissionTemplateUpdate,
) -> MissionTemplate:
    context = resolve_context(session, token_value)
    ensure_permission(context, Permission.MANAGE_MISSION_TEMPLATES)

    template = _get_template_for_org(session, context.membership.organization_id, template_id)
    data = payload.model_dump(exclude_unset=True)

    if "name" in data:
        name = _normalise_name(data["name"])
        if not name:
            raise DomainError("Mission template name cannot be empty", status_code=422)
        duplicate = session.scalar(
            select(MissionTemplate)
            .where(MissionTemplate.organization_id == context.membership.organization_id)
            .where(MissionTemplate.name == name)
            .where(MissionTemplate.id != template.id)
        )
        if duplicate:
            raise DomainError("Mission template with this name already exists", status_code=409)
        template.name = name

    if "team_size" in data:
        _validate_team_size(data["team_size"])
        template.team_size = data["team_size"]

    start_time = data.get("default_start_time", template.default_start_time)
    end_time = data.get("default_end_time", template.default_end_time)
    _validate_times(start_time, end_time)

    if "default_start_time" in data:
        template.default_start_time = data["default_start_time"]
    if "default_end_time" in data:
        template.default_end_time = data["default_end_time"]

    if "default_venue_id" in data:
        template.default_venue = _load_default_venue(
            session, context.membership.organization_id, data["default_venue_id"]
        )

    if "tag_ids" in data:
        template.tags = _load_tags(
            session, context.membership.organization_id, data["tag_ids"]
        )

    for field in ["description", "required_skills"]:
        if field in data:
            setattr(template, field, data[field])

    session.add(template)
    session.commit()
    session.refresh(template)
    return template


def delete_template(session: Session, token_value: str, template_id: str) -> None:
    context = resolve_context(session, token_value)
    ensure_permission(context, Permission.MANAGE_MISSION_TEMPLATES)

    template = _get_template_for_org(session, context.membership.organization_id, template_id)
    session.delete(template)
    session.commit()
