from __future__ import annotations

from enum import Enum
from typing import Final


class Permission(Enum):
    MANAGE_INVITATIONS = "manage_invitations"
    SWITCH_ORGANISATION = "switch_organisation"
    REQUEST_MAGIC_LINK = "request_magic_link"


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
    },
    Role.ADMIN: {
        Permission.MANAGE_INVITATIONS,
        Permission.SWITCH_ORGANISATION,
        Permission.REQUEST_MAGIC_LINK,
    },
    Role.MEMBER: {
        Permission.SWITCH_ORGANISATION,
        Permission.REQUEST_MAGIC_LINK,
    },
    Role.VIEWER: {Permission.SWITCH_ORGANISATION},
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
