from __future__ import annotations

from dataclasses import dataclass

from sqlalchemy import select
from sqlalchemy.orm import Session

from ..models import SessionToken, UserOrganization
from ..rbac import Permission, require_permission
from ..security import now_utc
from .exceptions import AuthorizationError, DomainError


@dataclass
class AuthContext:
    session_token: SessionToken
    membership: UserOrganization


def _get_active_session_token(session: Session, token_value: str) -> SessionToken:
    token = session.scalar(select(SessionToken).where(SessionToken.token == token_value))
    if token is None:
        raise DomainError("Session not found", status_code=401)
    if token.revoked_at is not None:
        raise DomainError("Session revoked", status_code=401)
    if token.expires_at <= now_utc():
        raise DomainError("Session expired", status_code=401)
    return token


def resolve_context(session: Session, token_value: str) -> AuthContext:
    token = _get_active_session_token(session, token_value)
    membership = session.scalar(
        select(UserOrganization)
        .where(UserOrganization.user_id == token.user_id)
        .where(UserOrganization.organization_id == token.organization_id)
    )
    if membership is None:
        raise DomainError("Membership not found", status_code=403)
    return AuthContext(session_token=token, membership=membership)


def ensure_permission(context: AuthContext, permission: Permission) -> None:
    try:
        require_permission(context.membership.role, permission)
    except PermissionError as error:  # pragma: no cover - defensive
        raise AuthorizationError() from error
