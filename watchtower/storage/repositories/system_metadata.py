"""Key-value system metadata (provider chain, install markers)."""

from __future__ import annotations

import sqlite3
from datetime import UTC, datetime


class SystemMetadataRepository:
    def __init__(self, conn: sqlite3.Connection) -> None:
        self._conn = conn

    def get(self, key: str) -> str | None:
        row = self._conn.execute(
            "SELECT value FROM system_metadata WHERE key = ?",
            (key,),
        ).fetchone()
        return row[0] if row else None

    def set(self, key: str, value: str) -> None:
        now = datetime.now(UTC).isoformat()
        self._conn.execute(
            """
            INSERT INTO system_metadata (key, value, updated_at)
            VALUES (?, ?, ?)
            ON CONFLICT(key) DO UPDATE SET value = excluded.value, updated_at = excluded.updated_at
            """,
            (key, value, now),
        )

    def delete(self, key: str) -> None:
        self._conn.execute("DELETE FROM system_metadata WHERE key = ?", (key,))
