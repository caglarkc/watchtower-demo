"""LangGraph decision graph state schema."""

from __future__ import annotations

import operator
from typing import Annotated, Any, TypedDict


class GraphState(TypedDict, total=False):
    """State passed between decision graph nodes."""

    run_id: str
    tenant_id: str
    candidate: dict[str, Any]
    mode: str
    identity: dict[str, Any]
    asset: dict[str, Any]
    taxonomy_entry: dict[str, Any]
    policy_context: dict[str, Any]
    baseline_context: dict[str, Any]
    feedback_context: dict[str, Any]
    change_context: dict[str, Any]
    assessment_input: dict[str, Any]
    assessment: dict[str, Any]
    route: dict[str, Any]
    silent_finding_id: str | None
    alert_case_id: str | None
    learning_event_id: str | None
    llm_explanation: dict[str, Any] | None
    pending_rule_id: str | None
    approval_status: str | None
    baseline_update_skipped: bool
    halted: bool
    error: str | None
    status: str
    audit_trail: Annotated[list[dict[str, Any]], operator.add]
