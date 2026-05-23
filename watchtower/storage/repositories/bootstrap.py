"""Bootstrap admin persistence."""

from __future__ import annotations

import sqlite3
import uuid
from datetime import UTC, datetime

from watchtower.domain.tenant import BootstrapAdmin
from watchtower.storage.security import hash_password


class BootstrapRepository:
    def __init__(self, conn: sqlite3.Connection) -> None:
        self._conn = conn

    def has_active_admin(self, tenant_id: str) -> bool:
        row = self._conn.execute(
            """
            SELECT 1 FROM bootstrap_admins
            WHERE tenant_id = ? AND is_active = 1
            LIMIT 1
            """,
            (tenant_id,),
        ).fetchone()
        return row is not None

    def create_admin(
        self,
        tenant_id: str,
        username: str,
        email: str,
        password: str,
    ) -> BootstrapAdmin:
        admin_id = str(uuid.uuid4())
        created_at = datetime.now(UTC).isoformat()
        password_hash = hash_password(password)
        self._conn.execute(
            """
            INSERT INTO bootstrap_admins
                (id, tenant_id, username, email, password_hash, is_active, created_at)
            VALUES (?, ?, ?, ?, ?, 1, ?)
            """,
            (admin_id, tenant_id, username, email, password_hash, created_at),
        )
        return BootstrapAdmin(
            id=admin_id,
            tenant_id=tenant_id,
            username=username,
            email=email,
            created_at=datetime.fromisoformat(created_at),
        )

    def count_for_tenant(self, tenant_id: str) -> int:
        row = self._conn.execute(
            "SELECT COUNT(*) AS cnt FROM bootstrap_admins WHERE tenant_id = ?",
            (tenant_id,),
        ).fetchone()
        return int(row["cnt"]) if row else 0

    def list_for_tenant(self, tenant_id: str) -> list[BootstrapAdmin]:
        rows = self._conn.execute(
            """
            SELECT id, tenant_id, username, email, is_active, created_at
            FROM bootstrap_admins
            WHERE tenant_id = ?
            ORDER BY created_at
            """,
            (tenant_id,),
        ).fetchall()
        return [
            BootstrapAdmin(
                id=row["id"],
                tenant_id=row["tenant_id"],
                username=row["username"],
                email=row["email"],
                is_active=bool(row["is_active"]),
                created_at=datetime.fromisoformat(row["created_at"]),
            )
            for row in rows
        ]
