"""Decision graph node implementations (orchestration only)."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

from langgraph.types import interrupt

from watchtower.domain.assessment import AssessmentInput
from watchtower.domain.normalized_event import CandidateEvent
from watchtower.domain.profiles import BehaviorObservation
from watchtower.domain.rules import DecisionContext, RuleScope
from watchtower.graph.deps import GraphDeps
from watchtower.graph.nodes.schemas import (
    AssessmentOutput,
    AssetOutput,
    BaselineContextOutput,
    ChangeContextOutput,
    FeedbackContextOutput,
    IdentityOutput,
    ModeOutput,
    PolicyContextOutput,
    RouteOutput,
    TaxonomyOutput,
)
from watchtower.graph.state import GraphState
from watchtower.graph.validation import safe_node
from watchtower.policy.engine import PolicyEngine
from watchtower.rules.scope import scope_matches
from watchtower.taxonomy.loader import load_feature_taxonomy as get_feature_taxonomy


def _candidate(state: GraphState) -> CandidateEvent:
    return CandidateEvent.model_validate(state["candidate"])


def _audit_repo(deps: GraphDeps, state: GraphState, node: str, output: dict[str, Any]) -> None:
    run_id = state.get("run_id")
    if run_id:
        deps.graph_repo.append_audit(run_id, node, output)


@safe_node("load_mode", ModeOutput)
def load_mode(state: GraphState, deps: GraphDeps) -> dict[str, Any]:
    tenant_id = state["tenant_id"]
    mode = deps.mode_controller.get_mode(tenant_id)
    out = {"mode": mode}
    _audit_repo(deps, state, "load_mode", out)
    return {"mode": mode}


@safe_node("resolve_identity", IdentityOutput)
def resolve_identity(state: GraphState, deps: GraphDeps) -> dict[str, Any]:
    cand = _candidate(state)
    attrs = cand.attributes
    identity = IdentityOutput(
        user_id=attrs.get("user_id") or cand.actor,
        department_id=attrs.get("department_id"),
        role_id=attrs.get("role_id"),
        seniority=attrs.get("seniority", "worker"),
    )
    _audit_repo(deps, state, "resolve_identity", identity.model_dump())
    return {"identity": identity.model_dump()}


@safe_node("resolve_asset", AssetOutput)
def resolve_asset(state: GraphState, deps: GraphDeps) -> dict[str, Any]:
    cand = _candidate(state)
    asset = AssetOutput(
        asset_id=cand.attributes.get("asset_id") or cand.resource,
        resource=cand.resource,
        criticality=cand.attributes.get("asset_criticality", "medium"),
    )
    _audit_repo(deps, state, "resolve_asset", asset.model_dump())
    return {"asset": asset.model_dump()}


@safe_node("load_feature_taxonomy", TaxonomyOutput)
def load_feature_taxonomy(state: GraphState, deps: GraphDeps) -> dict[str, Any]:
    cand = _candidate(state)
    entry = get_feature_taxonomy().by_id()[cand.feature_hint]
    tax = TaxonomyOutput(
        feature_id=entry.feature_id,
        primary_detection_class=entry.primary_detection_class,
        requires_baseline=entry.requires_baseline,
    )
    _audit_repo(deps, state, "load_feature_taxonomy", tax.model_dump())
    return {"taxonomy_entry": tax.model_dump()}


@safe_node("load_policy_context", PolicyContextOutput)
def load_policy_context(state: GraphState, deps: GraphDeps) -> dict[str, Any]:
    cand = _candidate(state)
    identity = state.get("identity", {})
    entry = get_feature_taxonomy().by_id()[cand.feature_hint]
    inp = AssessmentInput(
        tenant_id=state["tenant_id"],
        feature_id=cand.feature_hint,
        user_id=identity.get("user_id"),
        role_id=identity.get("role_id"),
        department_id=identity.get("department_id"),
        seniority=identity.get("seniority", "worker"),
        resource=cand.resource,
        action=cand.action,
        volume=float(cand.attributes.get("volume", 0)),
        metric_name=cand.attributes.get("metric_name", "event_volume"),
        occurred_at=cand.occurred_at,
    )
    policy = PolicyEngine().evaluate(inp, entry)
    ctx = PolicyContextOutput(
        violated=policy.violated,
        severity_floor=policy.severity_floor,
    )
    _audit_repo(deps, state, "load_policy_context", ctx.model_dump())
    return {"policy_context": ctx.model_dump()}


@safe_node("load_baseline_context", BaselineContextOutput)
def load_baseline_context(state: GraphState, deps: GraphDeps) -> dict[str, Any]:
    cand = _candidate(state)
    tax = state.get("taxonomy_entry", {})
    identity = state.get("identity", {})
    if not tax.get("requires_baseline"):
        ctx = BaselineContextOutput(is_normal=None, source=None)
        return {"baseline_context": ctx.model_dump(), "baseline_update_skipped": True}

    eval_result = deps.baseline.evaluate(
        state["tenant_id"],
        cand.attributes.get("metric_name", "event_volume"),
        float(cand.attributes.get("volume", 0)),
        user_id=identity.get("user_id"),
        department_id=identity.get("department_id"),
        role_id=identity.get("role_id"),
        seniority=identity.get("seniority", "worker"),
    )
    ctx = BaselineContextOutput(
        is_normal=eval_result.is_normal,
        source=eval_result.source,
    )
    _audit_repo(deps, state, "load_baseline_context", ctx.model_dump())
    return {"baseline_context": ctx.model_dump()}


@safe_node("load_feedback_context", FeedbackContextOutput)
def load_feedback_context(state: GraphState, deps: GraphDeps) -> dict[str, Any]:
    cand = _candidate(state)
    identity = state.get("identity", {})
    decision_ctx = DecisionContext(
        tenant_id=state["tenant_id"],
        feature_id=cand.feature_hint,
        user_id=identity.get("user_id"),
        role_id=identity.get("role_id"),
        department_id=identity.get("department_id"),
        resource=cand.resource,
        action=cand.action,
        volume=float(cand.attributes.get("volume", 0)) if cand.attributes.get("volume") else None,
        occurred_at=cand.occurred_at,
        detection_class=state.get("taxonomy_entry", {}).get("primary_detection_class"),
    )
    result = deps.rules.apply_feedback_rules(decision_ctx)
    pending_id = result.pending_rule_id
    if not pending_id:
        scope = RuleScope(
            feature_id=cand.feature_hint,
            user_id=identity.get("user_id"),
            resource=cand.resource,
            action=cand.action,
        )
        for pending in deps.rules._repo.list_pending_rules(state["tenant_id"], status="pending"):
            if scope_matches(pending.scope, decision_ctx):
                pending_id = pending.id
                break
    fb = FeedbackContextOutput(
        matched=result.matched,
        pending_rule_id=pending_id,
        suppress_alert=result.suppress_alert,
    )
    _audit_repo(deps, state, "load_feedback_context", fb.model_dump())
    return {
        "feedback_context": fb.model_dump(),
        "pending_rule_id": pending_id,
    }


@safe_node("load_change_context", ChangeContextOutput)
def load_change_context(state: GraphState, deps: GraphDeps) -> dict[str, Any]:
    cand = _candidate(state)
    ctx = ChangeContextOutput(
        ticket_id=cand.attributes.get("change_ticket_id"),
        maintenance_window=bool(cand.attributes.get("maintenance_window")),
    )
    _audit_repo(deps, state, "load_change_context", ctx.model_dump())
    return {"change_context": ctx.model_dump()}


@safe_node("score_candidate")
def score_candidate(state: GraphState, deps: GraphDeps) -> dict[str, Any]:
    cand = _candidate(state)
    identity = state.get("identity", {})
    inp = AssessmentInput(
        tenant_id=state["tenant_id"],
        feature_id=cand.feature_hint,
        user_id=identity.get("user_id"),
        role_id=identity.get("role_id"),
        department_id=identity.get("department_id"),
        seniority=identity.get("seniority", "worker"),
        resource=cand.resource,
        action=cand.action,
        volume=float(cand.attributes.get("volume", 0)),
        metric_name=cand.attributes.get("metric_name", "event_volume"),
        occurred_at=cand.occurred_at,
        related_signals=cand.attributes.get("related_signals", []),
    )
    _audit_repo(deps, state, "score_candidate", inp.model_dump(mode="json"))
    return {"assessment_input": inp.model_dump(mode="json")}


@safe_node("decide_severity", AssessmentOutput)
def decide_severity(state: GraphState, deps: GraphDeps) -> dict[str, Any]:
    inp = AssessmentInput.model_validate(state["assessment_input"])
    assessment = deps.decision.assess(inp)
    out = AssessmentOutput(
        severity=assessment.severity,
        should_alert=assessment.should_alert,
        detection_class=assessment.detection_class,
    )
    _audit_repo(
        deps,
        state,
        "decide_severity",
        {**out.model_dump(), "breakdown": assessment.breakdown.model_dump()},
    )
    return {"assessment": assessment.model_dump(mode="json")}


@safe_node("route_by_mode", RouteOutput)
def route_by_mode(state: GraphState, deps: GraphDeps) -> dict[str, Any]:
    mode = state.get("mode", "learn")
    assessment = state.get("assessment", {})
    should_alert = bool(assessment.get("should_alert"))
    change = state.get("change_context", {})
    if change.get("maintenance_window"):
        should_alert = False

    if mode == "learn":
        route = RouteOutput(
            mode=mode,
            should_persist_silent=True,
            should_create_alert=False,
            should_enqueue_learning=True,
            baseline_update_allowed=True,
        )
    elif mode == "run":
        route = RouteOutput(
            mode=mode,
            should_persist_silent=False,
            should_create_alert=should_alert,
            should_enqueue_learning=False,
            baseline_update_allowed=False,
        )
    else:
        route = RouteOutput(
            mode=mode,
            should_persist_silent=True,
            should_create_alert=should_alert,
            should_enqueue_learning=True,
            baseline_update_allowed=True,
        )
    _audit_repo(deps, state, "route_by_mode", route.model_dump())
    return {"route": route.model_dump()}


def persist_silent_finding(state: GraphState, deps: GraphDeps) -> dict[str, Any]:
    if state.get("halted"):
        return {}
    route = state.get("route", {})
    if not route.get("should_persist_silent"):
        return {}
    cand = _candidate(state)
    assessment = state.get("assessment", {})
    fid = deps.graph_repo.insert_silent_finding(
        tenant_id=state["tenant_id"],
        run_id=state["run_id"],
        candidate_id=cand.id,
        feature_id=cand.feature_hint,
        severity=assessment.get("severity", "LOG"),
        payload={"assessment": assessment},
    )
    _audit_repo(deps, state, "persist_silent_finding", {"silent_finding_id": fid})
    return {"silent_finding_id": fid}


def create_alert_case(state: GraphState, deps: GraphDeps) -> dict[str, Any]:
    if state.get("halted"):
        return {}
    route = state.get("route", {})
    if not route.get("should_create_alert"):
        return {}
    cand = _candidate(state)
    assessment = state.get("assessment", {})
    aid = deps.graph_repo.insert_alert_case(
        tenant_id=state["tenant_id"],
        run_id=state["run_id"],
        candidate_id=cand.id,
        feature_id=cand.feature_hint,
        severity=assessment.get("severity", "ALERT"),
        payload={"assessment": assessment},
    )
    _audit_repo(deps, state, "create_alert_case", {"alert_case_id": aid})
    return {"alert_case_id": aid}


def enqueue_controlled_learning(state: GraphState, deps: GraphDeps) -> dict[str, Any]:
    if state.get("halted"):
        return {}
    route = state.get("route", {})
    if not route.get("should_enqueue_learning"):
        return {"baseline_update_skipped": True}
    cand = _candidate(state)
    identity = state.get("identity", {})
    lid = deps.graph_repo.insert_learning_event(
        tenant_id=state["tenant_id"],
        run_id=state["run_id"],
        candidate_id=cand.id,
        event_type="controlled_baseline_sample",
        payload={"mode": route.get("mode"), "feature_id": cand.feature_hint},
    )
    if route.get("baseline_update_allowed"):
        deps.baseline.record_observation(
            BehaviorObservation(
                tenant_id=state["tenant_id"],
                metric_name=cand.attributes.get("metric_name", "event_volume"),
                value=float(cand.attributes.get("volume", 0)),
                observed_at=cand.occurred_at,
                user_id=identity.get("user_id"),
                department_id=identity.get("department_id"),
                role_id=identity.get("role_id"),
                seniority=identity.get("seniority", "worker"),
            )
        )
    _audit_repo(deps, state, "enqueue_controlled_learning", {"learning_event_id": lid})
    return {"learning_event_id": lid, "baseline_update_skipped": False}


def maybe_generate_llm_explanation(state: GraphState, deps: GraphDeps) -> dict[str, Any]:
    if state.get("halted"):
        return {}
    assessment = state.get("assessment", {})
    if deps.llm_gateway is None:
        out = {"llm_explanation": {"skipped": True, "reason": "LLM gateway not configured"}}
        _audit_repo(deps, state, "maybe_generate_llm_explanation", out)
        return out
    prompt = (
        f"Explain alert for feature {state.get('taxonomy_entry', {}).get('feature_id')} "
        f"with severity {assessment.get('severity')} for operator review. "
        "Do not change severity or make a final decision."
    )
    result = deps.llm_gateway.invoke(
        "alert_explanation",
        prompt,
        tenant_id=state["tenant_id"],
        context={"assessment": assessment, "run_id": state.get("run_id")},
    )
    if result.success and result.data is not None:
        out = {
            "llm_explanation": {
                "skipped": False,
                "provider": result.provider,
                "data": result.data.model_dump(),
            }
        }
    else:
        out = {
            "llm_explanation": {
                "skipped": False,
                "fail_open": True,
                "note": result.note,
            }
        }
    _audit_repo(deps, state, "maybe_generate_llm_explanation", out)
    return out


def maybe_generate_pending_rule(state: GraphState, deps: GraphDeps) -> dict[str, Any]:
    if state.get("halted"):
        return {}
    pending_id = state.get("pending_rule_id")
    if pending_id:
        _audit_repo(deps, state, "maybe_generate_pending_rule", {"pending_rule_id": pending_id})
        return {"pending_rule_id": pending_id}
    return {}


def await_rule_approval(state: GraphState, deps: GraphDeps) -> dict[str, Any]:
    if state.get("halted"):
        return {}
    pending_id = state.get("pending_rule_id")
    if not pending_id:
        return {"approval_status": "none"}
    payload = interrupt(
        {
            "type": "rule_approval",
            "pending_rule_id": pending_id,
            "tenant_id": state["tenant_id"],
        }
    )
    decision = payload.get("decision", "approved") if isinstance(payload, dict) else "approved"
    if decision == "approved":
        deps.rules.approve_pending_rule(
            state["tenant_id"],
            pending_id,
            approver_id=payload.get("approver_id", "sec-1") if isinstance(payload, dict) else "sec-1",
            approver_role="security_operator",
            allow_policy_suppression=bool(
                payload.get("allow_policy_suppression") if isinstance(payload, dict) else False
            ),
        )
    elif decision == "rejected":
        deps.rules.reject_pending_rule(
            state["tenant_id"],
            pending_id,
            approver_id=payload.get("approver_id", "sec-1") if isinstance(payload, dict) else "sec-1",
            approver_role="security_operator",
        )
    _audit_repo(deps, state, "await_rule_approval", {"approval_status": decision})
    return {"approval_status": decision}


def finalize_decision(state: GraphState, deps: GraphDeps) -> dict[str, Any]:
    status = "failed" if state.get("halted") else "completed"
    deps.graph_repo.finish_run(
        state["run_id"],
        status=status,
        route=state.get("route"),
        assessment=state.get("assessment"),
        error=state.get("error"),
    )
    out = {
        "status": status,
        "silent_finding_id": state.get("silent_finding_id"),
        "alert_case_id": state.get("alert_case_id"),
        "learning_event_id": state.get("learning_event_id"),
    }
    _audit_repo(deps, state, "finalize_decision", out)
    return out
