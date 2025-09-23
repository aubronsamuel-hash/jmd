"""FastAPI application entrypoint."""

from __future__ import annotations

from fastapi import FastAPI, HTTPException, status

from .config import get_settings
from .domain import PlanningCreate, PlanningError, PlanningResponse, create_planning


def create_app() -> FastAPI:
    """Instantiate and configure the FastAPI application."""

    settings = get_settings()
    app = FastAPI(title=settings.app_name)

    @app.get(f"{settings.api_prefix}/health", tags=["health"])
    async def healthcheck() -> dict[str, str]:
        """Simple endpoint used by monitoring systems."""

        return {
            "status": "ok",
            "environment": settings.environment,
            "service": settings.app_name,
        }

    @app.post(
        f"{settings.api_prefix}/plannings",
        response_model=PlanningResponse,
        status_code=status.HTTP_201_CREATED,
        tags=["planning"],
    )
    async def post_planning(payload: PlanningCreate) -> PlanningResponse:
        """Create a planning from the provided payload."""

        try:
            return create_planning(payload)
        except PlanningError as exc:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc

    return app


app = create_app()

__all__ = ["app", "create_app"]
