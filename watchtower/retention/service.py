"""Apply configurable retention windows per table."""

from __future__ import annotations

import json
import sqlite3
import uuid
from dataclasses import dataclass, field
from datetime import UTC, datetime, timedelta

from watchtower.config.settings import WatchtowerSettings


@dataclass
class RetentionResult:
    tenant_id: str | None
    deleted: dict[str, int] = field(default_factory=dict)
    ran_at: str = ""


class RetentionService:
    def __init__(self, conn: sqlite3.Connection, settings: WatchtowerSettings) -> None:
        self._conn = conn
        self._settings = settings

    def apply(self, *, tenant_id: str | None = None, dry_run: bool = False) -> RetentionResult:
        now = datetime.now(UTC)
        deleted: dict[str, int] = {}

        policies = [
            ("raw_events", self._settings.retention_raw_events_days, "ingested_at"),
            ("normalized_events", self._settings.retention_normalized_events_days, "created_at"),
            ("audit_log", self._settings.retention_audit_days, "created_at"),
            ("llm_call_audit", self._settings.retention_llm_audit_days, "created_at"),
        ]

        for table, days, column in policies:
            if days <= 0:
                continue
            cutoff = (now - timedelta(days=days)).isoformat()
            query = f"SELECT COUNT(*) FROM {table} WHERE {column} < ?"
            params: list[str] = [cutoff]
            if tenant_id is not None and self._table_has_tenant(table):
                query += " AND tenant_id = ?"
                params.append(tenant_id)
            count = int(self._conn.execute(query, params).fetchone()[0])
            if count and not dry_run:
                delete_sql = f"DELETE FROM {table} WHERE {column} < ?"
                if tenant_id is not None and self._table_has_tenant(table):
                    delete_sql += " AND tenant_id = ?"
                self._conn.execute(delete_sql, params)
            deleted[table] = count

        result = RetentionResult(
            tenant_id=tenant_id,
            deleted=deleted,
            ran_at=now.isoformat(),
        )
        if not dry_run:
            self._record_run(result)
        return result

    def _record_run(self, result: RetentionResult) -> None:
        self._conn.execute(
            """
            INSERT INTO retention_runs (id, tenant_id, policy, deleted_counts_json, ran_at)
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                str(uuid.uuid4()),
                result.tenant_id,
                "default",
                json.dumps(result.deleted, ensure_ascii=False),
                result.ran_at,
            ),
        )

    @staticmethod
    def _table_has_tenant(table: str) -> bool:
        return table in {
            "raw_events",
            "normalized_events",
            "audit_log",
            "llm_call_audit",
        }
