"""Apply ordered SQL migrations."""

from __future__ import annotations

import sqlite3
from datetime import UTC, datetime
from pathlib import Path


class MigrationRunner:
    """SQLite migration runner."""

    def __init__(self, migrations_dir: Path) -> None:
        self.migrations_dir = migrations_dir

    def list_pending(self, conn: sqlite3.Connection) -> list[Path]:
        applied = self._applied_versions(conn)
        pending: list[Path] = []
        for path in sorted(self.migrations_dir.glob("*.sql")):
            if path.stem not in applied:
                pending.append(path)
        return pending

    def apply_all(self, conn: sqlite3.Connection) -> list[str]:
        applied_versions: list[str] = []
        for path in self.list_pending(conn):
            sql = path.read_text(encoding="utf-8")
            conn.executescript(sql)
            conn.execute(
                "INSERT INTO schema_migrations (version, applied_at) VALUES (?, ?)",
                (path.stem, datetime.now(UTC).isoformat()),
            )
            applied_versions.append(path.stem)
        return applied_versions

    def _applied_versions(self, conn: sqlite3.Connection) -> set[str]:
        tables = conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='schema_migrations'"
        ).fetchone()
        if tables is None:
            return set()
        rows = conn.execute("SELECT version FROM schema_migrations").fetchall()
        return {row[0] for row in rows}


def apply_migrations(conn: sqlite3.Connection, migrations_dir: Path) -> list[str]:
    """Apply all pending migrations and return applied version ids."""
    runner = MigrationRunner(migrations_dir)
    return runner.apply_all(conn)
