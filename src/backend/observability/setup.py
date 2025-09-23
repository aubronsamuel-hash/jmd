"""Factory assembling observability components for the FastAPI app."""

from __future__ import annotations

from dataclasses import dataclass

from fastapi import FastAPI

from backend.config import Settings

from .alerting import AlertChannel, AlertRule, AlertingService
from .logging import configure_structured_logging
from .metrics import MetricsRegistry
from .middleware import ObservabilityMiddleware
from .tracing import ObservabilityTracer


@dataclass(slots=True)
class ObservabilityComponents:
    """Bundle returned to the caller after setup."""

    tracer: ObservabilityTracer
    metrics: MetricsRegistry
    alerting: AlertingService


def setup_observability(app: FastAPI, settings: Settings) -> ObservabilityComponents:
    """Configure tracing, metrics, logging and alerting for the app."""

    tracer = ObservabilityTracer()
    metrics = MetricsRegistry()
    email_channel = AlertChannel("email")
    slack_channel = AlertChannel("slack")
    pagerduty_channel = AlertChannel("pagerduty")
    alerting = AlertingService([email_channel, slack_channel, pagerduty_channel])
    metrics.bind_alerting(alerting)
    configure_structured_logging()
    latency_threshold_seconds = settings.observability_latency_threshold_ms / 1000.0
    app.add_middleware(
        ObservabilityMiddleware,
        tracer=tracer,
        metrics=metrics,
        latency_threshold_seconds=latency_threshold_seconds,
    )
    _register_default_rules(alerting, settings)
    return ObservabilityComponents(tracer=tracer, metrics=metrics, alerting=alerting)


def _register_default_rules(alerting: AlertingService, settings: Settings) -> None:
    """Install alert rules covering API errors, latency and jobs."""

    latency_threshold = settings.observability_latency_threshold_ms / 1000.0
    queue_threshold = settings.observability_queue_threshold

    def _counter_detail(metric: str, labels: dict[str, str], value: float, metadata: dict[str, object]) -> dict[str, object]:
        message = (
            f"Seuil critique atteint pour {metric}"
            f" ({labels.get('path', labels.get('organization', 'global'))})"
        )
        return {"message": message, "labels": dict(labels), "value": value}

    alerting.register_rule(
        AlertRule(
            name="api.5xx",
            severity="critical",
            summary="Erreurs 5xx consecutives detectees",
            predicate=lambda metric, labels, value, metadata: metric
            == "api_request_errors_total"
            and metadata.get("kind") == "counter"
            and metadata.get("delta", 0) > 0,
            detail_builder=_counter_detail,
        )
    )

    alerting.register_rule(
        AlertRule(
            name="api.latency",
            severity="warning",
            summary="Derive de latence sur les requetes API",
            predicate=lambda metric, labels, value, metadata: metric
            == "api_request_duration_seconds"
            and metadata.get("kind") == "summary"
            and metadata.get("stat") == "p95"
            and value > latency_threshold,
            detail_builder=lambda metric, labels, value, metadata: {
                "message": (
                    "Latence p95 {path} = {value:.3f}s (> {threshold:.3f}s)"
                ).format(
                    path=labels.get("path", "unknown"),
                    value=value,
                    threshold=latency_threshold,
                )
            },
        )
    )

    alerting.register_rule(
        AlertRule(
            name="audit.job.failure",
            severity="critical",
            summary="Echec du job retention/audit",
            predicate=lambda metric, labels, value, metadata: metric
            == "retention_job_failures_total"
            and metadata.get("kind") == "counter"
            and metadata.get("delta", 0) > 0,
            detail_builder=_counter_detail,
        )
    )

    alerting.register_rule(
        AlertRule(
            name="calendar.queue",
            severity="warning",
            summary="File de synchronisation calendrier en saturation",
            predicate=lambda metric, labels, value, metadata: metric
            == "calendar_sync_pending_exports"
            and value >= queue_threshold,
            detail_builder=lambda metric, labels, value, metadata: {
                "message": (
                    "{calendar}: {value} exports en attente (seuil {threshold})"
                ).format(
                    calendar=labels.get("calendar", "default"),
                    value=int(value),
                    threshold=queue_threshold,
                )
            },
        )
    )


__all__ = ["ObservabilityComponents", "setup_observability"]
