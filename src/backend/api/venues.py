from __future__ import annotations

from fastapi import APIRouter, Depends, Header, HTTPException, Response, status
from sqlalchemy.orm import Session

from ..dependencies import get_session
from ..schemas import VenueCreate, VenueResponse, VenueUpdate
from ..services.exceptions import DomainError
from ..services.venues import create_venue, delete_venue, get_venue, list_venues, update_venue

router = APIRouter(prefix="/venues", tags=["venues"])


@router.post("/", response_model=VenueResponse, status_code=status.HTTP_201_CREATED)
def create_venue_endpoint(
    payload: VenueCreate,
    session_token: str = Header(alias="X-Session-Token"),
    db: Session = Depends(get_session),
) -> VenueResponse:
    try:
        venue = create_venue(db, session_token, payload)
    except DomainError as error:
        raise HTTPException(status_code=error.status_code, detail=error.message) from error
    return VenueResponse.model_validate(venue, from_attributes=True)


@router.get("/", response_model=list[VenueResponse])
def list_venues_endpoint(
    session_token: str = Header(alias="X-Session-Token"),
    db: Session = Depends(get_session),
) -> list[VenueResponse]:
    try:
        venues = list_venues(db, session_token)
    except DomainError as error:
        raise HTTPException(status_code=error.status_code, detail=error.message) from error
    return [VenueResponse.model_validate(venue, from_attributes=True) for venue in venues]


@router.get("/{venue_id}", response_model=VenueResponse)
def get_venue_endpoint(
    venue_id: str,
    session_token: str = Header(alias="X-Session-Token"),
    db: Session = Depends(get_session),
) -> VenueResponse:
    try:
        venue = get_venue(db, session_token, venue_id)
    except DomainError as error:
        raise HTTPException(status_code=error.status_code, detail=error.message) from error
    return VenueResponse.model_validate(venue, from_attributes=True)


@router.put("/{venue_id}", response_model=VenueResponse)
def update_venue_endpoint(
    venue_id: str,
    payload: VenueUpdate,
    session_token: str = Header(alias="X-Session-Token"),
    db: Session = Depends(get_session),
) -> VenueResponse:
    try:
        venue = update_venue(db, session_token, venue_id, payload)
    except DomainError as error:
        raise HTTPException(status_code=error.status_code, detail=error.message) from error
    return VenueResponse.model_validate(venue, from_attributes=True)


@router.delete("/{venue_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_venue_endpoint(
    venue_id: str,
    session_token: str = Header(alias="X-Session-Token"),
    db: Session = Depends(get_session),
) -> Response:
    try:
        delete_venue(db, session_token, venue_id)
    except DomainError as error:
        raise HTTPException(status_code=error.status_code, detail=error.message) from error
    return Response(status_code=status.HTTP_204_NO_CONTENT)
