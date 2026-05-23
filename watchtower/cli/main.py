"""Watchtower `wt` CLI entrypoint."""

from __future__ import annotations

from pathlib import Path
from typing import Annotated, Optional

import typer

from watchtower import __version__
from watchtower.cli.deps import get_settings, require_bootstrap
from watchtower.domain.mode import VALID_MODES
from watchtower.services.app import create_app
from watchtower.services.bootstrap import BootstrapRequiredError
from watchtower.cli.commands_alerts import alerts_app
from watchtower.cli.commands_misc import (
    baseline_app,
    findings_app,
    register_query_command,
    rules_app,
)
from watchtower.cli.commands_production import (
    register_production_commands,
    register_sources_onboard,
)

app = typer.Typer(
    name="wt",
    help="Watchtower UEBA — CLI-first operator interface",
    no_args_is_help=True,
)

modes_app = typer.Typer(help="Operating mode commands")
sources_app = typer.Typer(help="Ingest source commands")
ingest_app = typer.Typer(help="Ingest commands")
app.add_typer(modes_app, name="modes")
app.add_typer(sources_app, name="sources")
app.add_typer(ingest_app, name="ingest")
app.add_typer(alerts_app, name="alerts")
app.add_typer(findings_app, name="findings")
app.add_typer(baseline_app, name="baseline")
app.add_typer(rules_app, name="rules")
register_query_command(app)
register_production_commands(app)
register_sources_onboard(sources_app)


def _open_app(
    db: Path | None = None,
    config: Path | None = None,
):
    settings = get_settings(db_path=db, config=config)
    return create_app(settings=settings, database_path=settings.database_path)


@app.callback()
def main(
    ctx: typer.Context,
    db: Annotated[Optional[Path], typer.Option("--db", help="SQLite DB path")] = None,
    config: Annotated[
        Optional[Path], typer.Option("--config", help="Config file path")
    ] = None,
) -> None:
    """Global options applied to subcommands."""
    settings = get_settings(db_path=db, config=config)
    ctx.obj = create_app(settings=settings, database_path=settings.database_path)


def _get_ctx_app(ctx: typer.Context):
    if ctx.obj is None:
        msg = "CLI context not initialized"
        raise typer.Exit(code=2)
    return ctx.obj


@app.command("bootstrap")
def bootstrap(
    ctx: typer.Context,
    username: Annotated[str, typer.Option("--username", "-u")] = "admin",
    email: Annotated[str, typer.Option("--email", "-e")] = "admin@localhost",
    password: Annotated[
        Optional[str],
        typer.Option("--password", hide_input=True),
    ] = None,
) -> None:
    """Create the bootstrap system administrator account."""
    wt_app = _get_ctx_app(ctx)
    resolved_password = password
    if resolved_password is None:
        resolved_password = typer.prompt("Password", hide_input=True)
        confirm = typer.prompt("Confirm password", hide_input=True)
        if resolved_password != confirm:
            typer.echo("Passwords do not match", err=True)
            raise typer.Exit(code=1)
    if not resolved_password:
        typer.echo("Password cannot be empty", err=True)
        raise typer.Exit(code=1)

    with wt_app.session() as session:
        try:
            tenant, admin = session.bootstrap_service.bootstrap(
                username, email, resolved_password
            )
        except ValueError as exc:
            typer.echo(str(exc), err=True)
            raise typer.Exit(code=1) from exc

        session.audit.log(
            "cli.bootstrap",
            tenant_id=tenant.id,
            actor=admin.username,
        )

    typer.echo(f"Bootstrap complete for tenant '{tenant.slug}' (admin: {admin.username})")


@app.command("status")
def status(ctx: typer.Context) -> None:
    """Show Watchtower installation status."""
    wt_app = _get_ctx_app(ctx)
    with wt_app.session() as session:
        tenant = session.bootstrap_service.get_default_tenant()
        bootstrapped = (
            tenant is not None
            and session.bootstrap_service.is_bootstrapped(tenant.id)
        )
        mode = None
        if bootstrapped and tenant is not None:
            mode = session.mode_controller.get_mode(tenant.id)

    typer.echo(f"watchtower_version: {__version__}")
    typer.echo(f"database: {wt_app.settings.database_path}")
    typer.echo(f"bootstrapped: {bootstrapped}")
    if tenant is not None:
        typer.echo(f"tenant: {tenant.slug} ({tenant.id})")
    if mode is not None:
        typer.echo(f"mode: {mode}")
    elif not bootstrapped:
        typer.echo("mode: (unavailable until bootstrap)")


@modes_app.command("get")
def modes_get(ctx: typer.Context) -> None:
    """Get the current operating mode."""
    wt_app = _get_ctx_app(ctx)
    with wt_app.session() as session:
        try:
            tenant_id = require_bootstrap(session)
            mode = session.mode_controller.get_mode(tenant_id)
        except BootstrapRequiredError as exc:
            typer.echo(str(exc), err=True)
            raise typer.Exit(code=1) from exc

    typer.echo(mode)


@modes_app.command("set")
def modes_set(
    ctx: typer.Context,
    mode: Annotated[str, typer.Argument(help="learn | run | hybrid")],
) -> None:
    """Set the operating mode."""
    if mode not in VALID_MODES:
        typer.echo(f"Invalid mode '{mode}'. Choose from: {', '.join(sorted(VALID_MODES))}")
        raise typer.Exit(code=1)

    wt_app = _get_ctx_app(ctx)
    with wt_app.session() as session:
        try:
            tenant_id = require_bootstrap(session)
            updated = session.mode_controller.set_mode(tenant_id, mode)  # type: ignore[arg-type]
        except BootstrapRequiredError as exc:
            typer.echo(str(exc), err=True)
            raise typer.Exit(code=1) from exc

    typer.echo(f"mode set to {updated}")


@sources_app.command("list")
def sources_list(ctx: typer.Context) -> None:
    """List configured ingest sources."""
    wt_app = _get_ctx_app(ctx)
    with wt_app.session() as session:
        try:
            tenant_id = require_bootstrap(session)
            rows = session.sources.list_for_tenant(tenant_id)
        except BootstrapRequiredError as exc:
            typer.echo(str(exc), err=True)
            raise typer.Exit(code=1) from exc

    if not rows:
        typer.echo("(no sources registered)")
        return
    for source in rows:
        flag = "enabled" if source.enabled else "disabled"
        typer.echo(f"{source.id}\t{source.connector_type}\t{source.name}\t{flag}")


@sources_app.command("health")
def sources_health(
    ctx: typer.Context,
    source_id: Annotated[
        Optional[str], typer.Option("--source", help="Source id (all if omitted)")
    ] = None,
) -> None:
    """Check connector health for one or all sources."""
    wt_app = _get_ctx_app(ctx)
    with wt_app.session() as session:
        try:
            tenant_id = require_bootstrap(session)
            targets = (
                [session.sources.get(source_id, tenant_id=tenant_id)]
                if source_id
                else session.sources.list_for_tenant(tenant_id)
            )
        except BootstrapRequiredError as exc:
            typer.echo(str(exc), err=True)
            raise typer.Exit(code=1) from exc

        for source in targets:
            if source is None:
                typer.echo(f"unknown source: {source_id}", err=True)
                raise typer.Exit(code=1)
            health = session.ingest.check_health(source)
            typer.echo(f"{source.id}\t{health.status}\t{health.message}")


@ingest_app.command("once")
def ingest_once(
    ctx: typer.Context,
    source_id: Annotated[str, typer.Option("--source", help="Source id")],
    limit: Annotated[
        Optional[int], typer.Option("--limit", help="Max events per poll")
    ] = None,
) -> None:
    """Poll a source once and store raw events."""
    wt_app = _get_ctx_app(ctx)
    batch_limit = limit or wt_app.settings.ingest_default_limit
    with wt_app.session() as session:
        try:
            tenant_id = require_bootstrap(session)
            result = session.ingest.ingest_once(tenant_id, source_id, limit=batch_limit)
            session.audit.log(
                "cli.ingest.once",
                tenant_id=tenant_id,
                details=result.model_dump(),
            )
        except BootstrapRequiredError as exc:
            typer.echo(str(exc), err=True)
            raise typer.Exit(code=1) from exc

    if result.error and result.stored == 0:
        typer.echo(f"ingest failed: {result.error}", err=True)
        raise typer.Exit(code=1)

    typer.echo(
        f"polled={result.polled} stored={result.stored} "
        f"duplicates={result.duplicates} has_more={result.has_more}"
    )
    if result.error:
        typer.echo(f"warning: {result.error}")


def run() -> None:
    """Console script entrypoint."""
    app()


if __name__ == "__main__":
    run()
