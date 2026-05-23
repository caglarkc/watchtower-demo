"""Normalized event persistence."""

from __future__ import annotations

import json
import sqlite3
import uuid
from datetime import UTC, datetime

from watchtower.domain.normalized_event import NormalizedEvent


class NormalizedEventRepository:
    def __init__(self, conn: sqlite3.Connection) -> None:
        self._conn = conn

    def insert(self, event: NormalizedEvent) -> NormalizedEvent:
        event_id = event.id or str(uuid.uuid4())
        created_at = datetime.now(UTC).isoformat()
        self._conn.execute(
            """
            INSERT INTO normalized_events (
                id, tenant_id, raw_event_id, source_id, schema_format,
                event_type, actor, action, resource, occurred_at,
                feature_hint, scenario_id, source_path, channel,
                anomaly_flag, attributes_json, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                event_id,
                event.tenant_id,
                event.raw_event_id,
                event.source_id,
                event.schema_format,
                event.event_type,
                event.actor,
                event.action,
                event.resource,
                event.occurred_at.isoformat(),
                event.feature_hint,
                event.scenario_id,
                event.source_path,
                event.channel,
                int(event.anomaly_flag),
                json.dumps(event.attributes, ensure_ascii=False),
                created_at,
            ),
        )
        return event.model_copy(update={"id": event_id})

    def exists_for_raw(self, raw_event_id: str) -> bool:
        row = self._conn.execute(
            "SELECT 1 FROM normalized_events WHERE raw_event_id = ?",
            (raw_event_id,),
        ).fetchone()
        return row is not None

    def get(self, event_id: str, tenant_id: str) -> NormalizedEvent | None:
        row = self._conn.execute(
            """
            SELECT id, tenant_id, raw_event_id, source_id, schema_format,
                   event_type, actor, action, resource, occurred_at,
                   feature_hint, scenario_id, source_path, channel,
                   anomaly_flag, attributes_json
            FROM normalized_events WHERE id = ? AND tenant_id = ?
            """,
            (event_id, tenant_id),
        ).fetchone()
        return self._row_to_model(row) if row else None

    @staticmethod
    def _row_to_model(row: sqlite3.Row) -> NormalizedEvent:
        return NormalizedEvent(
            id=row["id"],
            tenant_id=row["tenant_id"],
            raw_event_id=row["raw_event_id"],
            source_id=row["source_id"],
            schema_format=row["schema_format"],
            event_type=row["event_type"],
            actor=row["actor"],
            action=row["action"],
            resource=row["resource"],
            occurred_at=datetime.fromisoformat(row["occurred_at"]),
            feature_hint=row["feature_hint"],
            scenario_id=row["scenario_id"],
            source_path=row["source_path"],
            channel=row["channel"],
            anomaly_flag=bool(row["anomaly_flag"]),
            attributes=json.loads(row["attributes_json"] or "{}"),
        )
