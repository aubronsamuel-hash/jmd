from __future__ import annotations

from datetime import datetime, timedelta

import pytest

from backend.notifications import NotificationEventType


@pytest.mark.asyncio
async def test_notifications_test_endpoint_dispatches_channels(async_client) -> None:
    """The test endpoint should dispatch a message on every configured channel."""

    response = await async_client.post("/api/v1/notifications/test")
    body = response.json()

    assert response.status_code == 200
    assert body["event"] == NotificationEventType.TEST.value
    assert sorted(body["channels"]) == ["email", "telegram"]
    assert body["metadata"]["purpose"] == "connectivity-check"


@pytest.mark.asyncio
async def test_planning_creation_records_notification(async_client, artist_payload_factory) -> None:
    """Creating a planning should record a planning notification in history."""

    event_date = datetime(2024, 6, 21, 9, 0)
    payload = {
        "event_date": event_date.date().isoformat(),
        "artists": [
            artist_payload_factory(name="Alice", base=event_date, include_id=True),
            artist_payload_factory(
                name="Bob",
                base=event_date + timedelta(hours=1),
                include_id=True,
            ),
        ],
    }

    response = await async_client.post("/api/v1/plannings", json=payload)
    assert response.status_code == 201

    transport = async_client._transport  # type: ignore[attr-defined]
    service = transport.app.state.notification_service  # type: ignore[attr-defined]
    last_message = service.history[-1]

    assert last_message.event is NotificationEventType.PLANNING_CREATED
    assert "Nouvelle affectation planifiee" in last_message.subject
    assert "Alice" in last_message.body
    assert "Bob" in last_message.body


@pytest.mark.asyncio
async def test_trigger_planning_notification_endpoint(async_client, artist_payload_factory) -> None:
    """The planning notification endpoint should personalize the message."""

    event_date = datetime(2024, 7, 5, 10, 0)
    payload = {
        "event_date": event_date.date().isoformat(),
        "artists": [
            artist_payload_factory(name="Charlie", base=event_date, include_id=True),
        ],
    }

    creation = await async_client.post("/api/v1/plannings", json=payload)
    planning_id = creation.json()["planning_id"]

    response = await async_client.post(
        f"/api/v1/notifications/plannings/{planning_id}/events",
        json={"event": NotificationEventType.PLANNING_REMINDER.value},
    )
    body = response.json()

    assert response.status_code == 200
    assert body["event"] == NotificationEventType.PLANNING_REMINDER.value
    assert body["subject"].startswith("Rappel planning J-1")
    assert "Charlie" in body["body"]


@pytest.mark.asyncio
async def test_trigger_planning_notification_rejects_test_event(async_client, artist_payload_factory) -> None:
    """Requesting a planning notification with the test event should be rejected."""

    event_date = datetime(2024, 7, 6, 10, 0)
    payload = {
        "event_date": event_date.date().isoformat(),
        "artists": [artist_payload_factory(name="Dana", base=event_date, include_id=True)],
    }

    creation = await async_client.post("/api/v1/plannings", json=payload)
    planning_id = creation.json()["planning_id"]

    response = await async_client.post(
        f"/api/v1/notifications/plannings/{planning_id}/events",
        json={"event": NotificationEventType.TEST.value},
    )

    assert response.status_code == 422
