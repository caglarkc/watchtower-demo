"""SQLite migration tests."""

from __future__ import annotations

import sqlite3

from watchtower.storage.migrations.runner import MigrationRunner


def test_fresh_db_migration_applies_initial_schema(settings):
    runner = MigrationRunner(settings.migrations_dir)
    conn = sqlite3.connect(settings.database_path)
    conn.row_factory = sqlite3.Row
    try:
        pending = runner.list_pending(conn)
        assert len(pending) >= 1
        applied = runner.apply_all(conn)
        conn.commit()
        assert "001_initial" in applied

        tables = {
            row[0]
            for row in conn.execute(
                "SELECT name FROM sqlite_master WHERE type='table'"
            ).fetchall()
        }
        assert "tenants" in tables
        assert "bootstrap_admins" in tables
        assert "tenant_runtime" in tables
        assert "audit_log" in tables
        assert "schema_migrations" in tables

        pending_after = runner.list_pending(conn)
        assert pending_after == []
    finally:
        conn.close()
