"""Notification service and delivery channels for planning events."""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Iterable, Mapping, MutableMapping, Sequence
from uuid import UUID

from backend.domain.artists import Artist
from backend.domain.planning import PlanningAssignment, PlanningResponse

logger = logging.getLogger(__name__)


class NotificationEventType(str, Enum):
    """Enumeration describing the supported notification events."""

    TEST = "notifications.test"
    PLANNING_CREATED = "planning.assigned"
    PLANNING_UPDATED = "planning.updated"
    PLANNING_REMINDER = "planning.reminder"


@dataclass(slots=True)
class NotificationMessage:
    """Normalized representation of a notification to be dispatched."""

    event: NotificationEventType
    subject: str
    body: str
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class NotificationDispatchReport:
    """Summary of a notification dispatch across the registered channels."""

    event: NotificationEventType
    subject: str
    body: str
    channels: list[str]
    metadata: dict[str, Any] = field(default_factory=dict)


class NotificationDeliveryError(RuntimeError):
    """Raised when one or more channels failed to deliver a notification."""

    def __init__(self, event: NotificationEventType, errors: Mapping[str, str]):
        message = f"Notification dispatch failed for event '{event.value}'"
        super().__init__(message)
        self.event = event
        self.errors = dict(errors)


@dataclass(slots=True)
class NotificationChannel:
    """Base notification channel used by the dispatcher."""

    name: str = field(init=False)

    def send(self, message: NotificationMessage) -> None:  # pragma: no cover - interface
        """Deliver a notification message."""

        raise NotImplementedError


@dataclass(slots=True)
class EmailNotificationChannel(NotificationChannel):
    """Simple email channel storing dispatched messages for inspection."""

    sender: str
    recipients: Sequence[str]
    deliveries: list[dict[str, Any]] = field(default_factory=list, init=False)

    def __post_init__(self) -> None:
        self.name = "email"
        self.recipients = tuple(item for item in self.recipients if item)

    def send(self, message: NotificationMessage) -> None:
        delivery = {
            "sender": self.sender,
            "recipients": list(self.recipients),
            "subject": message.subject,
            "body": message.body,
            "metadata": message.metadata,
        }
        self.deliveries.append(delivery)
        logger.info(
            "Email notification dispatched",
            extra={
                "channel": self.name,
                "event": message.event.value,
                "recipients": self.recipients,
            },
        )


@dataclass(slots=True)
class TelegramNotificationChannel(NotificationChannel):
    """Telegram channel storing dispatched payloads for observability."""

    bot_token: str
    chat_ids: Sequence[str]
    deliveries: list[dict[str, Any]] = field(default_factory=list, init=False)

    def __post_init__(self) -> None:
        self.name = "telegram"
        self.chat_ids = tuple(item for item in self.chat_ids if item)

    def send(self, message: NotificationMessage) -> None:
        delivery = {
            "bot_token": self.bot_token,
            "chat_ids": list(self.chat_ids),
            "text": message.body,
            "metadata": message.metadata,
        }
        self.deliveries.append(delivery)
        logger.info(
            "Telegram notification dispatched",
            extra={
                "channel": self.name,
                "event": message.event.value,
                "chat_ids": self.chat_ids,
            },
        )


class NotificationService:
    """Coordinate notification delivery across configured channels."""

    def __init__(self, channels: Iterable[NotificationChannel]):
        self._channels: list[NotificationChannel] = list(channels)
        self._history: list[NotificationMessage] = []

    @property
    def channels(self) -> Sequence[NotificationChannel]:
        """Return the configured channels."""

        return tuple(self._channels)

    @property
    def history(self) -> Sequence[NotificationMessage]:
        """Return the immutable history of dispatched notifications."""

        return tuple(self._history)

    def send_test_notification(self) -> NotificationDispatchReport:
        """Send a test message over all configured channels."""

        message = NotificationMessage(
            event=NotificationEventType.TEST,
            subject="Notification de test",
            body=(
                "Message de test pour valider la configuration des canaux de notification."
            ),
            metadata={"purpose": "connectivity-check"},
        )
        channels = self._dispatch(message)
        return NotificationDispatchReport(
            event=message.event,
            subject=message.subject,
            body=message.body,
            channels=channels,
            metadata=message.metadata,
        )

    def notify_planning_event(
        self,
        planning: PlanningResponse,
        artists: Sequence[Artist] | None,
        *,
        event_type: NotificationEventType,
    ) -> NotificationDispatchReport:
        """Send a notification related to a planning lifecycle event."""

        if event_type == NotificationEventType.TEST:
            raise ValueError("Planning events cannot use the test notification type")

        message = self._compose_planning_message(planning, artists, event_type)
        channels = self._dispatch(message)
        return NotificationDispatchReport(
            event=message.event,
            subject=message.subject,
            body=message.body,
            channels=channels,
            metadata=message.metadata,
        )

    def _dispatch(self, message: NotificationMessage) -> list[str]:
        """Send a notification to all configured channels and collect the results."""

        dispatched: list[str] = []
        errors: MutableMapping[str, str] = {}

        for channel in self._channels:
            try:
                channel.send(message)
            except Exception as exc:  # pragma: no cover - defensive logging
                errors[channel.name] = str(exc)
                logger.exception(
                    "Notification delivery error",
                    extra={"channel": channel.name, "event": message.event.value},
                )
            else:
                dispatched.append(channel.name)

        if errors:
            raise NotificationDeliveryError(message.event, errors)

        self._history.append(message)
        return dispatched

    def _compose_planning_message(
        self,
        planning: PlanningResponse,
        artists: Sequence[Artist] | None,
        event_type: NotificationEventType,
    ) -> NotificationMessage:
        """Build a channel-agnostic message for a planning event."""

        title_map = {
            NotificationEventType.PLANNING_CREATED: "Nouvelle affectation planifiee",
            NotificationEventType.PLANNING_UPDATED: "Planning mis a jour",
            NotificationEventType.PLANNING_REMINDER: "Rappel planning J-1",
        }
        prefix = title_map.get(event_type, "Notification planning")
        subject = f"{prefix} - {planning.event_date.isoformat()}"

        artist_lookup = {
            artist.id: artist.name for artist in (artists or [])
        }
        assignments_lines = [
            self._format_assignment(assignment, artist_lookup)
            for assignment in planning.assignments
        ]

        body_lines = [
            subject,
            "",
            f"Planning: {planning.planning_id}",
            f"Date: {planning.event_date.isoformat()}",
        ]
        if assignments_lines:
            body_lines.append("Affectations:")
            body_lines.extend(assignments_lines)
        else:
            body_lines.append("Aucune affectation n'est enregistree.")

        metadata = {
            "planning_id": str(planning.planning_id),
            "event_type": event_type.value,
            "event_date": planning.event_date.isoformat(),
            "assignment_count": len(planning.assignments),
        }

        return NotificationMessage(
            event=event_type,
            subject=subject,
            body="\n".join(body_lines),
            metadata=metadata,
        )

    @staticmethod
    def _format_assignment(
        assignment: PlanningAssignment, artist_lookup: Mapping[UUID, str]
    ) -> str:
        """Format an assignment line for notification content."""

        artist_name = artist_lookup.get(assignment.artist_id, str(assignment.artist_id))
        start = assignment.slot.start.strftime("%Y-%m-%d %H:%M")
        end = assignment.slot.end.strftime("%H:%M")
        return f"- {artist_name}: {start} -> {end}"


__all__ = [
    "EmailNotificationChannel",
    "NotificationChannel",
    "NotificationDeliveryError",
    "NotificationDispatchReport",
    "NotificationEventType",
    "NotificationMessage",
    "NotificationService",
    "TelegramNotificationChannel",
]
