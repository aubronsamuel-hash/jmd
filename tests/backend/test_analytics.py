from __future__ import annotations

import base64
from datetime import datetime, timedelta
from decimal import Decimal

import pytest

from backend.models.analytics import (
    AnalyticsEquipmentIncident,
    AnalyticsMissionEvent,
    AnalyticsPayrollRecord,
)


@pytest.mark.asyncio
async def test_analytics_dashboard_returns_expected_metrics(async_client, db_session) -> None:
    """Dashboard endpoint should aggregate KPIs, heatmap and latencies."""

    base = datetime.utcnow().replace(hour=8, minute=0, second=0, microsecond=0)
    following = base + timedelta(days=1)
    event_one = AnalyticsMissionEvent(
        mission_code="M-001",
        project_code="PRJ-1",
        location_code="PARIS",
        team_name="Equipe A",
        start_time=base,
        end_time=base + timedelta(hours=4),
        actual_start_time=base,
        actual_end_time=base + timedelta(hours=3, minutes=30),
        actual_hours=Decimal("3.50"),
        status="completed",
        updated_at=datetime.utcnow() - timedelta(minutes=5),
    )
    event_two = AnalyticsMissionEvent(
        mission_code="M-002",
        project_code="PRJ-1",
        location_code="PARIS",
        team_name="Equipe A",
        start_time=following + timedelta(hours=6),
        end_time=following + timedelta(hours=10),
        actual_hours=Decimal("3.00"),
        status="completed",
        updated_at=datetime.utcnow() - timedelta(minutes=4),
    )
    other_event = AnalyticsMissionEvent(
        mission_code="M-999",
        project_code="PRJ-2",
        location_code="LYON",
        team_name="Equipe B",
        start_time=base,
        end_time=base + timedelta(hours=2),
        status="validated",
        updated_at=datetime.utcnow() - timedelta(minutes=2),
    )
    db_session.add_all([event_one, event_two, other_event])
    db_session.flush()

    db_session.add_all(
        [
            AnalyticsPayrollRecord(
                mission_event_id=event_one.id,
                amount=Decimal("420.00"),
                currency="EUR",
                recorded_at=datetime.utcnow() - timedelta(minutes=7),
                source="import",
            ),
            AnalyticsPayrollRecord(
                mission_event_id=event_two.id,
                amount=Decimal("360.00"),
                currency="EUR",
                recorded_at=datetime.utcnow() - timedelta(minutes=6),
                source="import",
            ),
            AnalyticsPayrollRecord(
                mission_event_id=other_event.id,
                amount=Decimal("100.00"),
                currency="EUR",
                recorded_at=datetime.utcnow() - timedelta(minutes=1),
                source="import",
            ),
        ]
    )

    db_session.add_all(
        [
            AnalyticsEquipmentIncident(
                mission_event=event_one,
                project_code="PRJ-1",
                location_code="PARIS",
                team_name="Equipe A",
                occurred_at=datetime.utcnow() - timedelta(minutes=3),
                severity="high",
                description="Ampoule HS",
            ),
            AnalyticsEquipmentIncident(
                mission_event=other_event,
                project_code="PRJ-2",
                location_code="LYON",
                team_name="Equipe B",
                occurred_at=datetime.utcnow() - timedelta(minutes=2),
                severity="low",
            ),
        ]
    )
    db_session.commit()

    params = {
        "project": "PRJ-1",
        "location": "PARIS",
        "team": "Equipe A",
        "start_date": base.date().isoformat(),
        "end_date": following.date().isoformat(),
    }
    response = await async_client.get("/api/v1/analytics/dashboard", params=params)
    body = response.json()

    assert response.status_code == 200
    assert body["kpis"]["missions_count"] == 2
    assert body["kpis"]["scheduled_hours"] == pytest.approx(8.0)
    assert body["kpis"]["realized_hours"] == pytest.approx(6.5)
    assert body["kpis"]["coverage_rate"] == pytest.approx(6.5 / 8.0, rel=1e-3)
    assert body["kpis"]["payroll_total"] == pytest.approx(780.0)
    assert body["kpis"]["average_hourly_cost"] == pytest.approx(780.0 / 6.5, rel=1e-3)
    assert body["kpis"]["equipment_incidents"] == 1
    assert {cell["hour"] for cell in body["heatmap"]}
    expected_days = {base.date().isoformat(), following.date().isoformat()}
    assert {point["date"] for point in body["comparisons"]} == expected_days
    assert body["filters"]["project"] == "PRJ-1"

    for latency in body["dataset_latencies"]:
        if latency["latency_minutes"] is not None:
            assert latency["latency_minutes"] <= 15


@pytest.mark.asyncio
async def test_analytics_export_supports_multiple_formats(async_client, db_session) -> None:
    """Exports endpoint should produce encoded payloads for every format."""

    base = datetime.utcnow().replace(hour=9, minute=0, second=0, microsecond=0)
    event = AnalyticsMissionEvent(
        mission_code="EXP-001",
        project_code="EXP",
        location_code="NICE",
        team_name="Equipe Export",
        start_time=base,
        end_time=base + timedelta(hours=5),
        actual_hours=Decimal("4.50"),
        updated_at=datetime.utcnow() - timedelta(minutes=8),
    )
    db_session.add(event)
    db_session.flush()
    db_session.add(
        AnalyticsPayrollRecord(
            mission_event_id=event.id,
            amount=Decimal("600.00"),
            currency="EUR",
            recorded_at=datetime.utcnow() - timedelta(minutes=9),
        )
    )
    db_session.commit()

    csv_response = await async_client.get(
        "/api/v1/analytics/exports", params={"project": "EXP", "format": "csv"}
    )
    csv_body = csv_response.json()

    assert csv_response.status_code == 200
    assert csv_body["format"] == "csv"
    assert csv_body["content_type"] == "text/csv"
    assert csv_body["metadata"]["project"] == "EXP"
    assert len(csv_body["signature"]) == 64
    csv_payload = base64.b64decode(csv_body["data_base64"]).decode()
    assert "date" in csv_payload

    png_response = await async_client.get(
        "/api/v1/analytics/exports", params={"project": "EXP", "format": "png"}
    )
    png_body = png_response.json()
    png_bytes = base64.b64decode(png_body["data_base64"])

    assert png_response.status_code == 200
    assert png_body["content_type"] == "image/png"
    assert png_bytes.startswith(b"\x89PNG")

    pdf_response = await async_client.get(
        "/api/v1/analytics/exports", params={"project": "EXP", "format": "pdf"}
    )
    pdf_body = pdf_response.json()
    pdf_bytes = base64.b64decode(pdf_body["data_base64"])

    assert pdf_response.status_code == 200
    assert pdf_body["content_type"] == "application/pdf"
    assert pdf_bytes.startswith(b"%PDF")
