"""Smoke tests for the health endpoint."""

from __future__ import annotations

import pytest


@pytest.mark.asyncio
async def test_health_endpoint_reports_ok(async_client) -> None:
    """The health endpoint should return a successful payload."""

    response = await async_client.get("/api/v1/health")
    payload = response.json()

    assert response.status_code == 200
    assert payload["status"] == "ok"
    assert "environment" in payload
    assert "service" in payload
