from __future__ import annotations

from fastapi import APIRouter, Depends, Header, HTTPException, status
from sqlalchemy.orm import Session

from ..config import Settings
from ..dependencies import get_session, get_settings
from ..schemas import (
    InvitationAcceptRequest,
    InvitationCreateRequest,
    InvitationResponse,
    LoginRequest,
    MagicLinkRequest,
    MagicLinkResponse,
    MagicLinkVerifyRequest,
    RegisterRequest,
    SessionEnvelope,
    SwitchOrganisationRequest,
)
from ..services.auth import (
    AuthError,
    AuthSession,
    accept_invitation,
    create_invitation,
    create_magic_link,
    login_user,
    register_user,
    switch_organisation,
    verify_magic_link,
)

router = APIRouter(prefix="/auth", tags=["auth"])


def _to_session_envelope(session: AuthSession) -> SessionEnvelope:
    return SessionEnvelope(
        session_token=session.token,
        user_id=session.user_id,
        organization_id=session.organization_id,
        role=session.role,
        expires_at=session.expires_at,
    )


def _handle_auth_error(error: AuthError) -> HTTPException:
    return HTTPException(status_code=error.status_code, detail=error.message)


@router.post("/register", response_model=SessionEnvelope, status_code=status.HTTP_201_CREATED)
def register_endpoint(
    payload: RegisterRequest,
    db: Session = Depends(get_session),
    settings: Settings = Depends(get_settings),
) -> SessionEnvelope:
    try:
        session = register_user(db, payload, settings)
    except AuthError as error:  # pragma: no cover - defensive
        raise _handle_auth_error(error) from error
    return _to_session_envelope(session)


@router.post("/login", response_model=SessionEnvelope)
def login_endpoint(
    payload: LoginRequest,
    db: Session = Depends(get_session),
    settings: Settings = Depends(get_settings),
) -> SessionEnvelope:
    try:
        session = login_user(db, payload, settings)
    except AuthError as error:
        raise _handle_auth_error(error) from error
    return _to_session_envelope(session)


@router.post("/magic-link", response_model=MagicLinkResponse, status_code=status.HTTP_201_CREATED)
def magic_link_request_endpoint(
    payload: MagicLinkRequest,
    db: Session = Depends(get_session),
    settings: Settings = Depends(get_settings),
) -> MagicLinkResponse:
    try:
        link = create_magic_link(db, payload, settings)
    except AuthError as error:
        raise _handle_auth_error(error) from error
    return MagicLinkResponse(token=link.token, expires_at=link.expires_at, organization_id=link.organization_id)


@router.post("/magic-link/verify", response_model=SessionEnvelope)
def magic_link_verify_endpoint(
    payload: MagicLinkVerifyRequest,
    db: Session = Depends(get_session),
    settings: Settings = Depends(get_settings),
) -> SessionEnvelope:
    try:
        session = verify_magic_link(db, payload, settings)
    except AuthError as error:
        raise _handle_auth_error(error) from error
    return _to_session_envelope(session)


@router.post("/invitations", response_model=InvitationResponse, status_code=status.HTTP_201_CREATED)
def invitation_create_endpoint(
    payload: InvitationCreateRequest,
    session_token: str = Header(alias="X-Session-Token"),
    db: Session = Depends(get_session),
    settings: Settings = Depends(get_settings),
) -> InvitationResponse:
    try:
        invitation = create_invitation(db, session_token, payload, settings)
    except AuthError as error:
        raise _handle_auth_error(error) from error
    return InvitationResponse(
        token=invitation.token,
        email=invitation.email,
        role=invitation.role,
        expires_at=invitation.expires_at,
        organization_id=invitation.organization_id,
    )


@router.post("/invitations/accept", response_model=SessionEnvelope)
def invitation_accept_endpoint(
    payload: InvitationAcceptRequest,
    db: Session = Depends(get_session),
    settings: Settings = Depends(get_settings),
) -> SessionEnvelope:
    try:
        session = accept_invitation(db, payload, settings)
    except AuthError as error:
        raise _handle_auth_error(error) from error
    return _to_session_envelope(session)


@router.post("/switch", response_model=SessionEnvelope)
def switch_endpoint(
    payload: SwitchOrganisationRequest,
    session_token: str = Header(alias="X-Session-Token"),
    db: Session = Depends(get_session),
    settings: Settings = Depends(get_settings),
) -> SessionEnvelope:
    try:
        session = switch_organisation(db, session_token, payload, settings)
    except AuthError as error:
        raise _handle_auth_error(error) from error
    return _to_session_envelope(session)
