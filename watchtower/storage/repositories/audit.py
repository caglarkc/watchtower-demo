"""Audit log persistence."""

from __future__ import annotations

import json
import sqlite3
import uuid
from datetime import UTC, datetime
from typing import Any

from watchtower.domain.audit import AuditEntry


class AuditRepository:
    def __init__(self, conn: sqlite3.Connection) -> None:
        self._conn = conn

    def append(
        self,
        tenant_id: str,
        action: str,
        *,
        actor: str | None = None,
        details: dict[str, Any] | None = None,
    ) -> AuditEntry:
        entry_id = str(uuid.uuid4())
        created_at = datetime.now(UTC).isoformat()
        payload = json.dumps(details or {}, ensure_ascii=False)
        self._conn.execute(
            """
            INSERT INTO audit_log (id, tenant_id, actor, action, details_json, created_at)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (entry_id, tenant_id, actor, action, payload, created_at),
        )
        return AuditEntry(
            id=entry_id,
            tenant_id=tenant_id,
            actor=actor,
            action=action,
            details=details or {},
            created_at=datetime.fromisoformat(created_at),
        )

    def list_for_tenant(self, tenant_id: str, *, limit: int = 100) -> list[AuditEntry]:
        rows = self._conn.execute(
            """
            SELECT id, tenant_id, actor, action, details_json, created_at
            FROM audit_log
            WHERE tenant_id = ?
            ORDER BY created_at DESC
            LIMIT ?
            """,
            (tenant_id, limit),
        ).fetchall()
        entries: list[AuditEntry] = []
        for row in rows:
            entries.append(
                AuditEntry(
                    id=row["id"],
                    tenant_id=row["tenant_id"],
                    actor=row["actor"],
                    action=row["action"],
                    details=json.loads(row["details_json"] or "{}"),
                    created_at=datetime.fromisoformat(row["created_at"]),
                )
            )
        return entries
