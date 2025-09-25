from __future__ import annotations

from datetime import date

from sqlalchemy import select
from sqlalchemy.orm import Session

from ..models import Project, Venue
from ..rbac import Permission
from ..schemas import ProjectCreate, ProjectUpdate
from .access import ensure_permission, resolve_context
from .exceptions import DomainError


def _normalise_name(value: str) -> str:
    return value.strip()


def _get_project_for_org(session: Session, organization_id: str, project_id: str) -> Project:
    project = session.get(Project, project_id)
    if project is None or project.organization_id != organization_id:
        raise DomainError("Project not found", status_code=404)
    return project


def _load_venues(session: Session, organization_id: str, venue_ids: list[str]) -> list[Venue]:
    if not venue_ids:
        return []
    venues = session.scalars(
        select(Venue)
        .where(Venue.organization_id == organization_id)
        .where(Venue.id.in_(venue_ids))
    )
    resolved = {venue.id: venue for venue in venues}
    missing = [venue_id for venue_id in venue_ids if venue_id not in resolved]
    if missing:
        raise DomainError("Venue not found", status_code=404)
    return [resolved[venue_id] for venue_id in venue_ids]


def _validate_dates(start: date | None, end: date | None) -> None:
    if start and end and end < start:
        raise DomainError("Project end date cannot be before start date", status_code=422)


def _validate_budget(value: int | None) -> None:
    if value is not None and value < 0:
        raise DomainError("Budget must be greater than or equal to zero", status_code=422)


def create_project(session: Session, token_value: str, payload: ProjectCreate) -> Project:
    context = resolve_context(session, token_value)
    ensure_permission(context, Permission.MANAGE_PROJECTS)

    name = _normalise_name(payload.name)
    if not name:
        raise DomainError("Project name cannot be empty", status_code=422)

    existing = session.scalar(
        select(Project)
        .where(Project.organization_id == context.membership.organization_id)
        .where(Project.name == name)
    )
    if existing:
        raise DomainError("Project with this name already exists", status_code=409)

    _validate_dates(payload.start_date, payload.end_date)
    _validate_budget(payload.budget_cents)

    venues = _load_venues(session, context.membership.organization_id, payload.venue_ids)

    project = Project(
        organization_id=context.membership.organization_id,
        name=name,
        description=payload.description,
        start_date=payload.start_date,
        end_date=payload.end_date,
        budget_cents=payload.budget_cents,
        team_type=payload.team_type,
    )
    project.venues = venues

    session.add(project)
    session.flush()
    session.commit()
    session.refresh(project)
    return project


def list_projects(session: Session, token_value: str) -> list[Project]:
    context = resolve_context(session, token_value)
    ensure_permission(context, Permission.VIEW_PROJECTS)

    result = session.scalars(
        select(Project)
        .where(Project.organization_id == context.membership.organization_id)
        .order_by(Project.created_at)
    )
    return list(result)


def get_project(session: Session, token_value: str, project_id: str) -> Project:
    context = resolve_context(session, token_value)
    ensure_permission(context, Permission.VIEW_PROJECTS)
    return _get_project_for_org(session, context.membership.organization_id, project_id)


def update_project(session: Session, token_value: str, project_id: str, payload: ProjectUpdate) -> Project:
    context = resolve_context(session, token_value)
    ensure_permission(context, Permission.MANAGE_PROJECTS)

    project = _get_project_for_org(session, context.membership.organization_id, project_id)
    data = payload.model_dump(exclude_unset=True)

    if "name" in data:
        name = _normalise_name(data["name"])
        if not name:
            raise DomainError("Project name cannot be empty", status_code=422)
        duplicate = session.scalar(
            select(Project)
            .where(Project.organization_id == context.membership.organization_id)
            .where(Project.name == name)
            .where(Project.id != project.id)
        )
        if duplicate:
            raise DomainError("Project with this name already exists", status_code=409)
        project.name = name

    start_date = data.get("start_date", project.start_date)
    end_date = data.get("end_date", project.end_date)
    _validate_dates(start_date, end_date)

    if "budget_cents" in data:
        _validate_budget(data["budget_cents"])
        project.budget_cents = data["budget_cents"]

    if "venue_ids" in data:
        project.venues = _load_venues(
            session, context.membership.organization_id, data["venue_ids"]
        )

    for field in ["description", "team_type"]:
        if field in data:
            setattr(project, field, data[field])

    if "start_date" in data:
        project.start_date = data["start_date"]
    if "end_date" in data:
        project.end_date = data["end_date"]

    session.add(project)
    session.commit()
    session.refresh(project)
    return project


def delete_project(session: Session, token_value: str, project_id: str) -> None:
    context = resolve_context(session, token_value)
    ensure_permission(context, Permission.MANAGE_PROJECTS)

    project = _get_project_for_org(session, context.membership.organization_id, project_id)
    session.delete(project)
    session.commit()
