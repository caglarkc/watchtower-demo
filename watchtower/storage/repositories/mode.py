"""Tenant operating mode persistence."""

from __future__ import annotations

import sqlite3
from datetime import UTC, datetime

from watchtower.domain.mode import DEFAULT_MODE, VALID_MODES, WatchtowerMode


class ModeRepository:
    def __init__(self, conn: sqlite3.Connection) -> None:
        self._conn = conn

    def ensure_runtime_row(self, tenant_id: str) -> None:
        row = self._conn.execute(
            "SELECT tenant_id FROM tenant_runtime WHERE tenant_id = ?",
            (tenant_id,),
        ).fetchone()
        if row is None:
            now = datetime.now(UTC).isoformat()
            self._conn.execute(
                """
                INSERT INTO tenant_runtime (tenant_id, mode, updated_at)
                VALUES (?, ?, ?)
                """,
                (tenant_id, DEFAULT_MODE, now),
            )

    def get_mode(self, tenant_id: str) -> WatchtowerMode:
        self.ensure_runtime_row(tenant_id)
        row = self._conn.execute(
            "SELECT mode FROM tenant_runtime WHERE tenant_id = ?",
            (tenant_id,),
        ).fetchone()
        mode = row["mode"] if row else DEFAULT_MODE
        if mode not in VALID_MODES:
            msg = f"Invalid mode stored for tenant {tenant_id}: {mode}"
            raise ValueError(msg)
        return mode  # type: ignore[return-value]

    def set_mode(self, tenant_id: str, mode: WatchtowerMode) -> WatchtowerMode:
        if mode not in VALID_MODES:
            msg = f"Invalid mode: {mode}"
            raise ValueError(msg)
        self.ensure_runtime_row(tenant_id)
        now = datetime.now(UTC).isoformat()
        self._conn.execute(
            """
            UPDATE tenant_runtime SET mode = ?, updated_at = ?
            WHERE tenant_id = ?
            """,
            (mode, now, tenant_id),
        )
        return mode
