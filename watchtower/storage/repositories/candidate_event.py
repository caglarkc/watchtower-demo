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

    def get_by_id(self, candidate_id: str, tenant_id: str) -> CandidateEvent | None:
        row = self._conn.execute(
            """
            SELECT id, tenant_id, normalized_event_id, feature_hint,
                   actor, action, resource, occurred_at, scenario_id,
                   anomaly_flag, attributes_json
            FROM candidate_events
            WHERE id = ? AND tenant_id = ?
            """,
            (candidate_id, tenant_id),
        ).fetchone()
        if row is None:
            return None
        return self._row_to_candidate(row)

    def list_pending_graph(
        self,
        tenant_id: str,
        *,
        limit: int = 100,
    ) -> list[dict[str, str]]:
        rows = self._conn.execute(
            """
            SELECT c.id
            FROM candidate_events c
            WHERE c.tenant_id = ?
              AND NOT EXISTS (
                SELECT 1 FROM graph_runs g WHERE g.candidate_id = c.id
              )
            ORDER BY c.created_at ASC
            LIMIT ?
            """,
            (tenant_id, limit),
        ).fetchall()
        return [{"id": row["id"]} for row in rows]

    @staticmethod
    def _row_to_candidate(row: sqlite3.Row) -> CandidateEvent:
        from datetime import datetime

        occurred = row["occurred_at"]
        if isinstance(occurred, str):
            occurred_at = datetime.fromisoformat(occurred)
        else:
            occurred_at = occurred
        return CandidateEvent(
            id=row["id"],
            tenant_id=row["tenant_id"],
            normalized_event_id=row["normalized_event_id"],
            feature_hint=row["feature_hint"],
            actor=row["actor"],
            action=row["action"],
            resource=row["resource"],
            occurred_at=occurred_at,
            scenario_id=row["scenario_id"],
            anomaly_flag=bool(row["anomaly_flag"]),
            attributes=json.loads(row["attributes_json"]),
        )
