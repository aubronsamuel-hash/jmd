"""Integration service unit tests."""

from __future__ import annotations

from datetime import date, datetime, timedelta
from hashlib import sha256
from uuid import uuid4

import pytest

from backend.domain.artists import Artist, Availability
from backend.domain.planning import PlanningAssignment, PlanningResponse
from backend.integrations import (
    CalendarSyncService,
    InMemoryCalendarConnector,
    InMemoryStorageConnector,
    StorageGateway,
)


def _build_artist(name: str, slot_start: datetime) -> Artist:
    availability = Availability(start=slot_start, end=slot_start + timedelta(hours=1))
    return Artist(id=uuid4(), name=name, availabilities=[availability])


def _build_planning(artists: list[Artist], *, overlap: bool = False) -> PlanningResponse:
    assignments: list[PlanningAssignment] = []
    for index, artist in enumerate(artists):
        slot = artist.availabilities[0]
        if overlap and index:
            slot = Availability(start=artists[0].availabilities[0].start, end=slot.end)
        assignments.append(
            PlanningAssignment(artist_id=artist.id, slot=slot)
        )
    return PlanningResponse(
        planning_id=uuid4(),
        event_date=date(2024, 5, 12),
        assignments=assignments,
    )


def test_calendar_service_exports_ics_with_metadata() -> None:
    """Calendar synchronisation should produce ICS payloads enriched with metadata."""

    base = datetime(2024, 5, 12, 10, 0)
    artists = [_build_artist("Alice", base)]
    planning = _build_planning(artists)
    connector = InMemoryCalendarConnector("google")
    service = CalendarSyncService([connector], calendar_name="Planning Test")

    ics_payload = service.synchronize_planning(planning, artists=artists)

    assert service.export_log == (("google", ics_payload),)
    assert "BEGIN:VEVENT" in ics_payload
    assert "X-JMD-PLANNING_ID" in ics_payload

    report = service.ingest_webhook("google", ics_payload)

    assert len(report.events) == 1
    event = report.events[0]
    assert event.metadata["planning_id"] == str(planning.planning_id)
    assert event.summary.startswith("Alice")
    assert not report.conflicts


def test_calendar_service_detects_conflicts_from_webhook() -> None:
    """Webhook ingestion should highlight overlapping events."""

    base = datetime(2024, 6, 1, 9, 0)
    artists = [_build_artist("Alice", base), _build_artist("Bob", base + timedelta(minutes=30))]
    planning = _build_planning(artists, overlap=True)
    connector = InMemoryCalendarConnector("outlook")
    service = CalendarSyncService([connector])

    ics_payload = service.synchronize_planning(planning, artists=artists)
    report = service.ingest_webhook("outlook", ics_payload)

    assert len(report.events) == 2
    assert len(report.conflicts) == 1
    conflict = report.conflicts[0]
    assert conflict.first.uid != conflict.second.uid


def test_storage_gateway_publishes_planning_summary() -> None:
    """Storage gateway should persist a text summary with metadata."""

    base = datetime(2024, 5, 20, 14, 0)
    artists = [_build_artist("Charlie", base)]
    planning = _build_planning(artists)
    connector = InMemoryStorageConnector()
    gateway = StorageGateway([connector])

    results = gateway.publish_planning_document(planning, artists=artists)

    assert len(results) == 1
    result = results[0]
    assert result.connector == "memory"
    assert result.metadata["planning_id"] == str(planning.planning_id)
    stored = connector.documents[0]
    content = stored.content.decode("utf-8")
    assert "Planning" in content
    assert sha256(stored.content).hexdigest() == result.checksum
    assert gateway.history == tuple(results)


@pytest.mark.parametrize(
    "raw,expected",
    [
        ("google,outlook", ["google", "outlook"]),
        ("memory", ["memory"]),
    ],
)
def test_settings_list_parsing(raw: str, expected: list[str]) -> None:
    """Comma separated configuration should be accepted for connector lists."""

    from backend.config import Settings

    settings = Settings(
        BACKEND_CALENDAR_CONNECTORS=raw,
        BACKEND_STORAGE_CONNECTORS=raw,
    )

    assert settings.calendar_connectors == expected
    assert settings.storage_connectors == expected
