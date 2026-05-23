"""Graph runner with durable SQLite checkpointing and interrupt resume."""

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
from watchtower.graph.checkpointing import GraphCheckpointStore
from watchtower.graph.deps import GraphDeps
from watchtower.graph.state import GraphState
from watchtower.storage.repositories.graph import GraphRepository


@dataclass
class GraphRunResult:
    run_id: str
    state: dict[str, Any]
    interrupted: bool
    thread_id: str
    checkpoint_id: str | None = None


class GraphRunner:
    """Execute decision graph with durable checkpoint + audit."""

    def __init__(
        self,
        deps: GraphDeps,
        conn: sqlite3.Connection,
        *,
        checkpointer: BaseCheckpointSaver,
        checkpoint_store: GraphCheckpointStore | None = None,
    ) -> None:
        self._deps = deps
        self._conn = conn
        self._checkpointer = checkpointer
        self._checkpoint_store = checkpoint_store
        graph = build_decision_graph(deps)
        self._compiled = graph.compile(checkpointer=self._checkpointer)

    @property
    def uses_memory_checkpointer(self) -> bool:
        return isinstance(self._checkpointer, MemorySaver)

    def checkpoint_exists(self, thread_id: str) -> bool:
        if self._checkpoint_store is not None:
            return self._checkpoint_store.thread_has_checkpoint(thread_id)
        config = {"configurable": {"thread_id": thread_id}}
        if hasattr(self._checkpointer, "get_tuple"):
            return self._checkpointer.get_tuple(config) is not None  # type: ignore[union-attr]
        return False

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
            thread_id=thread_id,
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
        checkpoint_id = self._checkpoint_id_from_config(config)
        self._persist_checkpoint_meta(run_id, thread_id, checkpoint_id, interrupted)
        return GraphRunResult(
            run_id=run_id,
            state=dict(state),
            interrupted=interrupted,
            thread_id=thread_id,
            checkpoint_id=checkpoint_id,
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
        checkpoint_id = self._checkpoint_id_from_config(config)
        self._persist_checkpoint_meta(run_id, thread_id, checkpoint_id, interrupted)
        return GraphRunResult(
            run_id=run_id,
            state=dict(state),
            interrupted=interrupted,
            thread_id=thread_id,
            checkpoint_id=checkpoint_id,
        )

    def get_state(self, thread_id: str) -> dict[str, Any] | None:
        config = {"configurable": {"thread_id": thread_id}}
        snap = self._compiled.get_state(config)
        if snap is None or snap.values is None:
            return None
        values = dict(snap.values)
        if snap.config:
            cfg = snap.config.get("configurable", {})
            if cfg.get("checkpoint_id"):
                values["last_checkpoint_id"] = cfg["checkpoint_id"]
        return values

    def _checkpoint_id_from_config(self, config: dict[str, Any]) -> str | None:
        snap = self._compiled.get_state(config)
        if snap is None or not snap.config:
            return None
        return snap.config.get("configurable", {}).get("checkpoint_id")

    def _persist_checkpoint_meta(
        self,
        run_id: str,
        thread_id: str,
        checkpoint_id: str | None,
        interrupted: bool,
    ) -> None:
        self._deps.graph_repo.set_checkpoint_meta(
            run_id,
            thread_id=thread_id,
            checkpoint_id=checkpoint_id,
            interrupted=interrupted,
        )
        self._deps.graph_repo.append_audit(
            run_id,
            "checkpoint_meta",
            {
                "thread_id": thread_id,
                "checkpoint_id": checkpoint_id,
                "interrupted": interrupted,
                "checkpointer": (
                    "memory" if self.uses_memory_checkpointer else "sqlite"
                ),
            },
        )


def build_graph_runner(
    *,
    mode_controller: Any,
    decision: Any,
    baseline: Any,
    feedback: Any,
    rules: Any,
    graph_repo: GraphRepository,
    conn: sqlite3.Connection,
    checkpoint_store: GraphCheckpointStore,
    llm_gateway: Any | None = None,
    alerts: Any | None = None,
) -> GraphRunner:
    deps = GraphDeps(
        mode_controller=mode_controller,
        decision=decision,
        baseline=baseline,
        feedback=feedback,
        rules=rules,
        graph_repo=graph_repo,
        llm_gateway=llm_gateway,
        alerts=alerts,
    )
    checkpointer = checkpoint_store.get_checkpointer()
    return GraphRunner(
        deps,
        conn,
        checkpointer=checkpointer,
        checkpoint_store=checkpoint_store,
    )
