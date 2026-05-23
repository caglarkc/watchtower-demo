"""LLM call audit persistence."""

from __future__ import annotations

import sqlite3
from datetime import datetime


class LLMCallAuditRepository:
    def __init__(self, conn: sqlite3.Connection) -> None:
        self._conn = conn

    def insert(
        self,
        *,
        audit_id: str,
        tenant_id: str | None,
        task_name: str,
        provider: str | None,
        model: str | None,
        success: bool,
        attempts: int,
        prompt_hash: str,
        request_json: str,
        response_json: str | None,
        error: str | None,
        created_at: datetime,
    ) -> str:
        self._conn.execute(
            """
            INSERT INTO llm_call_audit (
                id, tenant_id, task_name, provider, model, success, attempts,
                prompt_hash, request_json, response_json, error, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                audit_id,
                tenant_id,
                task_name,
                provider,
                model,
                1 if success else 0,
                attempts,
                prompt_hash,
                request_json,
                response_json,
                error,
                created_at.isoformat(),
            ),
        )
        return audit_id

    def count_by_task(self, tenant_id: str | None, task_name: str) -> int:
        if tenant_id:
            row = self._conn.execute(
                "SELECT COUNT(*) FROM llm_call_audit WHERE tenant_id = ? AND task_name = ?",
                (tenant_id, task_name),
            ).fetchone()
        else:
            row = self._conn.execute(
                "SELECT COUNT(*) FROM llm_call_audit WHERE task_name = ?",
                (task_name,),
            ).fetchone()
        return int(row[0]) if row else 0
