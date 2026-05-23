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
    resume_payload: dict[str, Any] | None = None,
) -> GraphRunResult:
    with app.session() as session:
        result = session.graph_runner.run(candidate)
        if result.interrupted:
            payload = resume_payload or {"decision": "none"}
            result = session.graph_runner.resume(result.thread_id, payload)
        return result
