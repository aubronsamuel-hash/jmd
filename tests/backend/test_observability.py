from __future__ import annotations

from datetime import datetime, timedelta

import pytest


@pytest.mark.asyncio
async def test_metrics_endpoint_exposes_request_metrics(async_client) -> None:
    """Metrics endpoint should expose request latency and counters."""

    response = await async_client.get("/api/v1/health")
    assert response.status_code == 200
    trace_id = response.headers.get("X-Trace-Id")
    assert trace_id

    metrics_response = await async_client.get("/metrics")
    assert metrics_response.status_code == 200
    metrics_body = metrics_response.text
    assert (
        'api_request_duration_seconds_count{method="GET",path="/api/v1/health",status="200"}'
        in metrics_body
    )
    assert (
        'api_request_total{method="GET",path="/api/v1/health",status="200"}'
        in metrics_body
    )

    transport = async_client._transport
    app = transport.app
    spans = [span for span in app.state.tracer.get_spans() if span.name == "http.request"]
    assert any(span.attributes.get("path") == "/api/v1/health" for span in spans)


@pytest.mark.asyncio
async def test_alert_triggered_on_server_error(async_client, monkeypatch) -> None:
    """A server error should raise an alert and increment error metrics."""

    transport = async_client._transport
    app = transport.app
    notification_service = app.state.notification_service

    def _raise_notification() -> None:
        raise RuntimeError("boom")

    monkeypatch.setattr(notification_service, "send_test_notification", _raise_notification)

    with pytest.raises(RuntimeError):
        await async_client.post("/api/v1/notifications/test")

    metrics_body = (await async_client.get("/metrics")).text
    assert (
        'api_request_errors_total{method="POST",path="/api/v1/notifications/test",status="500"}'
        in metrics_body
    )

    alerting = app.state.alerting_service
    assert any(event.name == "api.5xx" for event in alerting.history)
    for channel in ("email", "slack", "pagerduty"):
        assert any(event.name == "api.5xx" for event in alerting.channels[channel].deliveries)


@pytest.mark.asyncio
async def test_retention_job_metrics_and_alert(async_client, db_session, monkeypatch) -> None:
    """Retention job metrics should be exposed and failures raise alerts."""

    transport = async_client._transport
    app = transport.app
    audit_service = app.state.audit_service
    metrics = app.state.metrics

    summary = audit_service.run_retention_job(session=db_session, organization_id="default-org")
    stats = metrics.get_summary(
        "retention_job_duration_seconds", {"organization": "default-org"}
    )
    assert stats.count == 1
    assert metrics.get_gauge(
        "retention_job_archived_records", {"organization": "default-org"}
    ) == float(summary.archived_count)

    def _raise_policy(*_args, **_kwargs):
        raise RuntimeError("failure")

    monkeypatch.setattr(audit_service, "get_retention_policy", _raise_policy)
    with pytest.raises(RuntimeError):
        audit_service.run_retention_job(session=db_session, organization_id="default-org")

    assert (
        metrics.get_counter("retention_job_failures_total", {"organization": "default-org"})
        >= 1
    )
    alerting = app.state.alerting_service
    assert any(event.name == "audit.job.failure" for event in alerting.history)


@pytest.mark.asyncio
async def test_calendar_queue_alert(async_client, monkeypatch) -> None:
    """Calendar connector failures should raise queue saturation alerts."""

    transport = async_client._transport
    app = transport.app
    calendar_service = app.state.calendar_service

    failing_connector = calendar_service.connectors[0]

    def _failing_publish(_payload: str) -> None:
        raise RuntimeError("unavailable")

    monkeypatch.setattr(failing_connector, "publish", _failing_publish)

    event_date = datetime.utcnow() - timedelta(days=1)
    payload = {
        "event_date": event_date.date().isoformat(),
        "artists": [
            {
                "name": "Zeta",
                "availabilities": [
                    {
                        "start": event_date.isoformat(),
                        "end": (event_date + timedelta(hours=1)).isoformat(),
                    }
                ],
            }
        ],
    }

    response = await async_client.post("/api/v1/plannings", json=payload)
    assert response.status_code == 201
    assert "X-Calendar-Error" in response.headers

    metrics = app.state.metrics
    gauge = metrics.get_gauge(
        "calendar_sync_pending_exports", {"calendar": calendar_service.calendar_name}
    )
    assert gauge >= 1.0

    alerting = app.state.alerting_service
    assert any(event.name == "calendar.queue" for event in alerting.history)
