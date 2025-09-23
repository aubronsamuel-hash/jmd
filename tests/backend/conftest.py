"""Test fixtures for the backend package."""

from __future__ import annotations

import pytest_asyncio
from httpx import ASGITransport, AsyncClient

from backend.main import create_app


@pytest_asyncio.fixture
async def async_client() -> AsyncClient:
    """Provide an HTTPX async client bound to the FastAPI app."""

    app = create_app()
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        yield client
