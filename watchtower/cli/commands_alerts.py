"""Alert CLI commands."""

from __future__ import annotations

from typing import Annotated, Optional

import typer

from watchtower.cli.deps import require_bootstrap

alerts_app = typer.Typer(help="Alert lifecycle commands")


def _session(ctx: typer.Context):
    return ctx.obj.session().__enter__()


@alerts_app.command("list")
def alerts_list(
    ctx: typer.Context,
    status: Annotated[Optional[str], typer.Option("--status")] = None,
    severity: Annotated[Optional[str], typer.Option("--severity")] = None,
) -> None:
    wt_app = ctx.obj
    with wt_app.session() as session:
        tenant_id = require_bootstrap(session)
        rows = session.alerts.list_alerts(
            tenant_id, status=status, severity=severity
        )
    if not rows:
        typer.echo("(no alerts)")
        return
    for alert in rows:
        typer.echo(
            f"{alert.id}\t{alert.severity}\t{alert.status}\t"
            f"{alert.feature_id}\t{alert.title}"
        )


@alerts_app.command("show")
def alerts_show(
    ctx: typer.Context,
    alert_id: Annotated[str, typer.Argument(help="Alert id")],
) -> None:
    wt_app = ctx.obj
    with wt_app.session() as session:
        tenant_id = require_bootstrap(session)
        alert = session.alerts.get_alert(tenant_id, alert_id)
    if alert is None:
        typer.echo(f"alert not found: {alert_id}", err=True)
        raise typer.Exit(code=1)
    typer.echo(f"id: {alert.id}")
    typer.echo(f"feature: {alert.feature_id}")
    typer.echo(f"severity: {alert.severity}")
    typer.echo(f"status: {alert.status}")
    typer.echo(f"title: {alert.title}")
    if alert.summary:
        typer.echo(f"summary: {alert.summary}")


@alerts_app.command("ack")
def alerts_ack(
    ctx: typer.Context,
    alert_id: Annotated[str, typer.Argument(help="Alert id")],
) -> None:
    wt_app = ctx.obj
    with wt_app.session() as session:
        tenant_id = require_bootstrap(session)
        try:
            alert = session.alerts.acknowledge(tenant_id, alert_id, actor="cli-operator")
        except Exception as exc:
            typer.echo(str(exc), err=True)
            raise typer.Exit(code=1) from exc
    typer.echo(f"alert {alert.id} -> {alert.status}")


@alerts_app.command("close")
def alerts_close(
    ctx: typer.Context,
    alert_id: Annotated[str, typer.Argument(help="Alert id")],
    outcome: Annotated[
        str,
        typer.Option("--outcome", help="true_positive|false_positive"),
    ],
) -> None:
    if outcome not in ("true_positive", "false_positive"):
        typer.echo("outcome must be true_positive or false_positive", err=True)
        raise typer.Exit(code=1)
    wt_app = ctx.obj
    with wt_app.session() as session:
        tenant_id = require_bootstrap(session)
        try:
            alert = session.alerts.close(
                tenant_id,
                alert_id,
                outcome,  # type: ignore[arg-type]
                actor="cli-operator",
            )
        except Exception as exc:
            typer.echo(str(exc), err=True)
            raise typer.Exit(code=1) from exc
    typer.echo(f"alert {alert.id} closed as {outcome}")


@alerts_app.command("suppress")
def alerts_suppress(
    ctx: typer.Context,
    alert_id: Annotated[str, typer.Argument(help="Alert id")],
    duration: Annotated[str, typer.Option("--duration", help="e.g. 7d, 24h")] = "7d",
) -> None:
    wt_app = ctx.obj
    with wt_app.session() as session:
        tenant_id = require_bootstrap(session)
        try:
            window = session.alerts.suppress(
                tenant_id,
                alert_id,
                duration,
                actor="cli-operator",
            )
        except Exception as exc:
            typer.echo(str(exc), err=True)
            raise typer.Exit(code=1) from exc
    typer.echo(
        f"suppressed until {window.expires_at.isoformat()} (window={window.id[:8]})"
    )
