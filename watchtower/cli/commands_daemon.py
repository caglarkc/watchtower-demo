"""Daemon pipeline CLI."""

from __future__ import annotations

import signal
import time
from typing import Annotated, Optional

import typer

from watchtower.cli.deps import require_bootstrap
from watchtower.daemon.service import DaemonService
from watchtower.services.bootstrap import BootstrapRequiredError

daemon_app = typer.Typer(help="Daemon pipeline runtime")


class _ShutdownController:
    def __init__(self) -> None:
        self.requested = False

    def install(self) -> None:
        def _handler(signum: int, _frame: object) -> None:
            self.requested = True

        signal.signal(signal.SIGINT, _handler)
        signal.signal(signal.SIGTERM, _handler)


def register_daemon_commands(app: typer.Typer) -> None:
    app.add_typer(daemon_app, name="daemon")


@daemon_app.command("run")
def daemon_run(
    ctx: typer.Context,
    once: Annotated[bool, typer.Option("--once", help="Run a single loop iteration")] = False,
    max_iterations: Annotated[
        Optional[int],
        typer.Option("--max-iterations", min=1, help="Stop after N loop iterations"),
    ] = None,
    interval: Annotated[
        Optional[int],
        typer.Option(
            "--interval",
            min=5,
            help="Seconds between loop iterations (default: WATCHTOWER_DAEMON_INGEST_INTERVAL_SECONDS)",
        ),
    ] = None,
    ingest_limit: Annotated[
        Optional[int],
        typer.Option("--ingest-limit", min=1, help="Max events per source poll"),
    ] = None,
    pipeline_limit: Annotated[
        int,
        typer.Option("--pipeline-limit", min=1, help="Max raw events to normalize per loop"),
    ] = 500,
    graph_limit: Annotated[
        int,
        typer.Option("--graph-limit", min=1, help="Max graph runs per loop"),
    ] = 100,
) -> None:
    """Run ingest → normalize → candidate → graph → alert/finding loop."""
    wt_app = ctx.obj
    sleep_seconds = interval or wt_app.settings.daemon_ingest_interval_seconds
    shutdown = _ShutdownController()
    shutdown.install()

    iteration = 0
    while True:
        iteration += 1
        with wt_app.session() as session:
            try:
                tenant_id = require_bootstrap(session)
                daemon = DaemonService(session)
                summary = daemon.run_once(
                    tenant_id,
                    iteration=iteration,
                    ingest_limit=ingest_limit,
                    pipeline_limit=pipeline_limit,
                    graph_limit=graph_limit,
                )
                session.audit.log(
                    "daemon.loop",
                    tenant_id=tenant_id,
                    actor="daemon",
                    details=summary.to_audit_details(),
                )
                session.conn.commit()
            except BootstrapRequiredError as exc:
                typer.echo(str(exc), err=True)
                raise typer.Exit(code=1) from exc

        typer.echo(
            f"loop={summary.iteration} mode={summary.mode} "
            f"sources={summary.sources_polled} raw_stored={summary.raw_stored} "
            f"normalized={summary.pipeline.get('normalized', 0)} "
            f"candidates={summary.pipeline.get('candidates', 0)} "
            f"graph_runs={summary.graph_runs} alerts={summary.alerts_created} "
            f"silent={summary.silent_findings} learning={summary.learning_events}"
        )
        if summary.errors:
            for err in summary.errors:
                typer.echo(f"warning: {err}", err=True)

        if once or max_iterations is not None and iteration >= max_iterations:
            break
        if shutdown.requested:
            typer.echo("shutdown requested, exiting daemon")
            break
        time.sleep(sleep_seconds)
