"""Application context wiring migrations, repositories, and services."""

from __future__ import annotations

import sqlite3
from dataclasses import dataclass
from pathlib import Path

from watchtower.config.loader import load_settings
from watchtower.config.settings import WatchtowerSettings
from watchtower.services.audit import AuditService
from watchtower.services.bootstrap import BootstrapService
from watchtower.services.mode_controller import ModeController
from watchtower.services.tenant_context import TenantContext
from watchtower.storage.database import Database, init_database
from watchtower.storage.migrations.runner import apply_migrations
from watchtower.storage.repositories.audit import AuditRepository
from watchtower.storage.repositories.bootstrap import BootstrapRepository
from watchtower.storage.repositories.mode import ModeRepository
from watchtower.storage.repositories.tenant import TenantRepository


@dataclass
class AppContext:
    settings: WatchtowerSettings
    database: Database
    tenants: TenantRepository
    bootstrap: BootstrapRepository
    modes: ModeRepository
    audit_repo: AuditRepository
    audit: AuditService
    mode_controller: ModeController
    bootstrap_service: BootstrapService

    def session(self):
        return self.database.session()

    def run_migrations(self) -> list[str]:
        with self.database.session() as conn:
            return apply_migrations(conn, self.settings.migrations_dir)

    def with_connection(self, fn):
        with self.database.session() as conn:
            return fn(conn)


_app: AppContext | None = None


def init_app(
    *,
    settings: WatchtowerSettings | None = None,
    database_path: Path | None = None,
    run_migrations: bool = True,
) -> AppContext:
    """Initialize settings, database, migrations, and service graph."""
    global _app
    resolved_settings = settings or load_settings()
    if database_path is not None:
        resolved_settings = resolved_settings.model_copy(
            update={"database_path": database_path}
        )

    database = init_database(resolved_settings)
    if run_migrations:
        with database.session() as conn:
            apply_migrations(conn, resolved_settings.migrations_dir)

    def build(conn: sqlite3.Connection) -> AppContext:
        tenants = TenantRepository(conn)
        bootstrap = BootstrapRepository(conn)
        modes = ModeRepository(conn)
        audit_repo = AuditRepository(conn)
        audit = AuditService(audit_repo, resolved_settings)
        mode_controller = ModeController(modes, audit)
        bootstrap_service = BootstrapService(
            tenants,
            bootstrap,
            mode_controller,
            audit,
            default_tenant_slug=resolved_settings.default_tenant_slug,
        )
        return AppContext(
            settings=resolved_settings,
            database=database,
            tenants=tenants,
            bootstrap=bootstrap,
            modes=modes,
            audit_repo=audit_repo,
            audit=audit,
            mode_controller=mode_controller,
            bootstrap_service=bootstrap_service,
        )

    # Repositories are connection-scoped; CLI opens a session per command.
    _app = build(database.connect())
    database.connect().close()

    tenant = _app.bootstrap_service.get_default_tenant()
    if tenant is not None:
        TenantContext.set_current(tenant.id)

    return _app


def get_app_context() -> AppContext:
    if _app is None:
        msg = "Application not initialized"
        raise RuntimeError(msg)
    return _app


def create_session_context(settings: WatchtowerSettings | None = None) -> AppContext:
    """Create a fresh app context bound to one DB session (for CLI/tests)."""
    resolved = settings or load_settings()
    database = Database(resolved.database_path)
    with database.session() as conn:
        apply_migrations(conn, resolved.migrations_dir)
        tenants = TenantRepository(conn)
        bootstrap = BootstrapRepository(conn)
        modes = ModeRepository(conn)
        audit_repo = AuditRepository(conn)
        audit = AuditService(audit_repo, resolved)
        mode_controller = ModeController(modes, audit)
        bootstrap_service = BootstrapService(
            tenants,
            bootstrap,
            mode_controller,
            audit,
            default_tenant_slug=resolved.default_tenant_slug,
        )
        ctx = AppContext(
            settings=resolved,
            database=database,
            tenants=tenants,
            bootstrap=bootstrap,
            modes=modes,
            audit_repo=audit_repo,
            audit=audit,
            mode_controller=mode_controller,
            bootstrap_service=bootstrap_service,
        )
        tenant = bootstrap_service.get_default_tenant()
        if tenant is not None:
            TenantContext.set_current(tenant.id)
        return ctx
