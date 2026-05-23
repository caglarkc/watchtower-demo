"""Watchtower `wt` CLI entrypoint."""

from __future__ import annotations

from pathlib import Path
from typing import Annotated, Optional

import typer

from watchtower import __version__
from watchtower.cli.deps import get_settings, require_bootstrap
from watchtower.domain.mode import VALID_MODES
from watchtower.services.app import create_app, init_app
from watchtower.services.bootstrap import BootstrapRequiredError

app = typer.Typer(
    name="wt",
    help="Watchtower UEBA — CLI-first operator interface",
    no_args_is_help=True,
)

modes_app = typer.Typer(help="Operating mode commands")
app.add_typer(modes_app, name="modes")


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
    username: Annotated[str, typer.Option(prompt=True)] = "admin",
    email: Annotated[str, typer.Option(prompt=True)] = "admin@localhost",
    password: Annotated[
        str,
        typer.Option(prompt=True, hide_input=True, confirmation_prompt=True),
    ] = "",
) -> None:
    """Create the bootstrap system administrator account."""
    wt_app = _get_ctx_app(ctx)
    if not password:
        typer.echo("Password cannot be empty", err=True)
        raise typer.Exit(code=1)

    with wt_app.session() as session:
        try:
            tenant, admin = session.bootstrap_service.bootstrap(
                username, email, password
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


def run() -> None:
    """Console script entrypoint."""
    app()


if __name__ == "__main__":
    run()
