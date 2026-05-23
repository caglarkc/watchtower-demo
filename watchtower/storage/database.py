"""SQLite connection wrapper with tenant-scoped helpers."""

from __future__ import annotations

import sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import Iterator

from watchtower.config.settings import WatchtowerSettings


class Database:
    """Thin SQLite database accessor."""

    def __init__(self, path: Path) -> None:
        self.path = path
        self.path.parent.mkdir(parents=True, exist_ok=True)

    def connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.path, check_same_thread=False)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON")
        return conn

    @contextmanager
    def session(self) -> Iterator[sqlite3.Connection]:
        conn = self.connect()
        try:
            yield conn
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()


_database: Database | None = None
_settings: WatchtowerSettings | None = None


def init_database(settings: WatchtowerSettings) -> Database:
    """Initialize the process-wide database handle."""
    global _database, _settings
    _database = Database(settings.database_path)
    _settings = settings
    return _database


def get_database() -> Database:
    if _database is None:
        msg = "Database not initialized; call init_database() first"
        raise RuntimeError(msg)
    return _database


def get_settings() -> WatchtowerSettings:
    if _settings is None:
        msg = "Settings not initialized"
        raise RuntimeError(msg)
    return _settings
