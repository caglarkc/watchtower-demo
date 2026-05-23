"""Graph runner with checkpointing and interrupt resume."""

from __future__ import annotations

import sqlite3
import uuid
from dataclasses import dataclass
from typing import Any

from langgraph.checkpoint.base import BaseCheckpointSaver
from langgraph.checkpoint.memory import MemorySaver
from langgraph.types import Command

from watchtower.domain.normalized_event import CandidateEvent
from watchtower.graph.builder import build_decision_graph
from watchtower.graph.deps import GraphDeps
from watchtower.graph.state import GraphState
from watchtower.storage.repositories.graph import GraphRepository


@dataclass
class GraphRunResult:
    run_id: str
    state: dict[str, Any]
    interrupted: bool
    thread_id: str


class GraphRunner:
    """Execute decision graph with SQLite checkpoint + audit."""

    def __init__(
        self,
        deps: GraphDeps,
        conn: sqlite3.Connection,
        *,
        checkpointer: BaseCheckpointSaver | None = None,
    ) -> None:
        self._deps = deps
        self._conn = conn
        # MemorySaver avoids nested-transaction conflicts with app session commits.
        self._checkpointer = checkpointer or MemorySaver()
        graph = build_decision_graph(deps)
        self._compiled = graph.compile(checkpointer=self._checkpointer)

    def run(
        self,
        candidate: CandidateEvent,
        *,
        run_id: str | None = None,
        thread_id: str | None = None,
    ) -> GraphRunResult:
        run_id = run_id or str(uuid.uuid4())
        thread_id = thread_id or run_id
        self._deps.graph_repo.create_run(
            run_id=run_id,
            tenant_id=candidate.tenant_id,
            candidate_id=candidate.id,
            mode=self._deps.mode_controller.get_mode(candidate.tenant_id),
        )
        initial: GraphState = {
            "run_id": run_id,
            "tenant_id": candidate.tenant_id,
            "candidate": candidate.model_dump(mode="json"),
            "audit_trail": [],
            "status": "running",
        }
        config = {"configurable": {"thread_id": thread_id}}
        state = self._compiled.invoke(initial, config)
        interrupted = bool(state.get("__interrupt__"))
        return GraphRunResult(
            run_id=run_id,
            state=dict(state),
            interrupted=interrupted,
            thread_id=thread_id,
        )

    def resume(
        self,
        thread_id: str,
        payload: dict[str, Any],
    ) -> GraphRunResult:
        config = {"configurable": {"thread_id": thread_id}}
        state = self._compiled.invoke(Command(resume=payload), config)
        interrupted = bool(state.get("__interrupt__"))
        run_id = state.get("run_id", thread_id)
        return GraphRunResult(
            run_id=run_id,
            state=dict(state),
            interrupted=interrupted,
            thread_id=thread_id,
        )

    def get_state(self, thread_id: str) -> dict[str, Any] | None:
        config = {"configurable": {"thread_id": thread_id}}
        snap = self._compiled.get_state(config)
        if snap is None or snap.values is None:
            return None
        return dict(snap.values)


def build_graph_runner(
    *,
    mode_controller: Any,
    decision: Any,
    baseline: Any,
    feedback: Any,
    rules: Any,
    graph_repo: GraphRepository,
    conn: sqlite3.Connection,
    llm_gateway: Any | None = None,
) -> GraphRunner:
    deps = GraphDeps(
        mode_controller=mode_controller,
        decision=decision,
        baseline=baseline,
        feedback=feedback,
        rules=rules,
        graph_repo=graph_repo,
        llm_gateway=llm_gateway,
    )
    return GraphRunner(deps, conn)
