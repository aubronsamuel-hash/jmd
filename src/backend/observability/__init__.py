"""Public helpers exposing observability utilities to the codebase."""

from __future__ import annotations

from contextlib import contextmanager
from typing import Iterator

from .alerting import AlertingService
from .context import (
    clear_attributes,
    get_attribute,
    get_context,
    reset_context,
    update_attributes,
)
from .metrics import MetricsRegistry, NoopMetricsRegistry
from .setup import ObservabilityComponents, setup_observability
from .tracing import ObservabilityTracer, _NoopTracer, trace as _trace

_tracer: ObservabilityTracer | _NoopTracer = _NoopTracer()
_metrics: MetricsRegistry = NoopMetricsRegistry()
_alerting: AlertingService | None = None


def bind_components(components: ObservabilityComponents) -> None:
    """Expose the concrete observability components to helper functions."""

    global _tracer, _metrics, _alerting
    _tracer = components.tracer
    _metrics = components.metrics
    _alerting = components.alerting


def get_tracer() -> ObservabilityTracer | _NoopTracer:
    return _tracer


def get_metrics() -> MetricsRegistry:
    return _metrics


def get_alerting_service() -> AlertingService | None:
    return _alerting


@contextmanager
def trace(name: str, **attributes) -> Iterator[object]:
    """Start a span with the configured tracer."""

    with _trace(_tracer, name, **attributes) as span:
        yield span


def record_event(name: str, **attributes) -> None:
    """Record an event on the currently active span when available."""

    if isinstance(_tracer, _NoopTracer):  # pragma: no cover - noop guard
        return
    _tracer.record_event(name, **attributes)


__all__ = [
    "AlertingService",
    "ObservabilityComponents",
    "bind_components",
    "clear_attributes",
    "get_alerting_service",
    "get_attribute",
    "get_context",
    "get_metrics",
    "get_tracer",
    "record_event",
    "reset_context",
    "setup_observability",
    "trace",
    "update_attributes",
]
