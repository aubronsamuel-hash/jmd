"""Context management utilities for observability features."""

from __future__ import annotations

from contextvars import ContextVar
from dataclasses import dataclass, field
from typing import Any


@dataclass
class ObservabilityContext:
    """Mutable context shared across traces, logs and metrics."""

    trace_id: str | None = None
    span_stack: list[str] = field(default_factory=list)
    attributes: dict[str, Any] = field(default_factory=dict)


_context_var: ContextVar[ObservabilityContext | None] = ContextVar(
    "backend_observability_context", default=None
)


def get_context() -> ObservabilityContext:
    """Return the current observability context, creating one when missing."""

    context = _context_var.get()
    if context is None:
        context = ObservabilityContext()
        _context_var.set(context)
    return context


def reset_context(trace_id: str | None = None) -> ObservabilityContext:
    """Reset the observability context for a new execution scope."""

    context = ObservabilityContext(trace_id=trace_id)
    _context_var.set(context)
    return context


def set_trace_id(trace_id: str) -> None:
    """Attach a trace identifier to the current context."""

    context = get_context()
    context.trace_id = trace_id


def push_span(span_id: str) -> None:
    """Push a span identifier on the context stack."""

    context = get_context()
    context.span_stack.append(span_id)


def pop_span() -> None:
    """Pop the latest span identifier from the stack if present."""

    context = get_context()
    if context.span_stack:
        context.span_stack.pop()


def current_span_id() -> str | None:
    """Return the active span identifier when available."""

    context = get_context()
    if not context.span_stack:
        return None
    return context.span_stack[-1]


def update_attributes(**attributes: Any) -> None:
    """Update contextual attributes shared with logs and traces."""

    context = get_context()
    for key, value in attributes.items():
        if value is not None:
            context.attributes[key] = value


def get_attribute(name: str, default: Any | None = None) -> Any:
    """Return a contextual attribute or a default placeholder."""

    context = get_context()
    return context.attributes.get(name, default)


def clear_attributes(*names: str) -> None:
    """Remove one or multiple contextual attributes."""

    context = get_context()
    for name in names:
        context.attributes.pop(name, None)


__all__ = [
    "ObservabilityContext",
    "get_context",
    "reset_context",
    "set_trace_id",
    "push_span",
    "pop_span",
    "current_span_id",
    "update_attributes",
    "get_attribute",
    "clear_attributes",
]
