"""Tenant persistence."""

from __future__ import annotations

import sqlite3
import uuid
from datetime import UTC, datetime

from watchtower.domain.tenant import Tenant


class TenantRepository:
    def __init__(self, conn: sqlite3.Connection) -> None:
        self._conn = conn

    def get_by_slug(self, slug: str) -> Tenant | None:
        row = self._conn.execute(
            "SELECT id, name, slug, created_at FROM tenants WHERE slug = ?",
            (slug,),
        ).fetchone()
        if row is None:
            return None
        return Tenant(
            id=row["id"],
            name=row["name"],
            slug=row["slug"],
            created_at=datetime.fromisoformat(row["created_at"]),
        )

    def get_by_id(self, tenant_id: str) -> Tenant | None:
        row = self._conn.execute(
            "SELECT id, name, slug, created_at FROM tenants WHERE id = ?",
            (tenant_id,),
        ).fetchone()
        if row is None:
            return None
        return Tenant(
            id=row["id"],
            name=row["name"],
            slug=row["slug"],
            created_at=datetime.fromisoformat(row["created_at"]),
        )

    def create(self, name: str, slug: str) -> Tenant:
        tenant_id = str(uuid.uuid4())
        created_at = datetime.now(UTC).isoformat()
        self._conn.execute(
            "INSERT INTO tenants (id, name, slug, created_at) VALUES (?, ?, ?, ?)",
            (tenant_id, name, slug, created_at),
        )
        return Tenant(
            id=tenant_id,
            name=name,
            slug=slug,
            created_at=datetime.fromisoformat(created_at),
        )

    def list_all(self) -> list[Tenant]:
        rows = self._conn.execute(
            "SELECT id, name, slug, created_at FROM tenants ORDER BY created_at"
        ).fetchall()
        return [
            Tenant(
                id=row["id"],
                name=row["name"],
                slug=row["slug"],
                created_at=datetime.fromisoformat(row["created_at"]),
            )
            for row in rows
        ]
