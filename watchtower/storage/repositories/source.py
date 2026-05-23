"""Source registry persistence."""

from __future__ import annotations

import json
import sqlite3
import uuid
from datetime import UTC, datetime
from typing import Any

from watchtower.domain.source import SourceRecord


class SourceRepository:
    def __init__(self, conn: sqlite3.Connection) -> None:
        self._conn = conn

    def create(
        self,
        tenant_id: str,
        connector_type: str,
        name: str,
        config: dict[str, Any] | None = None,
        *,
        source_id: str | None = None,
        enabled: bool = True,
    ) -> SourceRecord:
        sid = source_id or str(uuid.uuid4())
        now = datetime.now(UTC).isoformat()
        self._conn.execute(
            """
            INSERT INTO sources
                (id, tenant_id, connector_type, name, config_json, enabled, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                sid,
                tenant_id,
                connector_type,
                name,
                json.dumps(config or {}, ensure_ascii=False),
                int(enabled),
                now,
                now,
            ),
        )
        return SourceRecord(
            id=sid,
            tenant_id=tenant_id,
            connector_type=connector_type,
            name=name,
            config=config or {},
            enabled=enabled,
            created_at=datetime.fromisoformat(now),
            updated_at=datetime.fromisoformat(now),
        )

    def get(self, source_id: str, *, tenant_id: str | None = None) -> SourceRecord | None:
        if tenant_id is not None:
            row = self._conn.execute(
                """
                SELECT id, tenant_id, connector_type, name, config_json, enabled, created_at, updated_at
                FROM sources WHERE id = ? AND tenant_id = ?
                """,
                (source_id, tenant_id),
            ).fetchone()
        else:
            row = self._conn.execute(
                """
                SELECT id, tenant_id, connector_type, name, config_json, enabled, created_at, updated_at
                FROM sources WHERE id = ?
                """,
                (source_id,),
            ).fetchone()
        return self._row_to_record(row) if row else None

    def list_for_tenant(self, tenant_id: str, *, enabled_only: bool = False) -> list[SourceRecord]:
        query = """
            SELECT id, tenant_id, connector_type, name, config_json, enabled, created_at, updated_at
            FROM sources WHERE tenant_id = ?
        """
        params: list[Any] = [tenant_id]
        if enabled_only:
            query += " AND enabled = 1"
        query += " ORDER BY name"
        rows = self._conn.execute(query, params).fetchall()
        return [self._row_to_record(row) for row in rows]

    @staticmethod
    def _row_to_record(row: sqlite3.Row) -> SourceRecord:
        return SourceRecord(
            id=row["id"],
            tenant_id=row["tenant_id"],
            connector_type=row["connector_type"],
            name=row["name"],
            config=json.loads(row["config_json"] or "{}"),
            enabled=bool(row["enabled"]),
            created_at=datetime.fromisoformat(row["created_at"]),
            updated_at=datetime.fromisoformat(row["updated_at"]),
        )
