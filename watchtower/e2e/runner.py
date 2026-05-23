"""E2E graph runner helpers."""

from __future__ import annotations

from typing import Any

from watchtower.domain.normalized_event import CandidateEvent
from watchtower.graph.runner import GraphRunResult, build_graph_runner
from watchtower.services.app import AppContext


def _attach_llm_gateway(session, llm_gateway: Any, *, checkpoint_store: Any) -> None:
    session.graph_runner = build_graph_runner(
        mode_controller=session.mode_controller,
        decision=session.decision,
        baseline=session.baseline,
        feedback=session.feedback,
        rules=session.rules,
        graph_repo=session.graph,
        conn=session.conn,
        checkpoint_store=checkpoint_store,
        llm_gateway=llm_gateway,
        alerts=session.alerts,
    )
    session.llm = llm_gateway


def run_graph_to_completion(
    app: AppContext,
    candidate: CandidateEvent,
    *,
    llm_gateway: Any | None = None,
    resume_payload: dict[str, Any] | None = None,
) -> GraphRunResult:
    with app.session() as session:
        if llm_gateway is not None:
            _attach_llm_gateway(session, llm_gateway)
        result = session.graph_runner.run(candidate)
        if result.interrupted:
            payload = resume_payload or {"decision": "none"}
            result = session.graph_runner.resume(result.thread_id, payload)
        return result
