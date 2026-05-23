"""E2E graph runner helpers."""

from __future__ import annotations

from typing import Any

from watchtower.domain.normalized_event import CandidateEvent
from watchtower.graph.runner import GraphRunResult
from watchtower.services.app import AppContext


def run_graph_to_completion(
    app: AppContext,
    candidate: CandidateEvent,
    *,
    llm_gateway: Any | None = None,
    resume_payload: dict[str, Any] | None = None,
) -> GraphRunResult:
    with app.session() as session:
        if llm_gateway is not None:
            from tests.e2e.conftest import attach_mock_llm

            attach_mock_llm(session, llm_gateway)
        result = session.graph_runner.run(candidate)
        if result.interrupted:
            payload = resume_payload or {"decision": "none"}
            result = session.graph_runner.resume(result.thread_id, payload)
        return result
