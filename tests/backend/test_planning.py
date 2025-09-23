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
    assert "planning_id" in body
    assert body["event_date"] == event_date.date().isoformat()
    assert len(body["assignments"]) == 2

    first_assignment = body["assignments"][0]
    assert first_assignment["artist_id"] == artist_one_id
    assert first_assignment["slot"]["start"].startswith(event_date.date().isoformat())

    second_assignment = body["assignments"][1]
    assert second_assignment["artist_id"] == artist_two_id
    assert second_assignment["slot"]["start"].startswith(event_date.date().isoformat())

    list_response = await async_client.get("/api/v1/plannings")
    assert list_response.status_code == 200
    listed = list_response.json()
    assert len(listed) == 1
    assert listed[0]["planning_id"] == body["planning_id"]


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


@pytest.mark.asyncio
async def test_get_planning_by_id_returns_persisted_item(async_client) -> None:
    """Fetching a planning by id should return the persisted payload."""

    event_date = datetime(2024, 5, 15)
    payload = {
        "event_date": event_date.date().isoformat(),
        "artists": [
            {
                "name": "Echo",
                "availabilities": [
                    {
                        "start": (event_date + timedelta(hours=12)).isoformat(),
                        "end": (event_date + timedelta(hours=13)).isoformat(),
                    }
                ],
            }
        ],
    }

    creation = await async_client.post("/api/v1/plannings", json=payload)
    planning_id = creation.json()["planning_id"]

    response = await async_client.get(f"/api/v1/plannings/{planning_id}")
    body = response.json()

    assert response.status_code == 200
    assert body["planning_id"] == planning_id
    assert body["event_date"] == event_date.date().isoformat()
    assert len(body["assignments"]) == 1


@pytest.mark.asyncio
async def test_get_planning_returns_404_for_unknown_id(async_client) -> None:
    """Requesting a non existing planning should return 404."""

    random_id = str(uuid4())

    response = await async_client.get(f"/api/v1/plannings/{random_id}")
    body = response.json()

    assert response.status_code == 404
    assert body["detail"].startswith("Planning")
