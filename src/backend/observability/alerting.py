"""Alerting primitives used to react on metric thresholds."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Callable, Iterable, Mapping


@dataclass(slots=True)
class AlertEvent:
    """Alert raised by an evaluation rule."""

    name: str
    severity: str
    message: str
    labels: dict[str, str]
    triggered_at: datetime
    metadata: dict[str, object] = field(default_factory=dict)


@dataclass(slots=True)
class AlertRule:
    """Declarative alert rule evaluated against metric updates."""

    name: str
    severity: str
    summary: str
    predicate: Callable[[str, Mapping[str, str], float, Mapping[str, object]], bool]
    detail_builder: Callable[[str, Mapping[str, str], float, Mapping[str, object]], dict[str, object]]

    def evaluate(
        self,
        *,
        metric: str,
        labels: Mapping[str, str],
        value: float,
        metadata: Mapping[str, object],
    ) -> AlertEvent | None:
        if not self.predicate(metric, labels, value, metadata):
            return None
        details = self.detail_builder(metric, labels, value, metadata)
        message = details.pop("message", self.summary)
        return AlertEvent(
            name=self.name,
            severity=self.severity,
            message=message,
            labels=dict(labels),
            triggered_at=datetime.utcnow(),
            metadata=dict(details),
        )


class AlertChannel:
    """Base alert delivery channel storing events for verification."""

    def __init__(self, name: str) -> None:
        self.name = name
        self.deliveries: list[AlertEvent] = []

    def send(self, event: AlertEvent) -> None:
        self.deliveries.append(event)


class AlertingService:
    """Evaluate alert rules and dispatch events to registered channels."""

    def __init__(self, channels: Iterable[AlertChannel]):
        self._rules: list[AlertRule] = []
        self._channels: dict[str, AlertChannel] = {channel.name: channel for channel in channels}
        self.history: list[AlertEvent] = []

    @property
    def channels(self) -> Mapping[str, AlertChannel]:
        return dict(self._channels)

    def register_rule(self, rule: AlertRule) -> None:
        self._rules.append(rule)

    def evaluate(
        self,
        *,
        metric: str,
        labels: Mapping[str, str],
        value: float,
        metadata: Mapping[str, object],
        registry: "MetricsRegistry",
    ) -> None:
        for rule in self._rules:
            event = rule.evaluate(metric=metric, labels=labels, value=value, metadata=metadata)
            if event is None:
                continue
            event.metadata.setdefault("metric", metric)
            event.metadata.setdefault("value", value)
            event.metadata.setdefault("labels", dict(labels))
            event.metadata.setdefault("source", "metrics")
            event.metadata.setdefault("context", dict(metadata))
            self.history.append(event)
            for channel in self._channels.values():
                channel.send(event)


__all__ = [
    "AlertChannel",
    "AlertEvent",
    "AlertRule",
    "AlertingService",
]
