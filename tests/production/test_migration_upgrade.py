"""Upgrade migration path is idempotent and applies 009."""

from __future__ import annotations

import sqlite3

from watchtower.storage.migrations.runner import MigrationRunner


def test_upgrade_migration_idempotent(prod_app, prod_db):
    prod_app.run_migrations()
    second = prod_app.run_migrations()
    assert second == []

    with sqlite3.connect(prod_db) as conn:
        runner = MigrationRunner(prod_app.settings.migrations_dir)
        assert runner.list_pending(conn) == []
        versions = {
            row[0]
            for row in conn.execute("SELECT version FROM schema_migrations").fetchall()
        }
        tables = {
            row[0]
            for row in conn.execute(
                "SELECT name FROM sqlite_master WHERE type='table'"
            ).fetchall()
        }
    assert "009_production" in versions
    assert "system_metadata" in tables
    assert "retention_runs" in tables
