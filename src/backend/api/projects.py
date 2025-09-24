from __future__ import annotations

from fastapi import APIRouter, Depends, Header, HTTPException, Response, status
from sqlalchemy.orm import Session

from ..dependencies import get_session
from ..schemas import ProjectCreate, ProjectResponse, ProjectUpdate
from ..services.exceptions import DomainError
from ..services.projects import create_project, delete_project, get_project, list_projects, update_project

router = APIRouter(prefix="/projects", tags=["projects"])


@router.post("/", response_model=ProjectResponse, status_code=status.HTTP_201_CREATED)
def create_project_endpoint(
    payload: ProjectCreate,
    session_token: str = Header(alias="X-Session-Token"),
    db: Session = Depends(get_session),
) -> ProjectResponse:
    try:
        project = create_project(db, session_token, payload)
    except DomainError as error:
        raise HTTPException(status_code=error.status_code, detail=error.message) from error
    return ProjectResponse.model_validate(project, from_attributes=True)


@router.get("/", response_model=list[ProjectResponse])
def list_projects_endpoint(
    session_token: str = Header(alias="X-Session-Token"),
    db: Session = Depends(get_session),
) -> list[ProjectResponse]:
    try:
        projects = list_projects(db, session_token)
    except DomainError as error:
        raise HTTPException(status_code=error.status_code, detail=error.message) from error
    return [ProjectResponse.model_validate(project, from_attributes=True) for project in projects]


@router.get("/{project_id}", response_model=ProjectResponse)
def get_project_endpoint(
    project_id: str,
    session_token: str = Header(alias="X-Session-Token"),
    db: Session = Depends(get_session),
) -> ProjectResponse:
    try:
        project = get_project(db, session_token, project_id)
    except DomainError as error:
        raise HTTPException(status_code=error.status_code, detail=error.message) from error
    return ProjectResponse.model_validate(project, from_attributes=True)


@router.put("/{project_id}", response_model=ProjectResponse)
def update_project_endpoint(
    project_id: str,
    payload: ProjectUpdate,
    session_token: str = Header(alias="X-Session-Token"),
    db: Session = Depends(get_session),
) -> ProjectResponse:
    try:
        project = update_project(db, session_token, project_id, payload)
    except DomainError as error:
        raise HTTPException(status_code=error.status_code, detail=error.message) from error
    return ProjectResponse.model_validate(project, from_attributes=True)


@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_project_endpoint(
    project_id: str,
    session_token: str = Header(alias="X-Session-Token"),
    db: Session = Depends(get_session),
) -> Response:
    try:
        delete_project(db, session_token, project_id)
    except DomainError as error:
        raise HTTPException(status_code=error.status_code, detail=error.message) from error
    return Response(status_code=status.HTTP_204_NO_CONTENT)
