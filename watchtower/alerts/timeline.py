"""Case timeline persistence helpers."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

from watchtower.domain.alerts import CaseTimelineEntry, CaseTimelineEventType
from watchtower.storage.repositories.alerts import AlertRepository


class CaseTimelineRecorder:
    def __init__(self, repo: AlertRepository) -> None:
        self._repo = repo

    def record(
        self,
        tenant_id: str,
        alert_id: str,
        case_id: str | None,
        event_type: CaseTimelineEventType,
        *,
        actor: str = "system",
        comment: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> CaseTimelineEntry:
        entry = CaseTimelineEntry(
            id=self._repo.new_id(),
            tenant_id=tenant_id,
            alert_id=alert_id,
            case_id=case_id,
            event_type=event_type,
            actor=actor,
            comment=comment,
            metadata=metadata or {},
            created_at=datetime.now(UTC),
        )
        self._repo.insert_timeline_entry(entry)
        return entry
