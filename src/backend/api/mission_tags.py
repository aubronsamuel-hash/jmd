from __future__ import annotations

from fastapi import APIRouter, Depends, Header, HTTPException, Response, status
from sqlalchemy.orm import Session

from ..dependencies import get_session
from ..schemas import MissionTagCreate, MissionTagResponse, MissionTagUpdate
from ..services.exceptions import DomainError
from ..services.mission_tags import create_tag, delete_tag, get_tag, list_tags, update_tag

router = APIRouter(prefix="/mission-tags", tags=["mission-tags"])


@router.post("/", response_model=MissionTagResponse, status_code=status.HTTP_201_CREATED)
def create_tag_endpoint(
    payload: MissionTagCreate,
    session_token: str = Header(alias="X-Session-Token"),
    db: Session = Depends(get_session),
) -> MissionTagResponse:
    try:
        tag = create_tag(db, session_token, payload)
    except DomainError as error:
        raise HTTPException(status_code=error.status_code, detail=error.message) from error
    return MissionTagResponse.model_validate(tag, from_attributes=True)


@router.get("/", response_model=list[MissionTagResponse])
def list_tags_endpoint(
    session_token: str = Header(alias="X-Session-Token"),
    db: Session = Depends(get_session),
) -> list[MissionTagResponse]:
    try:
        tags = list_tags(db, session_token)
    except DomainError as error:
        raise HTTPException(status_code=error.status_code, detail=error.message) from error
    return [MissionTagResponse.model_validate(tag, from_attributes=True) for tag in tags]


@router.get("/{tag_id}", response_model=MissionTagResponse)
def get_tag_endpoint(
    tag_id: str,
    session_token: str = Header(alias="X-Session-Token"),
    db: Session = Depends(get_session),
) -> MissionTagResponse:
    try:
        tag = get_tag(db, session_token, tag_id)
    except DomainError as error:
        raise HTTPException(status_code=error.status_code, detail=error.message) from error
    return MissionTagResponse.model_validate(tag, from_attributes=True)


@router.put("/{tag_id}", response_model=MissionTagResponse)
def update_tag_endpoint(
    tag_id: str,
    payload: MissionTagUpdate,
    session_token: str = Header(alias="X-Session-Token"),
    db: Session = Depends(get_session),
) -> MissionTagResponse:
    try:
        tag = update_tag(db, session_token, tag_id, payload)
    except DomainError as error:
        raise HTTPException(status_code=error.status_code, detail=error.message) from error
    return MissionTagResponse.model_validate(tag, from_attributes=True)


@router.delete("/{tag_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_tag_endpoint(
    tag_id: str,
    session_token: str = Header(alias="X-Session-Token"),
    db: Session = Depends(get_session),
) -> Response:
    try:
        delete_tag(db, session_token, tag_id)
    except DomainError as error:
        raise HTTPException(status_code=error.status_code, detail=error.message) from error
    return Response(status_code=status.HTTP_204_NO_CONTENT)
