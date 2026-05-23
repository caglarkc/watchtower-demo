"""Application context wiring migrations, repositories, and services."""

from __future__ import annotations

import sqlite3
from contextlib import contextmanager
from dataclasses import dataclass
from pathlib import Path
from typing import Iterator

from watchtower.config.loader import load_settings
from watchtower.config.settings import WatchtowerSettings
from watchtower.services.audit import AuditService
from watchtower.services.bootstrap import BootstrapService
from watchtower.services.mode_controller import ModeController
from watchtower.services.tenant_context import TenantContext
from watchtower.storage.database import Database
from watchtower.storage.migrations.runner import apply_migrations
from watchtower.storage.repositories.audit import AuditRepository
from watchtower.storage.repositories.bootstrap import BootstrapRepository
from watchtower.storage.repositories.mode import ModeRepository
from watchtower.ingest.service import IngestService
from watchtower.storage.repositories.raw_event import RawEventRepository
from watchtower.storage.repositories.source import SourceRepository
from watchtower.storage.repositories.source_cursor import SourceCursorRepository
from watchtower.storage.repositories.tenant import TenantRepository


@dataclass
class SessionContext:
    """Connection-scoped services for one database transaction."""

    conn: sqlite3.Connection
    settings: WatchtowerSettings
    database: Database
    tenants: TenantRepository
    bootstrap: BootstrapRepository
    modes: ModeRepository
    audit_repo: AuditRepository
    audit: AuditService
    mode_controller: ModeController
    bootstrap_service: BootstrapService
    sources: SourceRepository
    source_cursors: SourceCursorRepository
    raw_events: RawEventRepository
    ingest: IngestService

    def set_default_tenant_context(self) -> str | None:
        tenant = self.bootstrap_service.get_default_tenant()
        if tenant is None:
            TenantContext.clear()
            return None
        TenantContext.set_current(tenant.id)
        return tenant.id


@dataclass
class AppContext:
    settings: WatchtowerSettings
    database: Database

    def run_migrations(self) -> list[str]:
        with self.database.session() as conn:
            return apply_migrations(conn, self.settings.migrations_dir)

    @contextmanager
    def session(self) -> Iterator[SessionContext]:
        with self.database.session() as conn:
            ctx = _build_session(conn, self.settings, self.database)
            tenant_id = ctx.set_default_tenant_context()
            try:
                yield ctx
            finally:
                if tenant_id is not None:
                    TenantContext.clear()


def _build_session(
    conn: sqlite3.Connection,
    settings: WatchtowerSettings,
    database: Database,
) -> SessionContext:
    tenants = TenantRepository(conn)
    bootstrap = BootstrapRepository(conn)
    modes = ModeRepository(conn)
    audit_repo = AuditRepository(conn)
    audit = AuditService(audit_repo, settings)
    mode_controller = ModeController(modes, audit)
    bootstrap_service = BootstrapService(
        tenants,
        bootstrap,
        mode_controller,
        audit,
        default_tenant_slug=settings.default_tenant_slug,
    )
    return SessionContext(
        conn=conn,
        settings=settings,
        database=database,
        tenants=tenants,
        bootstrap=bootstrap,
        modes=modes,
        audit_repo=audit_repo,
        audit=audit,
        mode_controller=mode_controller,
        bootstrap_service=bootstrap_service,
    )


_app: AppContext | None = None


def init_app(
    *,
    settings: WatchtowerSettings | None = None,
    database_path: Path | None = None,
    run_migrations: bool = True,
) -> AppContext:
    """Initialize global app context (settings + database)."""
    global _app
    resolved_settings = settings or load_settings()
    if database_path is not None:
        resolved_settings = resolved_settings.model_copy(
            update={"database_path": database_path}
        )

    database = Database(resolved_settings.database_path)
    _app = AppContext(settings=resolved_settings, database=database)
    if run_migrations:
        _app.run_migrations()
    return _app


def get_app_context() -> AppContext:
    if _app is None:
        msg = "Application not initialized"
        raise RuntimeError(msg)
    return _app


def create_app(
    *,
    settings: WatchtowerSettings | None = None,
    database_path: Path | None = None,
    run_migrations: bool = True,
) -> AppContext:
    """Create an isolated app context (tests) without touching the global singleton."""
    resolved_settings = settings or load_settings()
    if database_path is not None:
        resolved_settings = resolved_settings.model_copy(
            update={"database_path": database_path}
        )
    app = AppContext(settings=resolved_settings, database=Database(resolved_settings.database_path))
    if run_migrations:
        app.run_migrations()
    return app
