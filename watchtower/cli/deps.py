"""CLI dependencies and guards."""

from __future__ import annotations

from pathlib import Path
from typing import Annotated

import typer

from watchtower.config.loader import load_settings
from watchtower.config.settings import WatchtowerSettings
from watchtower.services.app import AppContext, SessionContext, create_app, get_app_context, init_app
from watchtower.services.bootstrap import BootstrapRequiredError
from watchtower.services.tenant_context import TenantContext


def get_settings(
    db_path: Annotated[
        Path | None,
        typer.Option("--db", help="SQLite database path override"),
    ] = None,
    config: Annotated[
        Path | None,
        typer.Option("--config", help="YAML config file path"),
    ] = None,
) -> WatchtowerSettings:
    overrides: dict = {}
    if db_path is not None:
        overrides["database_path"] = db_path
    settings = load_settings(config_file=config, overrides=overrides or None)
    if db_path is not None:
        settings = settings.model_copy(update={"database_path": db_path})
    return settings


def get_app(
    db_path: Annotated[Path | None, typer.Option("--db")] = None,
    config: Annotated[Path | None, typer.Option("--config")] = None,
) -> AppContext:
    settings = get_settings(db_path=db_path, config=config)
    try:
        return get_app_context()
    except RuntimeError:
        return init_app(settings=settings, database_path=settings.database_path)


def with_session(
    app: AppContext,
) -> SessionContext:
    """Used inside commands via context manager in main wiring."""
    raise RuntimeError("Use app.session() context manager")


def require_bootstrap(session: SessionContext) -> str:
    tenant = session.bootstrap_service.get_default_tenant()
    if tenant is None:
        raise BootstrapRequiredError(
            "Bootstrap admin is required. Run `wt bootstrap` first."
        )
    session.bootstrap_service.require_bootstrapped(tenant.id)
    TenantContext.set_current(tenant.id)
    return tenant.id
