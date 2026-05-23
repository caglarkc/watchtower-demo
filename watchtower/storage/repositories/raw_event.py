"""Raw event store persistence."""

from __future__ import annotations

import json
import sqlite3
import uuid
from datetime import UTC, datetime
from typing import Any

from watchtower.domain.events import RawEventRecord


class RawEventRepository:
    def __init__(self, conn: sqlite3.Connection) -> None:
        self._conn = conn

    def insert_if_new(
        self,
        tenant_id: str,
        source_id: str,
        event: RawEventRecord,
    ) -> bool:
        """Insert event; return True if stored, False if duplicate."""
        event_id = str(uuid.uuid4())
        ingested_at = datetime.now(UTC).isoformat()
        event_ts = (
            event.event_timestamp.isoformat() if event.event_timestamp else None
        )
        try:
            self._conn.execute(
                """
                INSERT INTO raw_events
                    (id, tenant_id, source_id, dedupe_key, payload_json,
                     source_path, event_timestamp, ingested_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    event_id,
                    tenant_id,
                    source_id,
                    event.dedupe_key,
                    json.dumps(event.payload, ensure_ascii=False),
                    event.source_path,
                    event_ts,
                    ingested_at,
                ),
            )
            return True
        except sqlite3.IntegrityError:
            return False

    def list_unprocessed(
        self,
        tenant_id: str,
        *,
        limit: int = 500,
    ) -> list[dict[str, Any]]:
        """Raw events not yet normalized or queued as unknown."""
        rows = self._conn.execute(
            """
            SELECT r.id, r.source_id, r.payload_json, r.source_path,
                   r.event_timestamp, r.dedupe_key, s.connector_type
            FROM raw_events r
            JOIN sources s ON s.id = r.source_id
            LEFT JOIN normalized_events n ON n.raw_event_id = r.id
            LEFT JOIN unknown_schema_queue u ON u.raw_event_id = r.id
            WHERE r.tenant_id = ?
              AND n.id IS NULL
              AND u.id IS NULL
            ORDER BY r.ingested_at
            LIMIT ?
            """,
            (tenant_id, limit),
        ).fetchall()
        return [
            {
                "id": row["id"],
                "source_id": row["source_id"],
                "connector_type": row["connector_type"],
                "payload": json.loads(row["payload_json"]),
                "source_path": row["source_path"],
                "event_timestamp": row["event_timestamp"],
                "dedupe_key": row["dedupe_key"],
            }
            for row in rows
        ]

    def get_by_id(self, raw_event_id: str, tenant_id: str) -> dict[str, Any] | None:
        row = self._conn.execute(
            """
            SELECT r.id, r.source_id, r.payload_json, r.source_path,
                   r.event_timestamp, s.connector_type
            FROM raw_events r
            JOIN sources s ON s.id = r.source_id
            WHERE r.id = ? AND r.tenant_id = ?
            """,
            (raw_event_id, tenant_id),
        ).fetchone()
        if row is None:
            return None
        return {
            "id": row["id"],
            "source_id": row["source_id"],
            "connector_type": row["connector_type"],
            "payload": json.loads(row["payload_json"]),
            "source_path": row["source_path"],
            "event_timestamp": row["event_timestamp"],
        }

    def count_for_source(self, tenant_id: str, source_id: str) -> int:
        row = self._conn.execute(
            """
            SELECT COUNT(*) AS cnt FROM raw_events
            WHERE tenant_id = ? AND source_id = ?
            """,
            (tenant_id, source_id),
        ).fetchone()
        return int(row["cnt"]) if row else 0

    def list_for_source(
        self,
        tenant_id: str,
        source_id: str,
        *,
        limit: int = 100,
    ) -> list[dict[str, Any]]:
        rows = self._conn.execute(
            """
            SELECT dedupe_key, payload_json, source_path, event_timestamp, ingested_at
            FROM raw_events
            WHERE tenant_id = ? AND source_id = ?
            ORDER BY ingested_at DESC
            LIMIT ?
            """,
            (tenant_id, source_id, limit),
        ).fetchall()
        return [
            {
                "dedupe_key": row["dedupe_key"],
                "payload": json.loads(row["payload_json"]),
                "source_path": row["source_path"],
                "event_timestamp": row["event_timestamp"],
                "ingested_at": row["ingested_at"],
            }
            for row in rows
        ]
