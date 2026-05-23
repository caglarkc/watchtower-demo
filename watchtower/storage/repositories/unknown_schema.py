"""Unknown schema queue persistence."""

from __future__ import annotations

import json
import sqlite3
import uuid
from datetime import UTC, datetime

from watchtower.domain.normalized_event import UnknownSchemaEntry


class UnknownSchemaRepository:
    def __init__(self, conn: sqlite3.Connection) -> None:
        self._conn = conn

    def enqueue(self, entry: UnknownSchemaEntry) -> UnknownSchemaEntry:
        entry_id = entry.id or str(uuid.uuid4())
        created_at = (entry.created_at or datetime.now(UTC)).isoformat()
        try:
            self._conn.execute(
                """
                INSERT INTO unknown_schema_queue (
                    id, tenant_id, raw_event_id, schema_signature,
                    payload_sample_json, reason, status, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    entry_id,
                    entry.tenant_id,
                    entry.raw_event_id,
                    entry.schema_signature,
                    json.dumps(entry.payload_sample, ensure_ascii=False),
                    entry.reason,
                    entry.status,
                    created_at,
                ),
            )
        except sqlite3.IntegrityError:
            return entry
        return entry.model_copy(update={"id": entry_id, "created_at": datetime.fromisoformat(created_at)})

    def count_pending(self, tenant_id: str) -> int:
        row = self._conn.execute(
            """
            SELECT COUNT(*) AS cnt FROM unknown_schema_queue
            WHERE tenant_id = ? AND status = 'pending'
            """,
            (tenant_id,),
        ).fetchone()
        return int(row["cnt"]) if row else 0
