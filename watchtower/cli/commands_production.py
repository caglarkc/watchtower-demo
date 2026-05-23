"""Production readiness CLI: health, backup, retention, migrate, onboarding."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Annotated, Optional

import typer

from watchtower.backup.service import BackupService, RestoreError
from watchtower.cli.deps import require_bootstrap
from watchtower.health.service import HealthService
from watchtower.llm.providers.onboarding import (
    clear_provider_chain,
    resolve_provider_chain,
    set_provider_chain,
)
from watchtower.retention.service import RetentionService
from watchtower.security.masking import mask_mapping
from watchtower.services.bootstrap import BootstrapRequiredError
from watchtower.sources.onboarding import SUPPORTED_CONNECTORS, SourceOnboardingService
from watchtower.storage.migrations.runner import MigrationRunner

health_app = typer.Typer(help="Health check commands")
backup_app = typer.Typer(help="Backup and restore")
retention_app = typer.Typer(help="Data retention")
migrate_app = typer.Typer(help="Database migrations")
providers_app = typer.Typer(help="LLM provider onboarding")


def register_production_commands(app: typer.Typer) -> None:
    app.add_typer(health_app, name="health")
    app.add_typer(backup_app, name="backup")
    app.add_typer(retention_app, name="retention")
    app.add_typer(migrate_app, name="migrate")
    app.add_typer(providers_app, name="providers")


@health_app.callback(invoke_without_command=True)
def health_root(
    ctx: typer.Context,
    json_output: Annotated[bool, typer.Option("--json", help="JSON output")] = False,
) -> None:
    """Run all health checks (exit 1 if unhealthy)."""
    wt_app = ctx.obj
    svc = HealthService()
    with wt_app.session() as session:
        report = svc.run(
            conn=session.conn,
            settings=wt_app.settings,
            session=session,
        )
    if json_output:
        typer.echo(report.to_json())
    else:
        typer.echo(f"status: {report.status}")
        typer.echo(f"version: {report.version}")
        for check in report.checks:
            typer.echo(f"  {check.name}: {check.status} — {check.message}")
    if report.status == "unhealthy":
        raise typer.Exit(code=1)


@backup_app.command("create")
def backup_create(ctx: typer.Context) -> None:
    """Create a SQLite backup under WATCHTOWER_BACKUP_DIR."""
    wt_app = ctx.obj
    svc = BackupService(wt_app.settings.backup_dir)
    manifest = svc.create_backup(wt_app.settings.database_path)
    typer.echo(f"backup: {manifest.path}")
    typer.echo(f"migrations: {', '.join(manifest.schema_versions)}")


@backup_app.command("list")
def backup_list(ctx: typer.Context) -> None:
    wt_app = ctx.obj
    svc = BackupService(wt_app.settings.backup_dir)
    rows = svc.list_backups()
    if not rows:
        typer.echo("(no backups)")
        return
    for path in rows:
        typer.echo(path)


@backup_app.command("restore")
def backup_restore(
    ctx: typer.Context,
    backup_file: Annotated[Path, typer.Argument(help="Backup .db file path")],
    yes: Annotated[bool, typer.Option("--yes", help="Skip confirmation")] = False,
) -> None:
    wt_app = ctx.obj
    if not yes:
        typer.confirm(
            f"Restore {backup_file} over {wt_app.settings.database_path}?",
            abort=True,
        )
    svc = BackupService(wt_app.settings.backup_dir)
    try:
        svc.restore_backup(backup_file, wt_app.settings.database_path)
    except RestoreError as exc:
        typer.echo(str(exc), err=True)
        raise typer.Exit(code=1) from exc
    typer.echo("restore complete")


@retention_app.command("apply")
def retention_apply(
    ctx: typer.Context,
    dry_run: Annotated[bool, typer.Option("--dry-run", help="Count only")] = False,
) -> None:
    """Apply retention policy (raw events, normalized, audit, LLM audit)."""
    wt_app = ctx.obj
    with wt_app.session() as session:
        try:
            tenant_id = require_bootstrap(session)
            svc = RetentionService(session.conn, wt_app.settings)
            result = svc.apply(tenant_id=tenant_id, dry_run=dry_run)
        except BootstrapRequiredError as exc:
            typer.echo(str(exc), err=True)
            raise typer.Exit(code=1) from exc
    prefix = "would delete" if dry_run else "deleted"
    for table, count in result.deleted.items():
        typer.echo(f"{prefix} {table}: {count}")


@migrate_app.command("status")
def migrate_status(ctx: typer.Context) -> None:
    wt_app = ctx.obj
    with wt_app.database.session() as conn:
        runner = MigrationRunner(wt_app.settings.migrations_dir)
        pending = runner.list_pending(conn)
        applied = conn.execute("SELECT version FROM schema_migrations ORDER BY version").fetchall()
    typer.echo(f"applied: {len(applied)}")
    for row in applied:
        typer.echo(f"  {row[0]}")
    if pending:
        typer.echo(f"pending: {len(pending)}")
        for path in pending:
            typer.echo(f"  {path.stem}")
    else:
        typer.echo("pending: 0")


@migrate_app.command("upgrade")
def migrate_upgrade(ctx: typer.Context) -> None:
    wt_app = ctx.obj
    applied = wt_app.run_migrations()
    if applied:
        typer.echo(f"applied: {', '.join(applied)}")
    else:
        typer.echo("no pending migrations")


@providers_app.command("list")
def providers_list(ctx: typer.Context) -> None:
    wt_app = ctx.obj
    with wt_app.session() as session:
        chain = resolve_provider_chain(wt_app.settings, session.conn)
        stored = session.conn.execute(
            "SELECT value FROM system_metadata WHERE key = 'llm_provider_chain'"
        ).fetchone()
    typer.echo(f"env_chain: {wt_app.settings.llm_provider_chain}")
    if stored:
        typer.echo(f"active_chain (db): {stored[0]}")
    typer.echo(f"resolved_providers: {', '.join(p.name for p in chain) or '(none)'}")


@providers_app.command("set-chain")
def providers_set_chain(
    ctx: typer.Context,
    chain: Annotated[str, typer.Argument(help="Comma-separated provider names")],
) -> None:
    """Persist provider fallback order (overrides env until cleared)."""
    wt_app = ctx.obj
    with wt_app.session() as session:
        set_provider_chain(session.conn, chain)
        session.conn.commit()
    typer.echo(f"provider chain set to: {chain}")


@providers_app.command("clear-chain")
def providers_clear_chain(ctx: typer.Context) -> None:
    wt_app = ctx.obj
    with wt_app.session() as session:
        clear_provider_chain(session.conn)
        session.conn.commit()
    typer.echo("provider chain override cleared (using env)")


def register_sources_onboard(sources_app: typer.Typer) -> None:
    @sources_app.command("register")
    def sources_register(
        ctx: typer.Context,
        connector_type: Annotated[str, typer.Option("--type", "-t", help="Connector type")],
        name: Annotated[str, typer.Option("--name", "-n", help="Human-readable name")],
        config_json: Annotated[
            Optional[str],
            typer.Option("--config", "-c", help="JSON config object"),
        ] = None,
        source_id: Annotated[
            Optional[str], typer.Option("--id", help="Optional stable source id")
        ] = None,
    ) -> None:
        """Onboard a new ingest source."""
        if connector_type not in SUPPORTED_CONNECTORS:
            typer.echo(
                f"Invalid connector '{connector_type}'. "
                f"Choose: {', '.join(SUPPORTED_CONNECTORS)}",
                err=True,
            )
            raise typer.Exit(code=1)
        config: dict = {}
        if config_json:
            try:
                config = json.loads(config_json)
            except json.JSONDecodeError as exc:
                typer.echo(f"invalid JSON config: {exc}", err=True)
                raise typer.Exit(code=1) from exc

        wt_app = ctx.obj
        with wt_app.session() as session:
            try:
                tenant_id = require_bootstrap(session)
                onboard = SourceOnboardingService(session.sources)
                source = onboard.register(
                    tenant_id,
                    connector_type,
                    name,
                    config,
                    source_id=source_id,
                )
                session.audit.log(
                    "cli.sources.register",
                    tenant_id=tenant_id,
                    details={
                        "source_id": source.id,
                        "connector_type": connector_type,
                        "config": mask_mapping(config),
                    },
                )
            except ValueError as exc:
                typer.echo(str(exc), err=True)
                raise typer.Exit(code=1) from exc
            except BootstrapRequiredError as exc:
                typer.echo(str(exc), err=True)
                raise typer.Exit(code=1) from exc

        typer.echo(f"registered source {source.id} ({connector_type})")
        typer.echo(SourceOnboardingService.config_preview(config))
