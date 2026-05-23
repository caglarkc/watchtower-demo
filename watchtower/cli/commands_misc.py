"""Findings, baseline, rules, and query CLI commands."""

from __future__ import annotations

import json
from typing import Annotated, Optional

import typer

from watchtower.cli.deps import require_bootstrap
findings_app = typer.Typer(help="Silent findings commands")
baseline_app = typer.Typer(help="Baseline profile commands")
rules_app = typer.Typer(help="Feedback rule approval commands")


@findings_app.command("silent")
def findings_silent(
    ctx: typer.Context,
    last: Annotated[str, typer.Option("--last", help="e.g. 7d")] = "7d",
) -> None:
    from datetime import UTC, datetime, timedelta

    wt_app = ctx.obj
    if last.endswith("d"):
        since = datetime.now(UTC) - timedelta(days=int(last[:-1]))
    elif last.endswith("h"):
        since = datetime.now(UTC) - timedelta(hours=int(last[:-1]))
    else:
        since = datetime.now(UTC) - timedelta(days=7)
    with wt_app.session() as session:
        tenant_id = require_bootstrap(session)
        rows = session.alerts.list_silent_findings(tenant_id, since=since)
    if not rows:
        typer.echo("(no silent findings)")
        return
    for row in rows:
        typer.echo(
            f"{row['id'][:8]}\t{row['feature_id']}\t{row['severity']}\t{row['created_at']}"
        )


@baseline_app.command("user")
def baseline_user(
    ctx: typer.Context,
    user_id: Annotated[str, typer.Argument(help="User id")],
) -> None:
    wt_app = ctx.obj
    with wt_app.session() as session:
        tenant_id = require_bootstrap(session)
        profile = session.baseline._repo.get_user_profile(tenant_id, user_id)
    if profile is None:
        typer.echo(f"no profile for user {user_id}")
        raise typer.Exit(code=1)
    typer.echo(json.dumps(profile.model_dump(mode="json"), indent=2, default=str))


@baseline_app.command("department")
def baseline_department(
    ctx: typer.Context,
    department_id: Annotated[str, typer.Argument(help="Department id")],
) -> None:
    wt_app = ctx.obj
    with wt_app.session() as session:
        tenant_id = require_bootstrap(session)
        profile = session.baseline._repo.get_department_profile(tenant_id, department_id)
    if profile is None:
        typer.echo(f"no profile for department {department_id}")
        raise typer.Exit(code=1)
    typer.echo(json.dumps(profile.model_dump(mode="json"), indent=2, default=str))


@rules_app.command("pending")
def rules_pending(ctx: typer.Context) -> None:
    wt_app = ctx.obj
    with wt_app.session() as session:
        tenant_id = require_bootstrap(session)
        pending = session.rules._repo.list_pending_rules(tenant_id, status="pending")
    if not pending:
        typer.echo("(no pending rules)")
        return
    for rule in pending:
        typer.echo(f"{rule.id}\t{rule.proposed_by}\t{rule.scope.model_dump()}")


@rules_app.command("approve")
def rules_approve(
    ctx: typer.Context,
    rule_id: Annotated[str, typer.Argument(help="Pending rule id")],
    allow_policy_suppression: Annotated[
        bool, typer.Option("--allow-policy-suppression")
    ] = False,
) -> None:
    wt_app = ctx.obj
    with wt_app.session() as session:
        tenant_id = require_bootstrap(session)
        stable = session.rules.approve_pending_rule(
            tenant_id,
            rule_id,
            approver_id="cli-operator",
            approver_role="security_operator",  # type: ignore[arg-type]
            allow_policy_suppression=allow_policy_suppression,
        )
    typer.echo(f"approved stable rule {stable.id}")


@rules_app.command("reject")
def rules_reject(
    ctx: typer.Context,
    rule_id: Annotated[str, typer.Argument(help="Pending rule id")],
    comment: Annotated[Optional[str], typer.Option("--comment")] = None,
) -> None:
    wt_app = ctx.obj
    with wt_app.session() as session:
        tenant_id = require_bootstrap(session)
        session.rules.reject_pending_rule(
            tenant_id,
            rule_id,
            approver_id="cli-operator",
            approver_role="security_operator",  # type: ignore[arg-type]
            comment=comment,
        )
    typer.echo(f"rejected pending rule {rule_id}")


def register_query_command(app: typer.Typer) -> None:
    @app.command("query")
    def query_command(
        ctx: typer.Context,
        text: Annotated[str, typer.Argument(help="Natural language query")],
    ) -> None:
        wt_app = ctx.obj
        with wt_app.session() as session:
            tenant_id = require_bootstrap(session)
            result = session.query.answer(tenant_id, text)
            session.audit.log(
                "cli.query",
                tenant_id=tenant_id,
                details={"query_id": result["query_id"]},
            )
        typer.echo(result["answer"])
        typer.echo(f"\n[auditable query_id={result['query_id']}]")
