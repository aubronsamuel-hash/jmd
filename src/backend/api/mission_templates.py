from __future__ import annotations

from fastapi import APIRouter, Depends, Header, HTTPException, Response, status
from sqlalchemy.orm import Session

from ..dependencies import get_session
from ..schemas import MissionTemplateCreate, MissionTemplateResponse, MissionTemplateUpdate
from ..services.exceptions import DomainError
from ..services.mission_templates import (
    create_template,
    delete_template,
    get_template,
    list_templates,
    update_template,
)

router = APIRouter(prefix="/mission-templates", tags=["mission-templates"])


@router.post("/", response_model=MissionTemplateResponse, status_code=status.HTTP_201_CREATED)
def create_template_endpoint(
    payload: MissionTemplateCreate,
    session_token: str = Header(alias="X-Session-Token"),
    db: Session = Depends(get_session),
) -> MissionTemplateResponse:
    try:
        template = create_template(db, session_token, payload)
    except DomainError as error:
        raise HTTPException(status_code=error.status_code, detail=error.message) from error
    return MissionTemplateResponse.model_validate(template, from_attributes=True)


@router.get("/", response_model=list[MissionTemplateResponse])
def list_templates_endpoint(
    session_token: str = Header(alias="X-Session-Token"),
    db: Session = Depends(get_session),
) -> list[MissionTemplateResponse]:
    try:
        templates = list_templates(db, session_token)
    except DomainError as error:
        raise HTTPException(status_code=error.status_code, detail=error.message) from error
    return [MissionTemplateResponse.model_validate(template, from_attributes=True) for template in templates]


@router.get("/{template_id}", response_model=MissionTemplateResponse)
def get_template_endpoint(
    template_id: str,
    session_token: str = Header(alias="X-Session-Token"),
    db: Session = Depends(get_session),
) -> MissionTemplateResponse:
    try:
        template = get_template(db, session_token, template_id)
    except DomainError as error:
        raise HTTPException(status_code=error.status_code, detail=error.message) from error
    return MissionTemplateResponse.model_validate(template, from_attributes=True)


@router.put("/{template_id}", response_model=MissionTemplateResponse)
def update_template_endpoint(
    template_id: str,
    payload: MissionTemplateUpdate,
    session_token: str = Header(alias="X-Session-Token"),
    db: Session = Depends(get_session),
) -> MissionTemplateResponse:
    try:
        template = update_template(db, session_token, template_id, payload)
    except DomainError as error:
        raise HTTPException(status_code=error.status_code, detail=error.message) from error
    return MissionTemplateResponse.model_validate(template, from_attributes=True)


@router.delete("/{template_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_template_endpoint(
    template_id: str,
    session_token: str = Header(alias="X-Session-Token"),
    db: Session = Depends(get_session),
) -> Response:
    try:
        delete_template(db, session_token, template_id)
    except DomainError as error:
        raise HTTPException(status_code=error.status_code, detail=error.message) from error
    return Response(status_code=status.HTTP_204_NO_CONTENT)
