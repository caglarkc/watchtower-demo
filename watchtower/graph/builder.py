"""Build the LangGraph decision graph."""

from __future__ import annotations

from typing import Any, Literal

from langgraph.graph import END, START, StateGraph

from watchtower.graph.deps import GraphDeps
from watchtower.graph.nodes import pipeline as nodes
from watchtower.graph.state import GraphState


def _bind(fn: Any, deps: GraphDeps) -> Any:
    return lambda state: fn(state, deps)


def _route_after_halt(state: GraphState) -> Literal["halt", "continue"]:
    if state.get("halted"):
        return "halt"
    return "continue"


def _route_after_mode_route(state: GraphState) -> Literal["post_route", "finalize"]:
    if state.get("halted"):
        return "finalize"
    return "post_route"


def build_decision_graph(deps: GraphDeps) -> StateGraph:
    """Construct the decision StateGraph (uncompiled)."""
    graph: StateGraph = StateGraph(GraphState)

    graph.add_node("load_mode", _bind(nodes.load_mode, deps))
    graph.add_node("resolve_identity", _bind(nodes.resolve_identity, deps))
    graph.add_node("resolve_asset", _bind(nodes.resolve_asset, deps))
    graph.add_node("load_feature_taxonomy", _bind(nodes.load_feature_taxonomy, deps))
    graph.add_node("load_policy_context", _bind(nodes.load_policy_context, deps))
    graph.add_node("load_baseline_context", _bind(nodes.load_baseline_context, deps))
    graph.add_node("load_feedback_context", _bind(nodes.load_feedback_context, deps))
    graph.add_node("load_change_context", _bind(nodes.load_change_context, deps))
    graph.add_node("score_candidate", _bind(nodes.score_candidate, deps))
    graph.add_node("decide_severity", _bind(nodes.decide_severity, deps))
    graph.add_node("route_by_mode", _bind(nodes.route_by_mode, deps))
    graph.add_node("persist_silent_finding", _bind(nodes.persist_silent_finding, deps))
    graph.add_node("create_alert_case", _bind(nodes.create_alert_case, deps))
    graph.add_node(
        "enqueue_controlled_learning", _bind(nodes.enqueue_controlled_learning, deps)
    )
    graph.add_node(
        "maybe_generate_llm_explanation",
        _bind(nodes.maybe_generate_llm_explanation, deps),
    )
    graph.add_node(
        "maybe_generate_pending_rule", _bind(nodes.maybe_generate_pending_rule, deps)
    )
    graph.add_node("await_rule_approval", _bind(nodes.await_rule_approval, deps))
    graph.add_node("finalize_decision", _bind(nodes.finalize_decision, deps))

    graph.add_edge(START, "load_mode")
    graph.add_edge("load_mode", "resolve_identity")
    graph.add_conditional_edges(
        "resolve_identity",
        _route_after_halt,
        {"halt": "finalize_decision", "continue": "resolve_asset"},
    )
    graph.add_edge("resolve_asset", "load_feature_taxonomy")
    graph.add_edge("load_feature_taxonomy", "load_policy_context")
    graph.add_edge("load_policy_context", "load_baseline_context")
    graph.add_edge("load_baseline_context", "load_feedback_context")
    graph.add_edge("load_feedback_context", "load_change_context")
    graph.add_edge("load_change_context", "score_candidate")
    graph.add_edge("score_candidate", "decide_severity")
    graph.add_edge("decide_severity", "route_by_mode")
    graph.add_conditional_edges(
        "route_by_mode",
        _route_after_mode_route,
        {"finalize": "finalize_decision", "post_route": "persist_silent_finding"},
    )
    graph.add_edge("persist_silent_finding", "create_alert_case")
    graph.add_edge("create_alert_case", "enqueue_controlled_learning")
    graph.add_edge("enqueue_controlled_learning", "maybe_generate_llm_explanation")
    graph.add_edge("maybe_generate_llm_explanation", "maybe_generate_pending_rule")
    graph.add_edge("maybe_generate_pending_rule", "await_rule_approval")
    graph.add_edge("await_rule_approval", "finalize_decision")
    graph.add_edge("finalize_decision", END)

    return graph
