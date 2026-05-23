"""Durable runtime counters and loop-duration aggregates."""

from __future__ import annotations

import sqlite3
from datetime import UTC, datetime
from typing import Any


class MetricsRepository:
    def __init__(self, conn: sqlite3.Connection) -> None:
        self._conn = conn

    def increment(
        self,
        tenant_id: str,
        metric_name: str,
        delta: float = 1.0,
    ) -> float:
        now = datetime.now(UTC).isoformat()
        self._conn.execute(
            """
            INSERT INTO runtime_metrics (tenant_id, metric_name, value, updated_at)
            VALUES (?, ?, ?, ?)
            ON CONFLICT(tenant_id, metric_name) DO UPDATE SET
                value = runtime_metrics.value + excluded.value,
                updated_at = excluded.updated_at
            """,
            (tenant_id, metric_name, delta, now),
        )
        row = self._conn.execute(
            """
            SELECT value FROM runtime_metrics
            WHERE tenant_id = ? AND metric_name = ?
            """,
            (tenant_id, metric_name),
        ).fetchone()
        return float(row[0]) if row else delta

    def record_loop_duration(self, tenant_id: str, duration_ms: float) -> None:
        now = datetime.now(UTC).isoformat()
        self._conn.execute(
            """
            INSERT INTO runtime_metrics (tenant_id, metric_name, value, updated_at)
            VALUES (?, 'loop_duration_ms_count', 1, ?)
            ON CONFLICT(tenant_id, metric_name) DO UPDATE SET
                value = runtime_metrics.value + 1,
                updated_at = excluded.updated_at
            """,
            (tenant_id, now),
        )
        for suffix, delta in (
            ("loop_duration_ms_sum", duration_ms),
            ("loop_duration_ms_last", duration_ms),
        ):
            if suffix == "loop_duration_ms_last":
                self._conn.execute(
                    """
                    INSERT INTO runtime_metrics (tenant_id, metric_name, value, updated_at)
                    VALUES (?, ?, ?, ?)
                    ON CONFLICT(tenant_id, metric_name) DO UPDATE SET
                        value = excluded.value,
                        updated_at = excluded.updated_at
                    """,
                    (tenant_id, suffix, delta, now),
                )
            else:
                self._conn.execute(
                    """
                    INSERT INTO runtime_metrics (tenant_id, metric_name, value, updated_at)
                    VALUES (?, ?, ?, ?)
                    ON CONFLICT(tenant_id, metric_name) DO UPDATE SET
                        value = runtime_metrics.value + excluded.value,
                        updated_at = excluded.updated_at
                    """,
                    (tenant_id, suffix, delta, now),
                )
        row = self._conn.execute(
            """
            SELECT value FROM runtime_metrics
            WHERE tenant_id = ? AND metric_name = 'loop_duration_ms_max'
            """,
            (tenant_id,),
        ).fetchone()
        current_max = float(row[0]) if row else 0.0
        if duration_ms > current_max:
            self._conn.execute(
                """
                INSERT INTO runtime_metrics (tenant_id, metric_name, value, updated_at)
                VALUES (?, 'loop_duration_ms_max', ?, ?)
                ON CONFLICT(tenant_id, metric_name) DO UPDATE SET
                    value = excluded.value,
                    updated_at = excluded.updated_at
                """,
                (tenant_id, duration_ms, now),
            )

    def get_snapshot(self, tenant_id: str) -> dict[str, float]:
        rows = self._conn.execute(
            """
            SELECT metric_name, value FROM runtime_metrics
            WHERE tenant_id = ?
            ORDER BY metric_name
            """,
            (tenant_id,),
        ).fetchall()
        return {row[0]: float(row[1]) for row in rows}

    def get_global_snapshot(self) -> dict[str, float]:
        rows = self._conn.execute(
            """
            SELECT metric_name, SUM(value) AS total
            FROM runtime_metrics
            GROUP BY metric_name
            ORDER BY metric_name
            """
        ).fetchall()
        return {row[0]: float(row[1]) for row in rows}
