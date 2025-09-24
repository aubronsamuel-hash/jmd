from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from ..config import Settings
from ..models import Invitation, MagicLink, Organization, SessionToken, User, UserOrganization
from ..rbac import Permission, Role, highest_role, require_permission
from ..schemas import (
    InvitationAcceptRequest,
    InvitationCreateRequest,
    LoginRequest,
    MagicLinkRequest,
    MagicLinkVerifyRequest,
    RegisterRequest,
    SwitchOrganisationRequest,
)
from ..security import (
    generate_token,
    hash_password,
    invitation_expiration,
    magic_link_expiration,
    now_utc,
    session_expiration,
    verify_password,
)


class AuthError(Exception):
    """Domain exception for authentication failures."""

    def __init__(self, message: str, status_code: int = 400) -> None:
        super().__init__(message)
        self.message = message
        self.status_code = status_code


@dataclass
class AuthSession:
    token: str
    user_id: str
    organization_id: str
    role: Role
    expires_at: datetime


def _normalise_email(value: str) -> str:
    return value.strip().lower()


def _normalise_slug(value: str) -> str:
    return value.strip().lower()


def _get_user(session: Session, email: str) -> User | None:
    return session.scalar(select(User).where(User.email == _normalise_email(email)))


def _ensure_unique_organization_slug(session: Session, slug: str) -> None:
    exists = session.scalar(select(Organization).where(Organization.slug == slug))
    if exists:
        raise AuthError("Organization slug already in use", status_code=409)


def _create_session(session: Session, user: User, organization_id: str, settings: Settings) -> SessionToken:
    token_value = generate_token(24)
    expires_at = session_expiration(settings)
    session_token = SessionToken(
        user_id=user.id,
        organization_id=organization_id,
        token=token_value,
        expires_at=expires_at,
    )
    session.add(session_token)
    session.flush()
    return session_token


def register_user(session: Session, payload: RegisterRequest, settings: Settings) -> AuthSession:
    email = _normalise_email(payload.email)
    slug = _normalise_slug(payload.organization_slug)

    if _get_user(session, email):
        raise AuthError("User already exists", status_code=409)

    _ensure_unique_organization_slug(session, slug)

    organization = Organization(name=payload.organization_name, slug=slug)
    user = User(email=email, hashed_password=hash_password(payload.password))
    membership = UserOrganization(user=user, organization=organization, role=Role.OWNER)

    session.add_all([organization, user, membership])
    session.flush()

    session_token = _create_session(session, user, organization.id, settings)
    session.commit()

    return AuthSession(
        token=session_token.token,
        user_id=user.id,
        organization_id=organization.id,
        role=Role.OWNER,
        expires_at=session_token.expires_at,
    )


def _get_memberships(session: Session, user_id: str) -> list[UserOrganization]:
    result = session.scalars(
        select(UserOrganization)
        .where(UserOrganization.user_id == user_id)
        .order_by(UserOrganization.created_at)
    )
    return list(result)


def _resolve_membership(session: Session, user_id: str, organization_id: str | None) -> UserOrganization:
    memberships = _get_memberships(session, user_id)
    if not memberships:
        raise AuthError("User has no organisation membership", status_code=403)

    if organization_id is None:
        return memberships[0]

    for membership in memberships:
        if membership.organization_id == organization_id:
            return membership
    raise AuthError("User is not linked to this organisation", status_code=404)


def login_user(session: Session, payload: LoginRequest, settings: Settings) -> AuthSession:
    user = _get_user(session, payload.email)
    if not user or not verify_password(payload.password, user.hashed_password):
        raise AuthError("Invalid credentials", status_code=401)

    membership = _resolve_membership(session, user.id, payload.organization_id)
    session_token = _create_session(session, user, membership.organization_id, settings)
    session.commit()

    return AuthSession(
        token=session_token.token,
        user_id=user.id,
        organization_id=membership.organization_id,
        role=membership.role,
        expires_at=session_token.expires_at,
    )


def _membership_for_magic_link(session: Session, payload: MagicLinkRequest) -> tuple[User, UserOrganization]:
    user = _get_user(session, payload.email)
    if not user:
        raise AuthError("User not found", status_code=404)
    membership = _resolve_membership(session, user.id, payload.organization_id)
    return user, membership


def create_magic_link(session: Session, payload: MagicLinkRequest, settings: Settings) -> MagicLink:
    user, membership = _membership_for_magic_link(session, payload)
    require_permission(membership.role, Permission.REQUEST_MAGIC_LINK)

    link = MagicLink(
        user_id=user.id,
        organization_id=membership.organization_id,
        token=generate_token(20),
        expires_at=magic_link_expiration(settings),
    )
    session.add(link)
    session.flush()
    session.commit()
    return link


def verify_magic_link(session: Session, payload: MagicLinkVerifyRequest, settings: Settings) -> AuthSession:
    link = session.scalar(select(MagicLink).where(MagicLink.token == payload.token))
    if not link:
        raise AuthError("Magic link not found", status_code=404)
    if link.consumed_at is not None:
        raise AuthError("Magic link already used", status_code=400)
    if link.expires_at <= now_utc():
        raise AuthError("Magic link expired", status_code=400)

    link.consumed_at = now_utc()
    user = session.get(User, link.user_id)
    if not user:
        raise AuthError("User not found", status_code=404)

    session_token = _create_session(session, user, link.organization_id, settings)
    membership = _resolve_membership(session, user.id, link.organization_id)
    session.commit()

    return AuthSession(
        token=session_token.token,
        user_id=user.id,
        organization_id=link.organization_id,
        role=membership.role,
        expires_at=session_token.expires_at,
    )


def _get_active_session(session: Session, token: str) -> SessionToken:
    session_token = session.scalar(select(SessionToken).where(SessionToken.token == token))
    if not session_token:
        raise AuthError("Session not found", status_code=401)
    if session_token.revoked_at is not None:
        raise AuthError("Session revoked", status_code=401)
    if session_token.expires_at <= now_utc():
        raise AuthError("Session expired", status_code=401)
    return session_token


def create_invitation(
    session: Session,
    session_token_value: str,
    payload: InvitationCreateRequest,
    settings: Settings,
) -> Invitation:
    session_token = _get_active_session(session, session_token_value)
    membership = _resolve_membership(session, session_token.user_id, session_token.organization_id)
    require_permission(membership.role, Permission.MANAGE_INVITATIONS)

    invitation = Invitation(
        organization_id=membership.organization_id,
        email=_normalise_email(payload.email),
        role=payload.role,
        token=generate_token(20),
        expires_at=invitation_expiration(settings),
        invited_by_id=membership.user_id,
    )
    session.add(invitation)
    session.flush()
    session.commit()
    return invitation


def accept_invitation(
    session: Session,
    payload: InvitationAcceptRequest,
    settings: Settings,
) -> AuthSession:
    invitation = session.scalar(select(Invitation).where(Invitation.token == payload.token))
    if not invitation:
        raise AuthError("Invitation not found", status_code=404)
    if invitation.accepted_at is not None:
        raise AuthError("Invitation already used", status_code=400)
    if invitation.expires_at <= now_utc():
        raise AuthError("Invitation expired", status_code=400)

    email = _normalise_email(payload.email)
    if invitation.email != email:
        raise AuthError("Invitation email mismatch", status_code=400)

    user = _get_user(session, email)
    if user:
        if not verify_password(payload.password, user.hashed_password):
            raise AuthError("Invalid credentials", status_code=401)
    else:
        user = User(email=email, hashed_password=hash_password(payload.password))
        session.add(user)
        session.flush()

    existing_membership = session.scalar(
        select(UserOrganization).where(
            UserOrganization.user_id == user.id,
            UserOrganization.organization_id == invitation.organization_id,
        )
    )
    if existing_membership:
        raise AuthError("User already linked to organisation", status_code=409)

    membership = UserOrganization(
        user_id=user.id,
        organization_id=invitation.organization_id,
        role=invitation.role,
    )
    session.add(membership)

    invitation.accepted_at = now_utc()

    session_token = _create_session(session, user, invitation.organization_id, settings)
    session.commit()

    return AuthSession(
        token=session_token.token,
        user_id=user.id,
        organization_id=invitation.organization_id,
        role=membership.role,
        expires_at=session_token.expires_at,
    )


def switch_organisation(
    session: Session,
    session_token_value: str,
    payload: SwitchOrganisationRequest,
    settings: Settings,
) -> AuthSession:
    session_token = _get_active_session(session, session_token_value)
    membership = _resolve_membership(session, session_token.user_id, payload.organization_id)
    require_permission(membership.role, Permission.SWITCH_ORGANISATION)

    session_token.revoked_at = now_utc()
    user = session.get(User, session_token.user_id)
    if not user:
        raise AuthError("User not found", status_code=404)

    new_session = _create_session(session, user, membership.organization_id, settings)
    session.commit()

    return AuthSession(
        token=new_session.token,
        user_id=user.id,
        organization_id=membership.organization_id,
        role=membership.role,
        expires_at=new_session.expires_at,
    )


def resolve_default_role(session: Session, user_id: str) -> Role:
    memberships = _get_memberships(session, user_id)
    if not memberships:
        raise AuthError("User has no organisations", status_code=404)
    roles = [membership.role for membership in memberships]
    return highest_role(roles)
