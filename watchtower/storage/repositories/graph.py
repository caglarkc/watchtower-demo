"""Graph runs, audit, silent findings, alerts, learning events."""

from __future__ import annotations

import json
import sqlite3
import uuid
from datetime import UTC, datetime
from typing import Any


class GraphRepository:
    def __init__(self, conn: sqlite3.Connection) -> None:
        self._conn = conn

    @staticmethod
    def new_id() -> str:
        return str(uuid.uuid4())

    def create_run(
        self,
        *,
        run_id: str,
        tenant_id: str,
        candidate_id: str | None,
        mode: str,
        thread_id: str | None = None,
    ) -> None:
        now = datetime.now(UTC).isoformat()
        self._conn.execute(
            """
            INSERT INTO graph_runs (
                id, tenant_id, candidate_id, mode, status, started_at,
                thread_id, interrupted
            ) VALUES (?, ?, ?, ?, 'running', ?, ?, 0)
            """,
            (run_id, tenant_id, candidate_id, mode, now, thread_id),
        )

    def set_checkpoint_meta(
        self,
        run_id: str,
        *,
        thread_id: str,
        checkpoint_id: str | None,
        interrupted: bool,
    ) -> None:
        self._conn.execute(
            """
            UPDATE graph_runs SET
                thread_id = ?,
                last_checkpoint_id = ?,
                interrupted = ?
            WHERE id = ?
            """,
            (thread_id, checkpoint_id, int(interrupted), run_id),
        )

    def get_run_by_thread(self, thread_id: str) -> dict[str, Any] | None:
        row = self._conn.execute(
            "SELECT * FROM graph_runs WHERE thread_id = ? ORDER BY started_at DESC LIMIT 1",
            (thread_id,),
        ).fetchone()
        if not row:
            return None
        return dict(row)

    def list_interrupted_runs(
        self,
        tenant_id: str,
        *,
        limit: int = 50,
    ) -> list[dict[str, Any]]:
        rows = self._conn.execute(
            """
            SELECT id, tenant_id, candidate_id, mode, status, thread_id,
                   last_checkpoint_id, started_at
            FROM graph_runs
            WHERE tenant_id = ?
              AND interrupted = 1
              AND status = 'running'
            ORDER BY started_at DESC
            LIMIT ?
            """,
            (tenant_id, limit),
        ).fetchall()
        return [dict(r) for r in rows]

    def finish_run(
        self,
        run_id: str,
        *,
        status: str,
        route: dict[str, Any] | None = None,
        assessment: dict[str, Any] | None = None,
        error: str | None = None,
    ) -> None:
        now = datetime.now(UTC).isoformat()
        self._conn.execute(
            """
            UPDATE graph_runs SET
                status = ?, route_json = ?, assessment_json = ?,
                finished_at = ?, error = ?
            WHERE id = ?
            """,
            (
                status,
                json.dumps(route or {}, ensure_ascii=False),
                json.dumps(assessment or {}, ensure_ascii=False),
                now,
                error,
                run_id,
            ),
        )

    def append_audit(self, run_id: str, node_name: str, output: dict[str, Any]) -> str:
        audit_id = self.new_id()
        self._conn.execute(
            """
            INSERT INTO graph_run_audit (id, run_id, node_name, output_json, created_at)
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                audit_id,
                run_id,
                node_name,
                json.dumps(output, ensure_ascii=False, default=str),
                datetime.now(UTC).isoformat(),
            ),
        )
        return audit_id

    def insert_silent_finding(
        self,
        *,
        tenant_id: str,
        run_id: str,
        candidate_id: str | None,
        feature_id: str,
        severity: str,
        payload: dict[str, Any],
    ) -> str:
        fid = self.new_id()
        self._conn.execute(
            """
            INSERT INTO silent_candidate_findings (
                id, tenant_id, run_id, candidate_id, feature_id, severity, payload_json, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                fid,
                tenant_id,
                run_id,
                candidate_id,
                feature_id,
                severity,
                json.dumps(payload, ensure_ascii=False, default=str),
                datetime.now(UTC).isoformat(),
            ),
        )
        return fid

    def insert_alert_case(
        self,
        *,
        tenant_id: str,
        run_id: str,
        candidate_id: str | None,
        feature_id: str,
        severity: str,
        payload: dict[str, Any],
    ) -> str:
        aid = self.new_id()
        self._conn.execute(
            """
            INSERT INTO alert_cases (
                id, tenant_id, run_id, candidate_id, feature_id, severity, status, payload_json, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, 'open', ?, ?)
            """,
            (
                aid,
                tenant_id,
                run_id,
                candidate_id,
                feature_id,
                severity,
                json.dumps(payload, ensure_ascii=False, default=str),
                datetime.now(UTC).isoformat(),
            ),
        )
        return aid

    def insert_learning_event(
        self,
        *,
        tenant_id: str,
        run_id: str,
        candidate_id: str | None,
        event_type: str,
        payload: dict[str, Any],
    ) -> str:
        lid = self.new_id()
        self._conn.execute(
            """
            INSERT INTO controlled_learning_events (
                id, tenant_id, run_id, candidate_id, event_type, payload_json, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                lid,
                tenant_id,
                run_id,
                candidate_id,
                event_type,
                json.dumps(payload, ensure_ascii=False, default=str),
                datetime.now(UTC).isoformat(),
            ),
        )
        return lid

    def count_silent_findings(self, tenant_id: str, run_id: str) -> int:
        row = self._conn.execute(
            "SELECT COUNT(*) FROM silent_candidate_findings WHERE tenant_id = ? AND run_id = ?",
            (tenant_id, run_id),
        ).fetchone()
        return int(row[0]) if row else 0

    def count_alerts(self, tenant_id: str, run_id: str) -> int:
        row = self._conn.execute(
            "SELECT COUNT(*) FROM alert_cases WHERE tenant_id = ? AND run_id = ?",
            (tenant_id, run_id),
        ).fetchone()
        return int(row[0]) if row else 0

    def count_learning_events(self, tenant_id: str, run_id: str) -> int:
        row = self._conn.execute(
            "SELECT COUNT(*) FROM controlled_learning_events WHERE tenant_id = ? AND run_id = ?",
            (tenant_id, run_id),
        ).fetchone()
        return int(row[0]) if row else 0

    def list_audit(self, run_id: str) -> list[dict[str, Any]]:
        rows = self._conn.execute(
            "SELECT node_name, output_json, created_at FROM graph_run_audit WHERE run_id = ? ORDER BY created_at",
            (run_id,),
        ).fetchall()
        return [
            {
                "node_name": r[0],
                "output": json.loads(r[1] or "{}"),
                "created_at": r[2],
            }
            for r in rows
        ]

    def get_run(self, run_id: str) -> dict[str, Any] | None:
        row = self._conn.execute(
            "SELECT * FROM graph_runs WHERE id = ?", (run_id,)
        ).fetchone()
        if not row:
            return None
        return dict(row)
