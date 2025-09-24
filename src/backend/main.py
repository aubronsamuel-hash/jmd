from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI

from .api.auth import router as auth_router
from .api.mission_tags import router as mission_tags_router
from .api.mission_templates import router as mission_templates_router
from .api.projects import router as projects_router
from .api.venues import router as venues_router
from .config import Settings, get_settings
from .db import Base, build_engine, build_session_factory
from .dependencies import get_settings as request_settings  # noqa: F401
from .schemas import HealthResponse


def create_app(settings: Settings | None = None) -> FastAPI:
    runtime_settings = settings or get_settings()
    engine = build_engine(runtime_settings)
    Base.metadata.create_all(bind=engine)
    session_factory = build_session_factory(engine)

    @asynccontextmanager
    async def lifespan(app: FastAPI):  # pragma: no cover - simple resource management
        try:
            yield
        finally:
            engine.dispose()

    app = FastAPI(title="JMD Backend", version="0.1.0", lifespan=lifespan)
    app.state.settings = runtime_settings
    app.state.engine = engine
    app.state.session_factory = session_factory

    @app.get("/api/v1/health", response_model=HealthResponse, tags=["health"])
    def health_check() -> HealthResponse:  # pragma: no cover - trivial
        return HealthResponse()

    app.include_router(auth_router, prefix="/api/v1")
    app.include_router(venues_router, prefix="/api/v1")
    app.include_router(projects_router, prefix="/api/v1")
    app.include_router(mission_tags_router, prefix="/api/v1")
    app.include_router(mission_templates_router, prefix="/api/v1")

    return app


def get_app() -> FastAPI:
    return create_app()


app = get_app()
