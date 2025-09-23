"""Calendar integration helpers for planning synchronisation."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Dict, Iterable, List, Mapping, MutableMapping, Sequence

from backend.domain.artists import Artist
from backend.domain.planning import PlanningAssignment, PlanningResponse


@dataclass(slots=True)
class CalendarEvent:
    """Representation of a calendar event synchronised via ICS."""

    uid: str
    start: datetime
    end: datetime
    summary: str
    description: str | None = None
    location: str | None = None
    updated_at: datetime | None = None
    metadata: dict[str, str] = field(default_factory=dict)


@dataclass(slots=True)
class CalendarConflict:
    """Describe a detected conflict between two events."""

    first: CalendarEvent
    second: CalendarEvent


@dataclass(slots=True)
class CalendarWebhookReport:
    """Summarise the result of a webhook ingestion."""

    source: str
    events: list[CalendarEvent]
    conflicts: list[CalendarConflict]


class CalendarSyncError(RuntimeError):
    """Raised when synchronising events across connectors fails."""

    def __init__(self, errors: Mapping[str, str]):
        message = "Calendar synchronisation failed"
        super().__init__(message)
        self.errors = dict(errors)


class CalendarConnector:
    """Base connector used to publish ICS payloads."""

    name: str

    def publish(self, ics_payload: str) -> None:  # pragma: no cover - interface
        """Publish an ICS payload to the external calendar service."""

        raise NotImplementedError


class InMemoryCalendarConnector(CalendarConnector):
    """Simple connector storing published payloads for assertions."""

    def __init__(self, name: str, *, endpoint: str | None = None):
        self.name = name
        self.endpoint = endpoint
        self.published_payloads: list[dict[str, str | None]] = []

    def publish(self, ics_payload: str) -> None:
        self.published_payloads.append({"endpoint": self.endpoint, "payload": ics_payload})


class CalendarSyncService:
    """Coordinate calendar synchronisation across configured connectors."""

    def __init__(self, connectors: Iterable[CalendarConnector], *, calendar_name: str = "JMD Planning"):
        self._connectors: list[CalendarConnector] = list(connectors)
        self._calendar_name = calendar_name
        self._exports: list[tuple[str, str]] = []
        self._webhook_reports: list[CalendarWebhookReport] = []

    @property
    def connectors(self) -> Sequence[CalendarConnector]:
        """Return the registered connectors."""

        return tuple(self._connectors)

    @property
    def calendar_name(self) -> str:
        """Return the configured calendar name."""

        return self._calendar_name

    @property
    def export_log(self) -> Sequence[tuple[str, str]]:
        """Return the history of exported payloads."""

        return tuple(self._exports)

    @property
    def webhook_reports(self) -> Sequence[CalendarWebhookReport]:
        """Return the history of webhook reports."""

        return tuple(self._webhook_reports)

    def synchronize_planning(
        self, planning: PlanningResponse, artists: Sequence[Artist] | None = None
    ) -> str:
        """Build ICS payloads for a planning and publish them."""

        events = self._build_events(planning, artists or [])
        ics_payload = _export_ics(events, calendar_name=self._calendar_name)
        errors: MutableMapping[str, str] = {}

        for connector in self._connectors:
            try:
                connector.publish(ics_payload)
            except Exception as exc:  # pragma: no cover - defensive logging
                errors[connector.name] = str(exc)
            else:
                self._exports.append((connector.name, ics_payload))

        if errors:
            raise CalendarSyncError(errors)

        return ics_payload

    def ingest_webhook(self, source: str, payload: str) -> CalendarWebhookReport:
        """Parse a webhook payload and detect conflicting events."""

        events = _parse_ics(payload)
        conflicts = _detect_conflicts(events)
        report = CalendarWebhookReport(source=source, events=events, conflicts=conflicts)
        self._webhook_reports.append(report)
        return report

    @staticmethod
    def _build_events(planning: PlanningResponse, artists: Sequence[Artist]) -> list[CalendarEvent]:
        lookup = {artist.id: artist.name for artist in artists}
        events: list[CalendarEvent] = []

        for index, assignment in enumerate(planning.assignments):
            events.append(
                _event_from_assignment(
                    planning=planning,
                    assignment=assignment,
                    artist_name=lookup.get(assignment.artist_id),
                    sequence=index,
                )
            )

        return events


def _event_from_assignment(
    planning: PlanningResponse,
    assignment: PlanningAssignment,
    *,
    artist_name: str | None,
    sequence: int,
) -> CalendarEvent:
    """Create a calendar event from a planning assignment."""

    display_name = artist_name or str(assignment.artist_id)
    subject = f"{display_name} - {planning.event_date.isoformat()}"
    description = (
        "Affectation planning {planning_id} pour {artist}".format(
            planning_id=planning.planning_id, artist=display_name
        )
    )
    metadata = {
        "planning_id": str(planning.planning_id),
        "artist_id": str(assignment.artist_id),
        "slot_start": assignment.slot.start.isoformat(),
        "slot_end": assignment.slot.end.isoformat(),
    }
    return CalendarEvent(
        uid=f"{planning.planning_id}-{sequence}",
        start=assignment.slot.start,
        end=assignment.slot.end,
        summary=subject,
        description=description,
        updated_at=datetime.now(timezone.utc),
        metadata=metadata,
    )


def _export_ics(events: Sequence[CalendarEvent], *, calendar_name: str) -> str:
    """Serialize events to a RFC 5545 compatible ICS payload."""

    lines = [
        "BEGIN:VCALENDAR",
        "VERSION:2.0",
        "PRODID:-//JMD//Planning//FR",
        f"X-WR-CALNAME:{calendar_name}",
    ]
    for event in events:
        lines.extend(_event_to_ics_lines(event))
    lines.append("END:VCALENDAR")
    return "\r\n".join(lines) + "\r\n"


def _event_to_ics_lines(event: CalendarEvent) -> list[str]:
    """Return ICS lines representing a single event."""

    dtstamp = event.updated_at or datetime.now(timezone.utc)
    lines = [
        "BEGIN:VEVENT",
        f"UID:{event.uid}",
        f"DTSTAMP:{_format_datetime(dtstamp)}",
        f"DTSTART:{_format_datetime(event.start)}",
        f"DTEND:{_format_datetime(event.end)}",
        f"SUMMARY:{_escape_text(event.summary)}",
    ]
    if event.description:
        lines.append(f"DESCRIPTION:{_escape_text(event.description)}")
    if event.location:
        lines.append(f"LOCATION:{_escape_text(event.location)}")
    if event.updated_at:
        lines.append(f"LAST-MODIFIED:{_format_datetime(event.updated_at)}")
    for key, value in sorted(event.metadata.items()):
        formatted_key = key.upper().replace(" ", "-")
        lines.append(f"X-JMD-{formatted_key}:{_escape_text(value)}")
    lines.append("END:VEVENT")
    return lines


def _format_datetime(value: datetime) -> str:
    """Format datetime values following the ICS specification."""

    if value.tzinfo is None:
        return value.strftime("%Y%m%dT%H%M%S")
    return value.astimezone(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def _escape_text(value: str) -> str:
    return (
        value.replace("\\", "\\\\")
        .replace("\n", "\\n")
        .replace(",", "\\,")
        .replace(";", "\\;")
    )


def _parse_ics(payload: str) -> list[CalendarEvent]:
    """Parse an ICS payload and return the contained events."""

    events: list[CalendarEvent] = []
    current: Dict[str, str] | None = None

    for line in _unfold_ics_lines(payload):
        if line == "BEGIN:VEVENT":
            current = {}
            continue
        if line == "END:VEVENT":
            if current:
                events.append(_event_from_raw(current))
            current = None
            continue
        if current is None:
            continue
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        key = key.upper()
        if ";" in key:
            key = key.split(";", 1)[0]
        current[key] = value

    return events


def _event_from_raw(raw: Mapping[str, str]) -> CalendarEvent:
    """Build an event from raw ICS properties."""

    metadata = {
        key.removeprefix("X-JMD-").lower(): value
        for key, value in raw.items()
        if key.startswith("X-JMD-")
    }
    return CalendarEvent(
        uid=raw.get("UID", ""),
        start=_parse_datetime(raw.get("DTSTART")),
        end=_parse_datetime(raw.get("DTEND")),
        summary=_unescape_text(raw.get("SUMMARY", "")),
        description=_unescape_text(raw.get("DESCRIPTION")) if raw.get("DESCRIPTION") else None,
        location=_unescape_text(raw.get("LOCATION")) if raw.get("LOCATION") else None,
        updated_at=_parse_datetime(raw.get("LAST-MODIFIED")) if raw.get("LAST-MODIFIED") else None,
        metadata={key: _unescape_text(value) for key, value in metadata.items()},
    )


def _parse_datetime(value: str | None) -> datetime:
    if not value:
        raise ValueError("ICS datetime value missing")
    value = value.strip()
    if value.endswith("Z"):
        return datetime.strptime(value, "%Y%m%dT%H%M%SZ").replace(tzinfo=timezone.utc)
    if "T" in value:
        return datetime.strptime(value, "%Y%m%dT%H%M%S")
    return datetime.strptime(value, "%Y%m%d")


def _unescape_text(value: str) -> str:
    return (
        value.replace("\\n", "\n")
        .replace("\\,", ",")
        .replace("\\;", ";")
        .replace("\\\\", "\\")
    )


def _unfold_ics_lines(payload: str) -> List[str]:
    """Unfold folded ICS lines according to RFC 5545."""

    raw_lines = payload.replace("\r\n", "\n").split("\n")
    unfolded: List[str] = []
    buffer: str | None = None

    for line in raw_lines:
        if not line:
            continue
        if line.startswith(" ") or line.startswith("\t"):
            if buffer is None:
                buffer = line[1:]
            else:
                buffer += line[1:]
            continue
        if buffer is not None:
            unfolded.append(buffer)
        buffer = line
    if buffer is not None:
        unfolded.append(buffer)
    return unfolded


def _detect_conflicts(events: Sequence[CalendarEvent]) -> list[CalendarConflict]:
    """Return overlapping events found in the provided collection."""

    conflicts: list[CalendarConflict] = []
    sorted_events = sorted(events, key=lambda item: item.start)
    for index, current in enumerate(sorted_events):
        for candidate in sorted_events[index + 1 :]:
            if current.end <= candidate.start:
                break
            if current.start < candidate.end:
                conflicts.append(CalendarConflict(first=current, second=candidate))
    return conflicts


__all__ = [
    "CalendarConnector",
    "CalendarEvent",
    "CalendarSyncError",
    "CalendarSyncService",
    "CalendarWebhookReport",
    "InMemoryCalendarConnector",
]
