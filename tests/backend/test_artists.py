"""Integration tests covering the artist CRUD API."""

from __future__ import annotations

from uuid import uuid4

import pytest


@pytest.mark.asyncio
async def test_create_artist_persists_and_returns_payload(async_client, artist_payload_factory) -> None:
    """Posting a new artist should store it and return the representation."""

    payload = artist_payload_factory(name="Zelda", slots=2)

    response = await async_client.post("/api/v1/artists", json=payload)
    body = response.json()

    assert response.status_code == 201
    assert body["name"] == "Zelda"
    assert len(body["availabilities"]) == 2

    artist_id = body["id"]
    fetch = await async_client.get(f"/api/v1/artists/{artist_id}")
    assert fetch.status_code == 200
    assert fetch.json() == body


@pytest.mark.asyncio
async def test_list_artists_returns_ordered_items(async_client, artist_payload_factory) -> None:
    """Listing artists should return them ordered alphabetically by name."""

    await async_client.post("/api/v1/artists", json=artist_payload_factory(name="Charlie"))
    await async_client.post("/api/v1/artists", json=artist_payload_factory(name="Alice"))

    response = await async_client.get("/api/v1/artists")
    body = response.json()

    assert response.status_code == 200
    assert [item["name"] for item in body] == ["Alice", "Charlie"]


@pytest.mark.asyncio
async def test_put_artist_replaces_availabilities(async_client, artist_payload_factory) -> None:
    """Updating an artist should replace the stored availabilities set."""

    creation = await async_client.post("/api/v1/artists", json=artist_payload_factory(slots=2))
    artist_id = creation.json()["id"]

    update_payload = {
        "name": "Alice Updated",
        "availabilities": [
            {
                "start": "2024-05-11T10:00:00",
                "end": "2024-05-11T11:00:00",
            }
        ],
    }

    update = await async_client.put(f"/api/v1/artists/{artist_id}", json=update_payload)
    body = update.json()

    assert update.status_code == 200
    assert body["name"] == "Alice Updated"
    assert len(body["availabilities"]) == 1
    assert body["availabilities"][0]["start"] == "2024-05-11T10:00:00"

    fetch = await async_client.get(f"/api/v1/artists/{artist_id}")
    assert fetch.json()["availabilities"] == body["availabilities"]


@pytest.mark.asyncio
async def test_delete_artist_removes_resource(async_client, artist_payload_factory) -> None:
    """Deleting an artist should cascade to its availabilities."""

    creation = await async_client.post("/api/v1/artists", json=artist_payload_factory())
    artist_id = creation.json()["id"]

    deletion = await async_client.delete(f"/api/v1/artists/{artist_id}")
    assert deletion.status_code == 204

    fetch = await async_client.get(f"/api/v1/artists/{artist_id}")
    assert fetch.status_code == 404


@pytest.mark.asyncio
async def test_post_artist_with_existing_id_returns_conflict(async_client, artist_payload_factory) -> None:
    """Creating an artist with an existing identifier should return 409."""

    payload = artist_payload_factory(include_id=True)
    await async_client.post("/api/v1/artists", json=payload)

    response = await async_client.post("/api/v1/artists", json=payload)
    body = response.json()

    assert response.status_code == 409
    assert body["detail"].startswith("Artist")


@pytest.mark.asyncio
async def test_unknown_artist_operations_return_404(async_client) -> None:
    """Operations targeting an unknown artist should return 404."""

    random_id = str(uuid4())

    read = await async_client.get(f"/api/v1/artists/{random_id}")
    assert read.status_code == 404

    update_payload = {
        "name": "Ghost",
        "availabilities": [],
    }
    update = await async_client.put(f"/api/v1/artists/{random_id}", json=update_payload)
    assert update.status_code == 404

    delete = await async_client.delete(f"/api/v1/artists/{random_id}")
    assert delete.status_code == 404
