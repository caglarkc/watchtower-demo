"""Resume interrupted graph runs (human approval) after process restart."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from watchtower.graph.checkpointing import GraphCheckpointStore
from watchtower.graph.runner import GraphRunResult, GraphRunner
from watchtower.services.app import SessionContext


@dataclass
class InterruptedRunInfo:
    run_id: str
    thread_id: str
    candidate_id: str | None
    last_checkpoint_id: str | None
    mode: str
    started_at: str | None


class GraphResumeService:
    """List and resume checkpointed graph threads."""

    def __init__(
        self,
        session: SessionContext,
        checkpoint_store: GraphCheckpointStore,
    ) -> None:
        self._session = session
        self._checkpoint_store = checkpoint_store

    def list_interrupted(self, tenant_id: str) -> list[InterruptedRunInfo]:
        rows = self._session.graph.list_interrupted_runs(tenant_id)
        return [
            InterruptedRunInfo(
                run_id=row["id"],
                thread_id=row["thread_id"] or row["id"],
                candidate_id=row.get("candidate_id"),
                last_checkpoint_id=row.get("last_checkpoint_id"),
                mode=row["mode"],
                started_at=row.get("started_at"),
            )
            for row in rows
            if row.get("thread_id")
        ]

    def resume(
        self,
        tenant_id: str,
        thread_id: str,
        payload: dict[str, Any],
        *,
        runner: GraphRunner | None = None,
    ) -> GraphRunResult:
        if not self._checkpoint_store.thread_has_checkpoint(thread_id):
            msg = f"no durable checkpoint for thread_id={thread_id}"
            raise ValueError(msg)
        row = self._session.graph.get_run_by_thread(thread_id)
        if row is not None and row["tenant_id"] != tenant_id:
            msg = "thread belongs to another tenant"
            raise ValueError(msg)
        graph_runner = runner or self._session.graph_runner
        result = graph_runner.resume(thread_id, payload)
        if not result.interrupted:
            self._session.graph.set_checkpoint_meta(
                result.run_id,
                thread_id=thread_id,
                checkpoint_id=result.state.get("last_checkpoint_id"),
                interrupted=False,
            )
        return result
