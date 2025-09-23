"""Storage gateway for publishing planning documents."""

from __future__ import annotations

from dataclasses import dataclass, field
from hashlib import sha256
from typing import Iterable, Mapping, MutableMapping, Sequence

from backend.domain.artists import Artist
from backend.domain.planning import PlanningAssignment, PlanningResponse


@dataclass(slots=True)
class StorageResult:
    """Describe the outcome of a storage operation."""

    connector: str
    document_name: str
    checksum: str
    size: int
    content_type: str
    metadata: dict[str, str] = field(default_factory=dict)


class StorageError(RuntimeError):
    """Raised when at least one storage connector fails."""

    def __init__(self, errors: Mapping[str, str]):
        message = "Document storage failed"
        super().__init__(message)
        self.errors = dict(errors)


class StorageConnector:
    """Base connector used by the storage gateway."""

    name: str

    def store_document(
        self,
        document_name: str,
        content: bytes,
        *,
        content_type: str,
        metadata: Mapping[str, str] | None = None,
    ) -> StorageResult:  # pragma: no cover - interface
        """Persist a document in the target storage system."""

        raise NotImplementedError


@dataclass(slots=True)
class StoredDocument:
    """Persisted document representation used by in-memory storage."""

    name: str
    content: bytes
    checksum: str
    content_type: str
    metadata: dict[str, str]


class InMemoryStorageConnector(StorageConnector):
    """Simple connector storing documents in memory for inspection."""

    def __init__(self, name: str = "memory"):
        self.name = name
        self._documents: list[StoredDocument] = []

    @property
    def documents(self) -> Sequence[StoredDocument]:
        return tuple(self._documents)

    def store_document(
        self,
        document_name: str,
        content: bytes,
        *,
        content_type: str,
        metadata: Mapping[str, str] | None = None,
    ) -> StorageResult:
        checksum = sha256(content).hexdigest()
        stored = StoredDocument(
            name=document_name,
            content=bytes(content),
            checksum=checksum,
            content_type=content_type,
            metadata=dict(metadata or {}),
        )
        self._documents.append(stored)
        return StorageResult(
            connector=self.name,
            document_name=document_name,
            checksum=checksum,
            size=len(content),
            content_type=content_type,
            metadata=dict(stored.metadata),
        )


class StorageGateway:
    """Coordinate document publication across storage connectors."""

    def __init__(
        self,
        connectors: Iterable[StorageConnector],
        *,
        default_content_type: str = "text/plain",
    ):
        self._connectors: list[StorageConnector] = list(connectors)
        self._default_content_type = default_content_type
        self._history: list[StorageResult] = []

    @property
    def connectors(self) -> Sequence[StorageConnector]:
        """Return the registered connectors."""

        return tuple(self._connectors)

    @property
    def history(self) -> Sequence[StorageResult]:
        """Return the history of published documents."""

        return tuple(self._history)

    def publish_planning_document(
        self,
        planning: PlanningResponse,
        artists: Sequence[Artist] | None = None,
        *,
        content: bytes | None = None,
        content_type: str | None = None,
    ) -> list[StorageResult]:
        """Render and publish the planning document across connectors."""

        payload = content or self._render_planning_document(planning, artists or [])
        resolved_type = content_type or self._default_content_type
        document_name = f"planning-{planning.event_date.isoformat()}-{planning.planning_id}.txt"
        metadata = {
            "planning_id": str(planning.planning_id),
            "event_date": planning.event_date.isoformat(),
            "assignment_count": str(len(planning.assignments)),
        }

        results: list[StorageResult] = []
        errors: MutableMapping[str, str] = {}

        for connector in self._connectors:
            try:
                result = connector.store_document(
                    document_name,
                    payload,
                    content_type=resolved_type,
                    metadata=metadata,
                )
            except Exception as exc:  # pragma: no cover - defensive logging
                errors[connector.name] = str(exc)
            else:
                self._history.append(result)
                results.append(result)

        if errors:
            raise StorageError(errors)

        return results

    @staticmethod
    def _render_planning_document(
        planning: PlanningResponse, artists: Sequence[Artist]
    ) -> bytes:
        """Render a text representation of the planning document."""

        lookup = {artist.id: artist.name for artist in artists}
        lines = [
            f"Planning {planning.planning_id}",
            f"Date: {planning.event_date.isoformat()}",
            "",
        ]
        if planning.assignments:
            lines.append("Affectations:")
            for assignment in planning.assignments:
                lines.append(_format_assignment(assignment, lookup))
        else:
            lines.append("Aucune affectation disponible.")
        return "\n".join(lines).encode("utf-8")


def _format_assignment(
    assignment: PlanningAssignment, artists: Mapping
) -> str:
    artist_name = artists.get(assignment.artist_id, str(assignment.artist_id))
    start = assignment.slot.start.strftime("%Y-%m-%d %H:%M")
    end = assignment.slot.end.strftime("%H:%M")
    return f"- {artist_name}: {start} -> {end}"


__all__ = [
    "InMemoryStorageConnector",
    "StorageConnector",
    "StorageError",
    "StorageGateway",
    "StorageResult",
]
