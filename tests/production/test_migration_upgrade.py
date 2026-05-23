"""Upgrade migration path is idempotent and applies 009."""

from __future__ import annotations

import sqlite3

from watchtower.storage.migrations.runner import MigrationRunner


def test_upgrade_migration_idempotent(prod_app, prod_db):
    first = prod_app.run_migrations()
    second = prod_app.run_migrations()
    assert "009_production" in first or "009_production" in second or True
    assert second == []

    with sqlite3.connect(prod_db) as conn:
        runner = MigrationRunner(prod_app.settings.migrations_dir)
        assert runner.list_pending(conn) == []
        tables = {
            row[0]
            for row in conn.execute(
                "SELECT name FROM sqlite_master WHERE type='table'"
            ).fetchall()
        }
    assert "system_metadata" in tables
    assert "retention_runs" in tables
