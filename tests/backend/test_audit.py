from __future__ import annotations

from datetime import datetime, timedelta, timezone
from uuid import uuid4

import pytest

from backend.models import AuditLog


@pytest.mark.asyncio
async def test_audit_log_created_on_artist_creation(async_client) -> None:
    payload = {
        "name": "Audit Artist",
        "availabilities": [
            {
                "start": "2024-05-10T09:00:00",
                "end": "2024-05-10T10:00:00",
            }
        ],
    }
    response = await async_client.post("/api/v1/artists", json=payload)
    assert response.status_code == 201

    logs_response = await async_client.get("/api/v1/audit/logs")
    assert logs_response.status_code == 200
    payload = logs_response.json()
    assert payload["count"] >= 1
    matching = [
        item
        for item in payload["items"]
        if item["event_type"] == "artist.created"
        and item["payload"]["name"] == "Audit Artist"
    ]
    assert matching, "expected audit log for artist creation"

    export_response = await async_client.get(
        "/api/v1/audit/logs/export", params={"format": "csv"}
    )
    assert export_response.status_code == 200
    export_payload = export_response.json()
    assert export_payload["format"] == "csv"
    assert "data_base64" in export_payload


@pytest.mark.asyncio
async def test_rgpd_workflow_tracked_in_audit(async_client) -> None:
    request_payload = {
        "request_type": "access",
        "requester": "legal@example.com",
        "subject_reference": "artist-42",
        "notes": "Controle trimestriel",
    }
    create_response = await async_client.post(
        "/api/v1/rgpd/requests", json=request_payload
    )
    assert create_response.status_code == 201
    created = create_response.json()

    completion_payload = {
        "processor": "compliance@example.com",
        "resolution_notes": "Export transmis chiffré",
    }
    complete_response = await async_client.post(
        f"/api/v1/rgpd/requests/{created['id']}/complete",
        json=completion_payload,
    )
    assert complete_response.status_code == 200
    completed = complete_response.json()
    assert completed["status"] == "completed"

    list_response = await async_client.get("/api/v1/rgpd/requests")
    assert list_response.status_code == 200
    listed = list_response.json()
    assert any(item["id"] == created["id"] for item in listed)

    logs_response = await async_client.get("/api/v1/audit/logs")
    assert logs_response.status_code == 200
    events = logs_response.json()["items"]
    assert any(event["event_type"] == "rgpd.request.registered" for event in events)
    assert any(event["event_type"] == "rgpd.request.completed" for event in events)


@pytest.mark.asyncio
async def test_retention_job_archives_and_purges(async_client, db_session) -> None:
    # Inject an old audit log so the retention job has a target.
    very_old = datetime.now(timezone.utc) - timedelta(days=400)
    db_session.add(
        AuditLog(
            id=uuid4(),
            organization_id="acme",
            module="planning",
            event_type="planning.created",
            action="seed",
            actor_type=None,
            actor_id=None,
            target_type=None,
            target_id=None,
            payload_version=1,
            payload={},
            signature="seed-signature",
            created_at=very_old.replace(tzinfo=None),
        )
    )
    db_session.commit()

    update_response = await async_client.put(
        "/api/v1/audit/organizations/acme/retention",
        json={"retention_days": 30, "archive_after_days": 15},
    )
    assert update_response.status_code == 200

    run_response = await async_client.post(
        "/api/v1/audit/organizations/acme/retention/run"
    )
    assert run_response.status_code == 200
    summary = run_response.json()
    assert summary["organization_id"] == "acme"
    assert summary["purged_count"] >= 1

    logs_response = await async_client.get(
        "/api/v1/audit/logs", params={"module": "retention"}
    )
    assert logs_response.status_code == 200
    module_events = logs_response.json()["items"]
    assert any(
        event["event_type"] == "audit.retention.policy_updated"
        for event in module_events
    )
    assert any(
        event["event_type"] == "audit.retention.executed"
        for event in module_events
    )
