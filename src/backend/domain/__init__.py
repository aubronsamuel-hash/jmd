"""Domain models and services for the planning backend."""

from .artists import Artist, ArtistCreate, ArtistUpdate, Availability
from .planning import PlanningAssignment, PlanningCreate, PlanningResponse
from .services import (
    ArtistConflictError,
    ArtistError,
    ArtistNotFoundError,
    PlanningError,
    PlanningNotFoundError,
    create_artist,
    create_planning,
    delete_artist,
    get_artist,
    get_planning,
    list_artists,
    list_plannings,
    update_artist,
)

__all__ = [
    "Artist",
    "ArtistCreate",
    "ArtistUpdate",
    "Availability",
    "PlanningAssignment",
    "PlanningCreate",
    "PlanningResponse",
    "ArtistError",
    "ArtistNotFoundError",
    "ArtistConflictError",
    "PlanningError",
    "PlanningNotFoundError",
    "create_artist",
    "create_planning",
    "delete_artist",
    "get_artist",
    "get_planning",
    "list_artists",
    "list_plannings",
    "update_artist",
]
