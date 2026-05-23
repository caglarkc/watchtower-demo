"""Candidate event store persistence."""

from __future__ import annotations

import json
import sqlite3
import uuid
from datetime import UTC, datetime

from watchtower.domain.normalized_event import CandidateEvent


class CandidateEventRepository:
    def __init__(self, conn: sqlite3.Connection) -> None:
        self._conn = conn

    def insert(self, candidate: CandidateEvent) -> CandidateEvent:
        candidate_id = candidate.id or str(uuid.uuid4())
        created_at = datetime.now(UTC).isoformat()
        self._conn.execute(
            """
            INSERT INTO candidate_events (
                id, tenant_id, normalized_event_id, feature_hint,
                actor, action, resource, occurred_at, scenario_id,
                anomaly_flag, attributes_json, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                candidate_id,
                candidate.tenant_id,
                candidate.normalized_event_id,
                candidate.feature_hint,
                candidate.actor,
                candidate.action,
                candidate.resource,
                candidate.occurred_at.isoformat(),
                candidate.scenario_id,
                int(candidate.anomaly_flag),
                json.dumps(candidate.attributes, ensure_ascii=False),
                created_at,
            ),
        )
        return candidate.model_copy(update={"id": candidate_id})

    def exists_for_normalized(self, normalized_event_id: str) -> bool:
        row = self._conn.execute(
            "SELECT 1 FROM candidate_events WHERE normalized_event_id = ?",
            (normalized_event_id,),
        ).fetchone()
        return row is not None

    def count_for_tenant(self, tenant_id: str) -> int:
        row = self._conn.execute(
            "SELECT COUNT(*) AS cnt FROM candidate_events WHERE tenant_id = ?",
            (tenant_id,),
        ).fetchone()
        return int(row["cnt"]) if row else 0
