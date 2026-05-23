"""Graph checkpoint and approval resume CLI."""

from __future__ import annotations

import json
from typing import Annotated, Optional

import typer

from watchtower.cli.deps import require_bootstrap
from watchtower.graph.checkpointing import prune_completed_checkpoints
from watchtower.graph.resume import GraphResumeService
from watchtower.services.bootstrap import BootstrapRequiredError

graph_app = typer.Typer(help="Graph checkpoint and resume commands")


def register_graph_commands(app: typer.Typer) -> None:
    app.add_typer(graph_app, name="graph")


@graph_app.command("interrupted")
def graph_interrupted(
    ctx: typer.Context,
    json_output: Annotated[bool, typer.Option("--json", help="JSON output")] = False,
) -> None:
    """List graph runs waiting on human approval (checkpointed interrupt)."""
    wt_app = ctx.obj
    with wt_app.session() as session:
        try:
            tenant_id = require_bootstrap(session)
            svc = GraphResumeService(session, wt_app.checkpoint_store)
            rows = svc.list_interrupted(tenant_id)
        except BootstrapRequiredError as exc:
            typer.echo(str(exc), err=True)
            raise typer.Exit(code=1) from exc

    if json_output:
        typer.echo(
            json.dumps(
                [
                    {
                        "run_id": r.run_id,
                        "thread_id": r.thread_id,
                        "checkpoint_id": r.last_checkpoint_id,
                        "candidate_id": r.candidate_id,
                        "mode": r.mode,
                    }
                    for r in rows
                ],
                indent=2,
            )
        )
        return
    if not rows:
        typer.echo("(no interrupted graph runs)")
        return
    for row in rows:
        typer.echo(
            f"{row.run_id}\tthread={row.thread_id}\t"
            f"checkpoint={row.last_checkpoint_id or '-'}"
        )


@graph_app.command("resume")
def graph_resume(
    ctx: typer.Context,
    thread_id: Annotated[str, typer.Option("--thread-id", help="Graph thread id")],
    decision: Annotated[
        str, typer.Option("--decision", help="approved | rejected | none")
    ] = "approved",
    approver_id: Annotated[str, typer.Option("--approver-id")] = "cli-operator",
    allow_policy_suppression: Annotated[
        bool, typer.Option("--allow-policy-suppression")
    ] = False,
) -> None:
    """Resume an interrupted graph from durable checkpoint."""
    wt_app = ctx.obj
    payload = {
        "decision": decision,
        "approver_id": approver_id,
        "allow_policy_suppression": allow_policy_suppression,
    }
    with wt_app.session() as session:
        try:
            tenant_id = require_bootstrap(session)
            svc = GraphResumeService(session, wt_app.checkpoint_store)
            result = svc.resume(tenant_id, thread_id, payload)
            session.audit.log(
                "cli.graph.resume",
                tenant_id=tenant_id,
                details={
                    "thread_id": thread_id,
                    "run_id": result.run_id,
                    "decision": decision,
                    "interrupted": result.interrupted,
                },
            )
            session.conn.commit()
        except (BootstrapRequiredError, ValueError) as exc:
            typer.echo(str(exc), err=True)
            raise typer.Exit(code=1) from exc

    typer.echo(
        f"run_id={result.run_id} status={result.state.get('status')} "
        f"approval={result.state.get('approval_status')} "
        f"interrupted={result.interrupted}"
    )
    if result.interrupted:
        raise typer.Exit(code=2)


@graph_app.command("checkpoint-prune")
def graph_checkpoint_prune(
    ctx: typer.Context,
    retention_days: Annotated[
        Optional[int],
        typer.Option("--retention-days", help="Override settings retention"),
    ] = None,
    dry_run: Annotated[bool, typer.Option("--dry-run")] = False,
) -> None:
    """Prune durable checkpoint blobs for old completed graph runs."""
    wt_app = ctx.obj
    days = (
        retention_days
        if retention_days is not None
        else wt_app.settings.graph_checkpoint_retention_days
    )
    if days <= 0:
        typer.echo("retention disabled (graph_checkpoint_retention_days=0)")
        return

    with wt_app.session() as session:
        if dry_run:
            cutoff_rows = session.conn.execute(
                """
                SELECT thread_id FROM graph_runs
                WHERE status = 'completed' AND thread_id IS NOT NULL
                  AND finished_at IS NOT NULL
                """
            ).fetchall()
            typer.echo(f"would prune up to {len(cutoff_rows)} checkpoint thread(s)")
            return
        removed = prune_completed_checkpoints(
            session.conn,
            wt_app.checkpoint_store,
            retention_days=days,
        )
        session.audit.log(
            "cli.graph.checkpoint_prune",
            tenant_id=require_bootstrap(session),
            details={"retention_days": days, "threads_pruned": removed},
        )
        session.conn.commit()
    typer.echo(f"pruned checkpoint threads: {removed}")
