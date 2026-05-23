"""Source cursor persistence."""

from __future__ import annotations

import json
import sqlite3
from datetime import UTC, datetime

from watchtower.domain.events import ConnectorCursor


class SourceCursorRepository:
    def __init__(self, conn: sqlite3.Connection) -> None:
        self._conn = conn

    def get(
        self,
        source_id: str,
        tenant_id: str,
        *,
        cursor_key: str = "default",
    ) -> ConnectorCursor:
        row = self._conn.execute(
            """
            SELECT cursor_value FROM source_cursors
            WHERE source_id = ? AND tenant_id = ? AND cursor_key = ?
            """,
            (source_id, tenant_id, cursor_key),
        ).fetchone()
        if row is None:
            return ConnectorCursor()
        data = json.loads(row["cursor_value"] or "{}")
        return ConnectorCursor(data=data if isinstance(data, dict) else {})

    def save(
        self,
        source_id: str,
        tenant_id: str,
        cursor: ConnectorCursor,
        *,
        cursor_key: str = "default",
        ack: bool = True,
    ) -> None:
        now = datetime.now(UTC).isoformat()
        last_ack = now if ack else None
        existing = self._conn.execute(
            """
            SELECT 1 FROM source_cursors
            WHERE source_id = ? AND tenant_id = ? AND cursor_key = ?
            """,
            (source_id, tenant_id, cursor_key),
        ).fetchone()
        payload = json.dumps(cursor.data, ensure_ascii=False)
        if existing:
            self._conn.execute(
                """
                UPDATE source_cursors
                SET cursor_value = ?, last_ack_at = COALESCE(?, last_ack_at), updated_at = ?
                WHERE source_id = ? AND tenant_id = ? AND cursor_key = ?
                """,
                (payload, last_ack, now, source_id, tenant_id, cursor_key),
            )
        else:
            self._conn.execute(
                """
                INSERT INTO source_cursors
                    (source_id, tenant_id, cursor_key, cursor_value, last_ack_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (source_id, tenant_id, cursor_key, payload, last_ack, now),
            )
