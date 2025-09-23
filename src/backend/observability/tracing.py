"""Lightweight tracing primitives used across the backend."""

from __future__ import annotations

import time
from contextlib import contextmanager
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Callable, Iterator
from uuid import uuid4

from .context import current_span_id, get_context, pop_span, push_span, set_trace_id


@dataclass(slots=True)
class SpanEvent:
    """Event captured within a span for troubleshooting purposes."""

    name: str
    timestamp: datetime
    attributes: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class SpanRecord:
    """Immutable representation of a finished span."""

    trace_id: str
    span_id: str
    parent_span_id: str | None
    name: str
    started_at: datetime
    ended_at: datetime
    duration_seconds: float
    attributes: dict[str, Any] = field(default_factory=dict)
    status: str = "ok"
    events: list[SpanEvent] = field(default_factory=list)


class _Span:
    """Context manager used to manage span lifecycle."""

    def __init__(
        self,
        tracer: "ObservabilityTracer",
        name: str,
        *,
        attributes: dict[str, Any] | None = None,
    ) -> None:
        self._tracer = tracer
        self._name = name
        self._attributes = dict(attributes or {})
        self._trace_id: str | None = None
        self._span_id = uuid4().hex
        self._parent_id: str | None = None
        self._start_perf: float | None = None
        self._started_at: datetime | None = None
        self._events: list[SpanEvent] = []
        self._status = "ok"

    def __enter__(self) -> "_Span":
        self._trace_id, self._parent_id = self._tracer._enter_span(
            self._span_id, self._name, self._attributes
        )
        self._start_perf = time.perf_counter()
        self._started_at = datetime.now(timezone.utc)
        return self

    def __exit__(self, exc_type, exc, exc_tb) -> None:  # type: ignore[override]
        if exc is not None:
            self._status = "error"
            self._attributes.setdefault("error.type", exc_type.__name__ if exc_type else "Exception")
            self._attributes.setdefault("error.message", str(exc))
        ended_at = datetime.now(timezone.utc)
        duration = 0.0
        if self._start_perf is not None:
            duration = max(0.0, time.perf_counter() - self._start_perf)
        self._tracer._exit_span(
            trace_id=self._trace_id or uuid4().hex,
            span_id=self._span_id,
            parent_span_id=self._parent_id,
            name=self._name,
            started_at=self._started_at or ended_at,
            ended_at=ended_at,
            duration=duration,
            attributes=self._attributes,
            status=self._status,
            events=self._events,
        )

    def set_attribute(self, key: str, value: Any) -> None:
        """Add or replace an attribute on the span."""

        self._attributes[key] = value

    def record_event(self, name: str, **attributes: Any) -> None:
        """Append a structured event within the span."""

        self._events.append(
            SpanEvent(
                name=name,
                timestamp=datetime.now(timezone.utc),
                attributes=dict(attributes),
            )
        )


class ObservabilityTracer:
    """In-memory tracer storing finished spans for inspection."""

    def __init__(self) -> None:
        self._spans: list[SpanRecord] = []
        self._active: dict[str, _Span] = {}

    def start_span(self, name: str, *, attributes: dict[str, Any] | None = None) -> _Span:
        """Create a new span context manager."""

        return _Span(self, name, attributes=attributes)

    # The following helpers are intentionally private: they are used by _Span.
    def _enter_span(
        self, span_id: str, name: str, attributes: dict[str, Any]
    ) -> tuple[str, str | None]:
        context = get_context()
        if context.trace_id is None:
            trace_id = uuid4().hex
            set_trace_id(trace_id)
        else:
            trace_id = context.trace_id
        parent_span_id = current_span_id()
        push_span(span_id)
        self._active[span_id] = _SpanProxy(name=name, attributes=dict(attributes))
        return trace_id, parent_span_id

    def _exit_span(
        self,
        *,
        trace_id: str,
        span_id: str,
        parent_span_id: str | None,
        name: str,
        started_at: datetime,
        ended_at: datetime,
        duration: float,
        attributes: dict[str, Any],
        status: str,
        events: list[SpanEvent],
    ) -> None:
        pop_span()
        proxy = self._active.pop(span_id, None)
        if proxy is not None:
            # Merge attributes recorded after span start.
            proxy_attributes = proxy.attributes
            proxy_attributes.update(attributes)
            attributes = proxy_attributes
            events = proxy.events + events
        self._spans.append(
            SpanRecord(
                trace_id=trace_id,
                span_id=span_id,
                parent_span_id=parent_span_id,
                name=name,
                started_at=started_at,
                ended_at=ended_at,
                duration_seconds=duration,
                attributes=attributes,
                status=status,
                events=events,
            )
        )

    def get_spans(self, trace_id: str | None = None) -> list[SpanRecord]:
        """Return finished spans optionally filtered by trace identifier."""

        if trace_id is None:
            return list(self._spans)
        return [span for span in self._spans if span.trace_id == trace_id]

    def record_event(self, name: str, **attributes: Any) -> None:
        """Record an event on the currently active span if any."""

        active_id = current_span_id()
        if active_id is None:
            return
        proxy = self._active.get(active_id)
        if proxy is None:
            proxy = _SpanProxy(name=name, attributes={})
            self._active[active_id] = proxy
        proxy.events.append(
            SpanEvent(
                name=name,
                timestamp=datetime.now(timezone.utc),
                attributes=dict(attributes),
            )
        )


@dataclass
class _SpanProxy:
    """Store mutable data for spans while they are active."""

    name: str
    attributes: dict[str, Any]
    events: list[SpanEvent] = field(default_factory=list)


class _NoopSpan:
    """Context manager used when tracing is disabled."""

    def __enter__(self) -> "_NoopSpan":  # pragma: no cover - trivial
        return self

    def __exit__(self, exc_type, exc, exc_tb) -> None:  # pragma: no cover - trivial
        return None

    def set_attribute(self, key: str, value: Any) -> None:  # pragma: no cover - noop
        return None

    def record_event(self, name: str, **attributes: Any) -> None:  # pragma: no cover - noop
        return None


class _NoopTracer:
    """Tracer used before observability is initialised."""

    def start_span(self, name: str, *, attributes: dict[str, Any] | None = None) -> _NoopSpan:
        return _NoopSpan()

    def record_event(self, name: str, **attributes: Any) -> None:  # pragma: no cover - noop
        return None

    def get_spans(self, trace_id: str | None = None) -> list[SpanRecord]:  # pragma: no cover - noop
        return []


_noop_tracer = _NoopTracer()


@contextmanager
def trace(tracer: ObservabilityTracer | _NoopTracer, name: str, **attributes: Any) -> Iterator[_Span | _NoopSpan]:
    """Convenience context manager used by call sites."""

    span = tracer.start_span(name, attributes=attributes)
    manager = span.__enter__()
    try:
        yield manager
    except Exception as exc:
        span.__exit__(type(exc), exc, exc.__traceback__)
        raise
    else:
        span.__exit__(None, None, None)


__all__ = [
    "ObservabilityTracer",
    "SpanRecord",
    "SpanEvent",
    "trace",
    "_NoopTracer",
    "_NoopSpan",
]
