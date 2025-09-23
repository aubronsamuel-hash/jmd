"""Tests for the planning creation workflow."""

from __future__ import annotations

from datetime import datetime, timedelta
from uuid import uuid4

import pytest


@pytest.mark.asyncio
async def test_create_planning_returns_assignments(async_client) -> None:
    """Creating a planning should allocate the earliest slot for each artist."""

    event_date = datetime(2024, 5, 15)
    artist_one_id = str(uuid4())
    artist_two_id = str(uuid4())
    payload = {
        "event_date": event_date.date().isoformat(),
        "artists": [
            {
                "id": artist_one_id,
                "name": "Alice",
                "availabilities": [
                    {
                        "start": (event_date + timedelta(hours=8)).isoformat(),
                        "end": (event_date + timedelta(hours=9)).isoformat(),
                    },
                    {
                        "start": (event_date + timedelta(days=1, hours=10)).isoformat(),
                        "end": (event_date + timedelta(days=1, hours=12)).isoformat(),
                    },
                ],
            },
            {
                "id": artist_two_id,
                "name": "Bob",
                "availabilities": [
                    {
                        "start": (event_date + timedelta(hours=10)).isoformat(),
                        "end": (event_date + timedelta(hours=11)).isoformat(),
                    }
                ],
            },
        ],
    }

    response = await async_client.post("/api/v1/plannings", json=payload)
    body = response.json()

    assert response.status_code == 201
    assert body["event_date"] == event_date.date().isoformat()
    assert len(body["assignments"]) == 2

    first_assignment = body["assignments"][0]
    assert first_assignment["artist_id"] == artist_one_id
    assert first_assignment["slot"]["start"].startswith(event_date.date().isoformat())

    second_assignment = body["assignments"][1]
    assert second_assignment["artist_id"] == artist_two_id
    assert second_assignment["slot"]["start"].startswith(event_date.date().isoformat())


@pytest.mark.asyncio
async def test_create_planning_without_matching_slot_returns_400(async_client) -> None:
    """If an artist has no availability for the target date a 400 should be returned."""

    event_date = datetime(2024, 5, 15)
    payload = {
        "event_date": event_date.date().isoformat(),
        "artists": [
            {
                "name": "Charlie",
                "availabilities": [
                    {
                        "start": (event_date + timedelta(days=1, hours=9)).isoformat(),
                        "end": (event_date + timedelta(days=1, hours=10)).isoformat(),
                    }
                ],
            }
        ],
    }

    response = await async_client.post("/api/v1/plannings", json=payload)
    body = response.json()

    assert response.status_code == 400
    assert body["detail"].startswith("Artist 'Charlie' has no availability")


@pytest.mark.asyncio
async def test_create_planning_rejects_invalid_availability(async_client) -> None:
    """Availability slots with negative duration should be rejected by validation."""

    event_date = datetime(2024, 5, 15)
    payload = {
        "event_date": event_date.date().isoformat(),
        "artists": [
            {
                "name": "Delta",
                "availabilities": [
                    {
                        "start": (event_date + timedelta(hours=11)).isoformat(),
                        "end": (event_date + timedelta(hours=10, minutes=30)).isoformat(),
                    }
                ],
            }
        ],
    }

    response = await async_client.post("/api/v1/plannings", json=payload)
    body = response.json()

    assert response.status_code == 422
    assert "Availability end must be after start" in str(body)
