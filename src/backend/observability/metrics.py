"""In-memory metrics registry with Prometheus exposition support."""

from __future__ import annotations

import math
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Iterable, Mapping


def _labels_key(labels: Mapping[str, Any] | None) -> tuple[tuple[str, str], ...]:
    if not labels:
        return ()
    return tuple(sorted((str(key), str(value)) for key, value in labels.items()))


def _format_labels(labels: Mapping[str, Any] | None) -> str:
    if not labels:
        return ""
    parts = [f'{key}="{value}"' for key, value in sorted(labels.items())]
    return "{" + ",".join(parts) + "}"


def _percentile(values: Iterable[float], percentile: float) -> float:
    series = sorted(float(value) for value in values)
    if not series:
        return 0.0
    index = max(0, min(len(series) - 1, math.ceil(percentile * len(series)) - 1))
    return series[index]


@dataclass(slots=True)
class SummarySnapshot:
    """Computed summary statistics for an observed metric."""

    count: int
    sum: float
    p95: float


class MetricsRegistry:
    """Collect counter, gauge and summary metrics for observability."""

    def __init__(self) -> None:
        self._counters: dict[tuple[str, tuple[tuple[str, str], ...]], float] = {}
        self._gauges: dict[tuple[str, tuple[tuple[str, str], ...]], float] = {}
        self._summaries: dict[tuple[str, tuple[tuple[str, str], ...]], list[float]] = {}
        self._alerting = None

    def bind_alerting(self, alerting: "AlertingService") -> None:
        """Register the alerting service to evaluate metric updates."""

        self._alerting = alerting

    def increment(self, name: str, amount: float = 1.0, *, labels: Mapping[str, Any] | None = None) -> None:
        """Increase a counter by the provided amount."""

        key = (name, _labels_key(labels))
        new_value = self._counters.get(key, 0.0) + amount
        self._counters[key] = new_value
        if self._alerting is not None:
            self._alerting.evaluate(
                metric=name,
                labels=dict(labels or {}),
                value=new_value,
                metadata={"kind": "counter", "delta": amount, "updated_at": datetime.now(timezone.utc)},
                registry=self,
            )

    def set_gauge(self, name: str, value: float, *, labels: Mapping[str, Any] | None = None) -> None:
        """Set a gauge to an absolute value."""

        key = (name, _labels_key(labels))
        self._gauges[key] = float(value)
        if self._alerting is not None:
            self._alerting.evaluate(
                metric=name,
                labels=dict(labels or {}),
                value=float(value),
                metadata={"kind": "gauge", "updated_at": datetime.now(timezone.utc)},
                registry=self,
            )

    def observe(self, name: str, value: float, *, labels: Mapping[str, Any] | None = None) -> None:
        """Record a new value for a summary metric."""

        key = (name, _labels_key(labels))
        bucket = self._summaries.setdefault(key, [])
        bucket.append(float(value))
        snapshot = self.get_summary(name, labels)
        if self._alerting is not None:
            self._alerting.evaluate(
                metric=name,
                labels=dict(labels or {}),
                value=snapshot.p95,
                metadata={
                    "kind": "summary",
                    "stat": "p95",
                    "count": snapshot.count,
                    "sum": snapshot.sum,
                    "last": float(value),
                    "updated_at": datetime.now(timezone.utc),
                },
                registry=self,
            )

    def get_counter(self, name: str, labels: Mapping[str, Any] | None = None) -> float:
        """Return the current value of a counter."""

        return self._counters.get((name, _labels_key(labels)), 0.0)

    def get_gauge(self, name: str, labels: Mapping[str, Any] | None = None) -> float:
        """Return the current value of a gauge."""

        return self._gauges.get((name, _labels_key(labels)), 0.0)

    def get_summary(self, name: str, labels: Mapping[str, Any] | None = None) -> SummarySnapshot:
        """Return summary statistics for the provided metric."""

        values = self._summaries.get((name, _labels_key(labels)), [])
        total = sum(values)
        return SummarySnapshot(count=len(values), sum=total, p95=_percentile(values, 0.95))

    def render_prometheus(self) -> str:
        """Render metrics into the Prometheus text exposition format."""

        lines: list[str] = []
        counter_names = sorted({name for name, _ in self._counters.keys()})
        for name in counter_names:
            lines.append(f"# TYPE {name} counter")
            for (metric_name, labels_key), value in sorted(self._counters.items()):
                if metric_name != name:
                    continue
                labels_dict = dict(labels_key)
                lines.append(f"{name}{_format_labels(labels_dict)} {value}")
        summary_names = sorted({name for name, _ in self._summaries.keys()})
        for name in summary_names:
            lines.append(f"# TYPE {name} summary")
            for (metric_name, labels_key), values in sorted(self._summaries.items()):
                if metric_name != name:
                    continue
                labels_dict = dict(labels_key)
                count = len(values)
                total = sum(values)
                p95 = _percentile(values, 0.95)
                label_repr = _format_labels(labels_dict)
                lines.append(f"{name}_count{label_repr} {count}")
                lines.append(f"{name}_sum{label_repr} {total}")
                lines.append(f"{name}_p95{label_repr} {p95}")
        gauge_names = sorted({name for name, _ in self._gauges.keys()})
        for name in gauge_names:
            lines.append(f"# TYPE {name} gauge")
            for (metric_name, labels_key), value in sorted(self._gauges.items()):
                if metric_name != name:
                    continue
                labels_dict = dict(labels_key)
                lines.append(f"{name}{_format_labels(labels_dict)} {value}")
        return "\n".join(lines) + ("\n" if lines else "")


class NoopMetricsRegistry(MetricsRegistry):
    """Drop-in registry used before setup when instrumentation is disabled."""

    def __init__(self) -> None:  # pragma: no cover - trivial fallback
        super().__init__()

    def bind_alerting(self, alerting: "AlertingService") -> None:  # pragma: no cover - noop
        return None

    def increment(self, name: str, amount: float = 1.0, *, labels: Mapping[str, Any] | None = None) -> None:  # pragma: no cover - noop
        return None

    def set_gauge(self, name: str, value: float, *, labels: Mapping[str, Any] | None = None) -> None:  # pragma: no cover - noop
        return None

    def observe(self, name: str, value: float, *, labels: Mapping[str, Any] | None = None) -> None:  # pragma: no cover - noop
        return None

    def render_prometheus(self) -> str:  # pragma: no cover - noop
        return ""


__all__ = [
    "MetricsRegistry",
    "NoopMetricsRegistry",
    "SummarySnapshot",
]
