"""Case management CLI."""

from __future__ import annotations

from pathlib import Path
from typing import Annotated, Optional

import typer

from watchtower.alerts.service import AlertLifecycleError
from watchtower.cli.deps import require_bootstrap
from watchtower.services.bootstrap import BootstrapRequiredError

cases_app = typer.Typer(help="Alert case operator workflow")


def register_cases_commands(app: typer.Typer) -> None:
    app.add_typer(cases_app, name="cases")


@cases_app.command("list")
def cases_list(
    ctx: typer.Context,
    status: Annotated[Optional[str], typer.Option("--status")] = None,
    assignee: Annotated[Optional[str], typer.Option("--assignee")] = None,
) -> None:
    wt_app = ctx.obj
    with wt_app.session() as session:
        tenant_id = require_bootstrap(session)
        rows = session.alerts.list_cases(
            tenant_id, status=status, assigned_to=assignee
        )
    if not rows:
        typer.echo("(no cases)")
        return
    for case in rows:
        typer.echo(
            f"{case.id}\t{case.status}\tassignee={case.assigned_to or '-'}\t"
            f"alert={case.alert_id}\tticket={case.ticket_id or '-'}"
        )


@cases_app.command("show")
def cases_show(
    ctx: typer.Context,
    case_id: Annotated[str, typer.Argument(help="Case id")],
    explain: Annotated[bool, typer.Option("--explain", help="Generate LLM explanation")] = False,
) -> None:
    wt_app = ctx.obj
    with wt_app.session() as session:
        tenant_id = require_bootstrap(session)
        case = session.alerts.get_case(tenant_id, case_id)
        if case is None:
            typer.echo(f"case not found: {case_id}", err=True)
            raise typer.Exit(code=1)
        detail = session.alerts.get_alert_detail(
            tenant_id, case.alert_id, include_llm=explain
        )
    if detail is None:
        typer.echo("alert missing for case", err=True)
        raise typer.Exit(code=1)
    _render_alert_detail(detail)


@cases_app.command("assign")
def cases_assign(
    ctx: typer.Context,
    case_id: Annotated[str, typer.Argument(help="Case id")],
    assignee: Annotated[str, typer.Argument(help="Assignee id or name")],
) -> None:
    wt_app = ctx.obj
    with wt_app.session() as session:
        try:
            tenant_id = require_bootstrap(session)
            case = session.alerts.assign_case(
                tenant_id, case_id, assignee, actor="cli-operator"
            )
            session.conn.commit()
        except (BootstrapRequiredError, ValueError) as exc:
            typer.echo(str(exc), err=True)
            raise typer.Exit(code=1) from exc
    typer.echo(f"case {case.id} assigned to {assignee}")


@cases_app.command("comment")
def cases_comment(
    ctx: typer.Context,
    case_id: Annotated[str, typer.Argument(help="Case id")],
    text: Annotated[str, typer.Argument(help="Comment text")],
) -> None:
    wt_app = ctx.obj
    with wt_app.session() as session:
        try:
            tenant_id = require_bootstrap(session)
            entry = session.alerts.add_case_comment(
                tenant_id, case_id, text, actor="cli-operator"
            )
            session.conn.commit()
        except (BootstrapRequiredError, ValueError) as exc:
            typer.echo(str(exc), err=True)
            raise typer.Exit(code=1) from exc
    typer.echo(f"timeline entry {entry.id} ({entry.event_type})")


@cases_app.command("link-ticket")
def cases_link_ticket(
    ctx: typer.Context,
    case_id: Annotated[str, typer.Argument(help="Case id")],
    ticket_id: Annotated[str, typer.Argument(help="External ticket id")],
) -> None:
    wt_app = ctx.obj
    with wt_app.session() as session:
        try:
            tenant_id = require_bootstrap(session)
            case = session.alerts.get_case(tenant_id, case_id)
            if case is None:
                typer.echo(f"case not found: {case_id}", err=True)
                raise typer.Exit(code=1)
            session.alerts.link_ticket(
                tenant_id, case.alert_id, ticket_id, actor="cli-operator"
            )
            session.conn.commit()
        except (BootstrapRequiredError, AlertLifecycleError, ValueError) as exc:
            typer.echo(str(exc), err=True)
            raise typer.Exit(code=1) from exc
    typer.echo(f"linked ticket {ticket_id} to case {case_id}")


@cases_app.command("timeline")
def cases_timeline(
    ctx: typer.Context,
    case_id: Annotated[str, typer.Argument(help="Case id")],
) -> None:
    wt_app = ctx.obj
    with wt_app.session() as session:
        tenant_id = require_bootstrap(session)
        case = session.alerts.get_case(tenant_id, case_id)
        if case is None:
            typer.echo(f"case not found: {case_id}", err=True)
            raise typer.Exit(code=1)
        rows = session.alerts.get_timeline(tenant_id, case_id=case_id)
    if not rows:
        typer.echo("(empty timeline)")
        return
    for row in rows:
        meta = row.metadata
        extra = f" {meta}" if meta else ""
        typer.echo(
            f"{row.created_at.isoformat()}\t{row.event_type}\t{row.actor or '-'}{extra}"
        )
        if row.comment:
            typer.echo(f"  comment: {row.comment}")


@cases_app.command("export")
def cases_export(
    ctx: typer.Context,
    case_id: Annotated[str, typer.Argument(help="Case id")],
    fmt: Annotated[str, typer.Option("--format", help="json|md")] = "json",
    output: Annotated[
        Optional[Path], typer.Option("--output", "-o", help="Write to file")
    ] = None,
    explain: Annotated[bool, typer.Option("--explain")] = False,
) -> None:
    wt_app = ctx.obj
    with wt_app.session() as session:
        try:
            tenant_id = require_bootstrap(session)
            body = session.alerts.export_case(
                tenant_id, case_id, fmt=fmt, include_llm=explain
            )
        except (BootstrapRequiredError, ValueError) as exc:
            typer.echo(str(exc), err=True)
            raise typer.Exit(code=1) from exc
    if output:
        output.write_text(body, encoding="utf-8")
        typer.echo(f"wrote {output}")
    else:
        typer.echo(body)


def _render_alert_detail(detail) -> None:
    alert = detail.alert
    typer.echo(f"alert_id: {alert.id}")
    if detail.case:
        typer.echo(f"case_id: {detail.case.id}")
    typer.echo(f"feature: {alert.feature_id}")
    typer.echo(f"severity: {alert.severity}")
    typer.echo(f"status: {alert.status}")
    typer.echo(f"title: {alert.title}")
    if detail.assessment:
        typer.echo(f"detection_class: {detail.assessment.get('detection_class')}")
    if detail.score_breakdown:
        typer.echo("score_breakdown:")
        for comp in detail.score_breakdown.get("components", []):
            typer.echo(
                f"  - {comp.get('source')}: {comp.get('points')} — {comp.get('reason')}"
            )
    if detail.source_evidence.get("graph_audit"):
        typer.echo(f"graph_audit_nodes: {len(detail.source_evidence['graph_audit'])}")
    if detail.llm_explanation:
        typer.echo(f"llm_explanation: {detail.llm_explanation}")
