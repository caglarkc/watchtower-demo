"""Alert, case, suppression, and silent finding persistence."""

from __future__ import annotations

import json
import sqlite3
import uuid
from datetime import UTC, datetime
from typing import Any

from watchtower.domain.alerts import (
    Alert,
    AlertCase,
    AlertLifecycleEvent,
    CaseTimelineEntry,
    SuppressionWindow,
)


class AlertRepository:
    def __init__(self, conn: sqlite3.Connection) -> None:
        self._conn = conn

    @staticmethod
    def new_id() -> str:
        return str(uuid.uuid4())

    def ensure_graph_run(self, tenant_id: str, run_id: str, *, mode: str = "run") -> str:
        """Ensure a graph_runs row exists for alert_cases FK."""
        now = datetime.now(UTC).isoformat()
        self._conn.execute(
            """
            INSERT OR IGNORE INTO graph_runs (
                id, tenant_id, mode, status, started_at, finished_at
            ) VALUES (?, ?, ?, 'completed', ?, ?)
            """,
            (run_id, tenant_id, mode, now, now),
        )
        return run_id

    def insert_alert(self, alert: Alert) -> str:
        self._conn.execute(
            """
            INSERT INTO alerts (
                id, tenant_id, feature_id, severity, status, title, summary,
                user_id, department_id, resource, action, graph_run_id,
                payload_json, created_at, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                alert.id,
                alert.tenant_id,
                alert.feature_id,
                alert.severity,
                alert.status,
                alert.title,
                alert.summary,
                alert.user_id,
                alert.department_id,
                alert.resource,
                alert.action,
                alert.graph_run_id,
                json.dumps(alert.payload, ensure_ascii=False, default=str),
                alert.created_at.isoformat(),
                alert.updated_at.isoformat(),
            ),
        )
        return alert.id

    def get_alert(self, tenant_id: str, alert_id: str) -> Alert | None:
        row = self._conn.execute(
            "SELECT * FROM alerts WHERE tenant_id = ? AND id = ?",
            (tenant_id, alert_id),
        ).fetchone()
        return self._alert_from_row(row) if row else None

    def update_alert_status(
        self,
        tenant_id: str,
        alert_id: str,
        status: str,
        *,
        updated_at: datetime | None = None,
    ) -> None:
        now = (updated_at or datetime.now(UTC)).isoformat()
        self._conn.execute(
            "UPDATE alerts SET status = ?, updated_at = ? WHERE tenant_id = ? AND id = ?",
            (status, now, tenant_id, alert_id),
        )

    def list_cases(
        self,
        tenant_id: str,
        *,
        status: str | None = None,
        assigned_to: str | None = None,
        limit: int = 100,
    ) -> list[AlertCase]:
        clauses = ["tenant_id = ?"]
        params: list[Any] = [tenant_id]
        if status:
            clauses.append("status = ?")
            params.append(status)
        if assigned_to:
            clauses.append("assigned_to = ?")
            params.append(assigned_to)
        sql = (
            f"SELECT * FROM alert_cases WHERE {' AND '.join(clauses)} "
            f"ORDER BY created_at DESC LIMIT ?"
        )
        params.append(limit)
        rows = self._conn.execute(sql, params).fetchall()
        return [self._case_from_row(r) for r in rows]

    def get_graph_run_assessment(self, run_id: str) -> dict[str, Any] | None:
        row = self._conn.execute(
            "SELECT assessment_json, route_json FROM graph_runs WHERE id = ?",
            (run_id,),
        ).fetchone()
        if row is None:
            return None
        assessment = json.loads(row["assessment_json"] or "{}")
        if not assessment:
            return None
        return assessment

    def get_graph_run_audit_summary(self, run_id: str) -> list[dict[str, Any]]:
        rows = self._conn.execute(
            """
            SELECT node_name, output_json, created_at
            FROM graph_run_audit WHERE run_id = ? ORDER BY created_at
            """,
            (run_id,),
        ).fetchall()
        return [
            {
                "node_name": r["node_name"],
                "output": json.loads(r["output_json"] or "{}"),
                "created_at": r["created_at"],
            }
            for r in rows
        ]

    def insert_timeline_entry(self, entry: CaseTimelineEntry) -> str:
        self._conn.execute(
            """
            INSERT INTO case_timeline (
                id, tenant_id, alert_id, case_id, event_type,
                actor, comment, metadata_json, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                entry.id,
                entry.tenant_id,
                entry.alert_id,
                entry.case_id,
                entry.event_type,
                entry.actor,
                entry.comment,
                json.dumps(entry.metadata, ensure_ascii=False, default=str),
                entry.created_at.isoformat(),
            ),
        )
        return entry.id

    def list_timeline(
        self,
        tenant_id: str,
        *,
        alert_id: str | None = None,
        case_id: str | None = None,
        limit: int = 200,
    ) -> list[CaseTimelineEntry]:
        clauses = ["tenant_id = ?"]
        params: list[Any] = [tenant_id]
        if alert_id:
            clauses.append("alert_id = ?")
            params.append(alert_id)
        if case_id:
            clauses.append("case_id = ?")
            params.append(case_id)
        sql = (
            f"SELECT * FROM case_timeline WHERE {' AND '.join(clauses)} "
            f"ORDER BY created_at ASC LIMIT ?"
        )
        params.append(limit)
        rows = self._conn.execute(sql, params).fetchall()
        return [self._timeline_from_row(r) for r in rows]

    def list_alerts(
        self,
        tenant_id: str,
        *,
        status: str | None = None,
        severity: str | None = None,
        department_id: str | None = None,
        since: datetime | None = None,
        limit: int = 100,
    ) -> list[Alert]:
        clauses = ["tenant_id = ?"]
        params: list[Any] = [tenant_id]
        if status:
            clauses.append("status = ?")
            params.append(status)
        if severity:
            clauses.append("severity = ?")
            params.append(severity)
        if department_id:
            clauses.append("department_id = ?")
            params.append(department_id)
        if since:
            clauses.append("created_at >= ?")
            params.append(since.isoformat())
        sql = (
            f"SELECT * FROM alerts WHERE {' AND '.join(clauses)} "
            f"ORDER BY created_at DESC LIMIT ?"
        )
        params.append(limit)
        rows = self._conn.execute(sql, params).fetchall()
        return [self._alert_from_row(r) for r in rows]

    def insert_case(self, case: AlertCase) -> str:
        self._conn.execute(
            """
            INSERT INTO alert_cases (
                id, tenant_id, run_id, candidate_id, feature_id, severity,
                status, payload_json, created_at, alert_id, updated_at,
                ticket_id, assigned_to
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                case.id,
                case.tenant_id,
                case.run_id or "",
                case.candidate_id,
                case.payload.get("feature_id", ""),
                case.payload.get("severity", "ALERT"),
                case.status,
                json.dumps(case.payload, ensure_ascii=False, default=str),
                case.created_at.isoformat(),
                case.alert_id,
                case.updated_at.isoformat(),
                case.ticket_id,
                case.assigned_to,
            ),
        )
        return case.id

    def get_case(self, tenant_id: str, case_id: str) -> AlertCase | None:
        row = self._conn.execute(
            "SELECT * FROM alert_cases WHERE tenant_id = ? AND id = ?",
            (tenant_id, case_id),
        ).fetchone()
        return self._case_from_row(row) if row else None

    def get_case_by_alert(self, tenant_id: str, alert_id: str) -> AlertCase | None:
        row = self._conn.execute(
            "SELECT * FROM alert_cases WHERE tenant_id = ? AND alert_id = ?",
            (tenant_id, alert_id),
        ).fetchone()
        return self._case_from_row(row) if row else None

    def update_case(
        self,
        tenant_id: str,
        case_id: str,
        *,
        status: str,
        ticket_id: str | None = None,
        assigned_to: str | None = None,
    ) -> None:
        now = datetime.now(UTC).isoformat()
        self._conn.execute(
            """
            UPDATE alert_cases SET status = ?, updated_at = ?,
                ticket_id = COALESCE(?, ticket_id),
                assigned_to = COALESCE(?, assigned_to)
            WHERE tenant_id = ? AND id = ?
            """,
            (status, now, ticket_id, assigned_to, tenant_id, case_id),
        )

    def insert_lifecycle_event(self, event: AlertLifecycleEvent) -> str:
        self._conn.execute(
            """
            INSERT INTO alert_lifecycle_events (
                id, tenant_id, alert_id, alert_case_id, from_status, to_status,
                actor, comment, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                event.id,
                event.tenant_id,
                event.alert_id,
                event.alert_case_id,
                event.from_status,
                event.to_status,
                event.actor,
                event.comment,
                event.created_at.isoformat(),
            ),
        )
        return event.id

    def insert_suppression(self, window: SuppressionWindow) -> str:
        self._conn.execute(
            """
            INSERT INTO suppression_windows (
                id, tenant_id, alert_id, scope_json, starts_at, expires_at,
                reason, created_by, active
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                window.id,
                window.tenant_id,
                window.alert_id,
                json.dumps(window.scope, ensure_ascii=False),
                window.starts_at.isoformat(),
                window.expires_at.isoformat(),
                window.reason,
                window.created_by,
                1 if window.active else 0,
            ),
        )
        return window.id

    def deactivate_expired_suppressions(self, tenant_id: str, *, as_of: datetime) -> int:
        cur = self._conn.execute(
            """
            UPDATE suppression_windows SET active = 0
            WHERE tenant_id = ? AND active = 1 AND expires_at <= ?
            """,
            (tenant_id, as_of.isoformat()),
        )
        return cur.rowcount

    def is_alert_suppressed(self, tenant_id: str, alert_id: str, *, as_of: datetime) -> bool:
        self.deactivate_expired_suppressions(tenant_id, as_of=as_of)
        row = self._conn.execute(
            """
            SELECT COUNT(*) FROM suppression_windows
            WHERE tenant_id = ? AND alert_id = ? AND active = 1 AND expires_at > ?
            """,
            (tenant_id, alert_id, as_of.isoformat()),
        ).fetchone()
        return bool(row and row[0] > 0)

    def list_active_suppressions(
        self, tenant_id: str, *, as_of: datetime
    ) -> list[SuppressionWindow]:
        self.deactivate_expired_suppressions(tenant_id, as_of=as_of)
        rows = self._conn.execute(
            """
            SELECT * FROM suppression_windows
            WHERE tenant_id = ? AND active = 1 AND expires_at > ?
            ORDER BY expires_at
            """,
            (tenant_id, as_of.isoformat()),
        ).fetchall()
        return [self._suppression_from_row(r) for r in rows]

    def list_silent_findings(
        self,
        tenant_id: str,
        *,
        since: datetime | None = None,
        limit: int = 100,
    ) -> list[dict[str, Any]]:
        if since:
            rows = self._conn.execute(
                """
                SELECT * FROM silent_candidate_findings
                WHERE tenant_id = ? AND created_at >= ?
                ORDER BY created_at DESC LIMIT ?
                """,
                (tenant_id, since.isoformat(), limit),
            ).fetchall()
        else:
            rows = self._conn.execute(
                """
                SELECT * FROM silent_candidate_findings
                WHERE tenant_id = ? ORDER BY created_at DESC LIMIT ?
                """,
                (tenant_id, limit),
            ).fetchall()
        return [dict(r) for r in rows]

    def insert_operator_query(
        self,
        *,
        query_id: str,
        tenant_id: str,
        query_text: str,
        answer_text: str,
        sources: list[dict[str, Any]],
    ) -> str:
        self._conn.execute(
            """
            INSERT INTO operator_queries (id, tenant_id, query_text, answer_text, sources_json, created_at)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                query_id,
                tenant_id,
                query_text,
                answer_text,
                json.dumps(sources, ensure_ascii=False),
                datetime.now(UTC).isoformat(),
            ),
        )
        return query_id

    def _alert_from_row(self, row: sqlite3.Row) -> Alert:
        return Alert(
            id=row["id"],
            tenant_id=row["tenant_id"],
            feature_id=row["feature_id"],
            severity=row["severity"],
            status=row["status"],
            title=row["title"],
            summary=row["summary"],
            user_id=row["user_id"],
            department_id=row["department_id"],
            resource=row["resource"],
            action=row["action"],
            graph_run_id=row["graph_run_id"],
            payload=json.loads(row["payload_json"] or "{}"),
            created_at=datetime.fromisoformat(row["created_at"]),
            updated_at=datetime.fromisoformat(row["updated_at"]),
        )

    def _case_from_row(self, row: sqlite3.Row) -> AlertCase:
        keys = row.keys()
        updated = row["updated_at"] if "updated_at" in keys and row["updated_at"] else row["created_at"]
        return AlertCase(
            id=row["id"],
            tenant_id=row["tenant_id"],
            alert_id=row["alert_id"] if "alert_id" in keys else "",
            status=row["status"],
            run_id=row["run_id"] or None,
            candidate_id=row["candidate_id"],
            ticket_id=row["ticket_id"] if "ticket_id" in keys else None,
            assigned_to=row["assigned_to"] if "assigned_to" in keys else None,
            payload=json.loads(row["payload_json"] or "{}"),
            created_at=datetime.fromisoformat(row["created_at"]),
            updated_at=datetime.fromisoformat(updated),
        )

    def _timeline_from_row(self, row: sqlite3.Row) -> CaseTimelineEntry:
        return CaseTimelineEntry(
            id=row["id"],
            tenant_id=row["tenant_id"],
            alert_id=row["alert_id"],
            case_id=row["case_id"],
            event_type=row["event_type"],
            actor=row["actor"],
            comment=row["comment"],
            metadata=json.loads(row["metadata_json"] or "{}"),
            created_at=datetime.fromisoformat(row["created_at"]),
        )

    def _suppression_from_row(self, row: sqlite3.Row) -> SuppressionWindow:
        return SuppressionWindow(
            id=row["id"],
            tenant_id=row["tenant_id"],
            alert_id=row["alert_id"],
            scope=json.loads(row["scope_json"] or "{}"),
            starts_at=datetime.fromisoformat(row["starts_at"]),
            expires_at=datetime.fromisoformat(row["expires_at"]),
            reason=row["reason"],
            created_by=row["created_by"],
            active=bool(row["active"]),
        )
