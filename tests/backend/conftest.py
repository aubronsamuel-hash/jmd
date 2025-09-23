"""Test fixtures for the backend package."""

from __future__ import annotations

import os
from collections.abc import AsyncIterator, Callable
from datetime import datetime, timedelta
from uuid import uuid4

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient

from backend.config import get_settings
from backend.main import create_app


@pytest_asyncio.fixture
async def async_client() -> AsyncIterator[AsyncClient]:
    """Provide an HTTPX async client bound to the FastAPI app."""

    os.environ["BACKEND_DATABASE_URL"] = "sqlite+pysqlite:///:memory:"
    get_settings.cache_clear()
    app = create_app()
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        yield client


@pytest.fixture
def artist_payload_factory() -> Callable[..., dict[str, object]]:
    """Return a factory producing artist payloads with generated slots."""

    def _factory(
        name: str = "Alice",
        *,
        base: datetime | None = None,
        slots: int = 1,
        include_id: bool = False,
    ) -> dict[str, object]:
        start_time = base or datetime(2024, 5, 10, 9, 0)
        availabilities = []
        for index in range(slots):
            slot_start = start_time + timedelta(hours=2 * index)
            availabilities.append(
                {
                    "start": slot_start.isoformat(),
                    "end": (slot_start + timedelta(hours=1)).isoformat(),
                }
            )
        payload: dict[str, object] = {"name": name, "availabilities": availabilities}
        if include_id:
            payload["id"] = str(uuid4())
        return payload

    return _factory
