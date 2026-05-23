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
