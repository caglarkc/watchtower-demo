"""Backup and restore round-trip."""

from __future__ import annotations

import sqlite3

from watchtower.backup.service import BackupService


def test_backup_restore_round_trip(prod_app, bootstrapped_tenant, prod_db, prod_settings):
    with prod_app.session() as session:
        session.sources.create(
            bootstrapped_tenant,
            "mock",
            "backup-test",
            config={"events": []},
            source_id="src-backup-1",
        )
        session.conn.commit()

    svc = BackupService(prod_settings.backup_dir)
    manifest = svc.create_backup(prod_db)
    assert manifest.path.is_file()

    with sqlite3.connect(prod_db) as conn:
        conn.execute("DELETE FROM sources")
        conn.commit()
        count = conn.execute("SELECT COUNT(*) FROM sources").fetchone()[0]
    assert count == 0

    svc.restore_backup(manifest.path, prod_db)
    with sqlite3.connect(prod_db) as conn:
        restored = conn.execute("SELECT COUNT(*) FROM sources").fetchone()[0]
    assert restored == 1
