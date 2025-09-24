from __future__ import annotations

from enum import Enum
from typing import Final


class Permission(Enum):
    MANAGE_INVITATIONS = "manage_invitations"
    SWITCH_ORGANISATION = "switch_organisation"
    REQUEST_MAGIC_LINK = "request_magic_link"
    MANAGE_VENUES = "manage_venues"
    VIEW_VENUES = "view_venues"
    MANAGE_PROJECTS = "manage_projects"
    VIEW_PROJECTS = "view_projects"
    MANAGE_MISSION_TEMPLATES = "manage_mission_templates"
    VIEW_MISSION_TEMPLATES = "view_mission_templates"
    MANAGE_MISSION_TAGS = "manage_mission_tags"
    VIEW_MISSION_TAGS = "view_mission_tags"


class Role(Enum):
    OWNER = "owner"
    ADMIN = "admin"
    MEMBER = "member"
    VIEWER = "viewer"


_ROLE_PERMISSIONS: Final[dict[Role, set[Permission]]] = {
    Role.OWNER: {
        Permission.MANAGE_INVITATIONS,
        Permission.SWITCH_ORGANISATION,
        Permission.REQUEST_MAGIC_LINK,
        Permission.MANAGE_VENUES,
        Permission.VIEW_VENUES,
        Permission.MANAGE_PROJECTS,
        Permission.VIEW_PROJECTS,
        Permission.MANAGE_MISSION_TEMPLATES,
        Permission.VIEW_MISSION_TEMPLATES,
        Permission.MANAGE_MISSION_TAGS,
        Permission.VIEW_MISSION_TAGS,
    },
    Role.ADMIN: {
        Permission.MANAGE_INVITATIONS,
        Permission.SWITCH_ORGANISATION,
        Permission.REQUEST_MAGIC_LINK,
        Permission.MANAGE_VENUES,
        Permission.VIEW_VENUES,
        Permission.MANAGE_PROJECTS,
        Permission.VIEW_PROJECTS,
        Permission.MANAGE_MISSION_TEMPLATES,
        Permission.VIEW_MISSION_TEMPLATES,
        Permission.MANAGE_MISSION_TAGS,
        Permission.VIEW_MISSION_TAGS,
    },
    Role.MEMBER: {
        Permission.SWITCH_ORGANISATION,
        Permission.REQUEST_MAGIC_LINK,
        Permission.VIEW_VENUES,
        Permission.VIEW_PROJECTS,
        Permission.VIEW_MISSION_TEMPLATES,
        Permission.VIEW_MISSION_TAGS,
    },
    Role.VIEWER: {
        Permission.SWITCH_ORGANISATION,
        Permission.VIEW_VENUES,
        Permission.VIEW_PROJECTS,
        Permission.VIEW_MISSION_TEMPLATES,
        Permission.VIEW_MISSION_TAGS,
    },
}


def require_permission(role: Role, permission: Permission) -> None:
    """Validate that the provided role grants the given permission."""

    allowed = _ROLE_PERMISSIONS.get(role, set())
    if permission not in allowed:
        raise PermissionError(f"Role {role.value} lacks permission {permission.value}")


def highest_role(roles: list[Role]) -> Role:
    """Return the most privileged role from the given list."""

    hierarchy = [Role.OWNER, Role.ADMIN, Role.MEMBER, Role.VIEWER]
    for role in hierarchy:
        if role in roles:
            return role
    return Role.VIEWER
