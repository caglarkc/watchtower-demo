"""SQLite backup/restore for closed-network deployments."""

from __future__ import annotations

import json
import shutil
import sqlite3
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path


class RestoreError(RuntimeError):
    """Backup restore failed validation."""


@dataclass
class BackupManifest:
    path: Path
    created_at: str
    source_db: str
    schema_versions: list[str]


class BackupService:
    def __init__(self, backup_dir: Path) -> None:
        self.backup_dir = Path(backup_dir)
        self.backup_dir.mkdir(parents=True, exist_ok=True)

    def create_backup(self, database_path: Path) -> BackupManifest:
        database_path = Path(database_path)
        if not database_path.is_file():
            msg = f"database not found: {database_path}"
            raise FileNotFoundError(msg)

        stamp = datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ")
        dest = self.backup_dir / f"watchtower-{stamp}.db"
        manifest_path = self.backup_dir / f"watchtower-{stamp}.manifest.json"

        with sqlite3.connect(database_path) as source, sqlite3.connect(dest) as target:
            source.backup(target)

        versions = self._schema_versions(dest)
        manifest = BackupManifest(
            path=dest,
            created_at=datetime.now(UTC).isoformat(),
            source_db=str(database_path.resolve()),
            schema_versions=versions,
        )
        manifest_path.write_text(
            json.dumps(
                {
                    "path": str(dest.name),
                    "created_at": manifest.created_at,
                    "source_db": manifest.source_db,
                    "schema_versions": manifest.schema_versions,
                },
                indent=2,
            ),
            encoding="utf-8",
        )
        return manifest

    def restore_backup(self, backup_path: Path, database_path: Path) -> None:
        backup_path = Path(backup_path)
        database_path = Path(database_path)
        if not backup_path.is_file():
            msg = f"backup not found: {backup_path}"
            raise FileNotFoundError(msg)

        with sqlite3.connect(backup_path) as conn:
            tables = {
                row[0]
                for row in conn.execute(
                    "SELECT name FROM sqlite_master WHERE type='table'"
                ).fetchall()
            }
        required = {"schema_migrations", "tenants"}
        if not required.issubset(tables):
            raise RestoreError(f"backup missing required tables: {required - tables}")

        database_path.parent.mkdir(parents=True, exist_ok=True)
        if database_path.exists():
            stale = database_path.with_suffix(".db.pre-restore")
            shutil.copy2(database_path, stale)
        shutil.copy2(backup_path, database_path)

    def list_backups(self) -> list[Path]:
        return sorted(self.backup_dir.glob("watchtower-*.db"), reverse=True)

    @staticmethod
    def _schema_versions(db_path: Path) -> list[str]:
        with sqlite3.connect(db_path) as conn:
            row = conn.execute(
                "SELECT name FROM sqlite_master WHERE type='table' AND name='schema_migrations'"
            ).fetchone()
            if row is None:
                return []
            rows = conn.execute(
                "SELECT version FROM schema_migrations ORDER BY version"
            ).fetchall()
        return [r[0] for r in rows]
