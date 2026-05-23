"""LLM task schemas — explanation and drafting only (no alert decisions)."""

from __future__ import annotations

from typing import Any, Literal, TypeVar

from pydantic import BaseModel, Field

# Allowed task names — explicitly excludes alert/severity decision tasks.
LLMTaskName = Literal[
    "alert_explanation",
    "rule_candidate_draft",
    "unknown_schema_mapping",
    "baseline_summary",
    "monthly_learning_report",
    "operator_query_answer",
]

FORBIDDEN_TASK_NAMES: frozenset[str] = frozenset(
    {
        "alert_decision",
        "severity_decision",
        "final_decision",
        "decide_alert",
        "decision",
    }
)


class AlertExplanation(BaseModel):
    """Human-readable alert explanation (does not change severity)."""

    summary: str = Field(min_length=1)
    risk_factors: list[str] = Field(default_factory=list)
    recommended_actions: list[str] = Field(default_factory=list)
    confidence_note: str | None = None


class RuleCandidateDraft(BaseModel):
    """Draft scoped rule for pending approval — not a stable rule."""

    scope_summary: str
    rationale: str
    suggested_effect: str = Field(description="downrank|suppress|severity_modifier")
    expires_in_days: int | None = None


class UnknownSchemaMapping(BaseModel):
    """Suggested mapping for unknown raw schema."""

    event_type: str
    feature_hint: str | None = None
    field_mappings: dict[str, str] = Field(default_factory=dict)
    notes: str | None = None


class BaselineSummary(BaseModel):
    """Narrative baseline profile summary."""

    user_id: str | None = None
    department_id: str | None = None
    highlights: list[str] = Field(default_factory=list)
    anomaly_notes: str | None = None


class MonthlyLearningReport(BaseModel):
    """Monthly learning mode report."""

    period: str
    findings_count: int = 0
    top_patterns: list[str] = Field(default_factory=list)
    recommendations: list[str] = Field(default_factory=list)


class OperatorQueryAnswer(BaseModel):
    """Natural language operator query response."""

    answer: str
    cited_features: list[str] = Field(default_factory=list)
    follow_up_questions: list[str] = Field(default_factory=list)


TSchema = TypeVar("TSchema", bound=BaseModel)

TASK_SCHEMA_REGISTRY: dict[LLMTaskName, type[BaseModel]] = {
    "alert_explanation": AlertExplanation,
    "rule_candidate_draft": RuleCandidateDraft,
    "unknown_schema_mapping": UnknownSchemaMapping,
    "baseline_summary": BaselineSummary,
    "monthly_learning_report": MonthlyLearningReport,
    "operator_query_answer": OperatorQueryAnswer,
}


def assert_task_allowed(task: str) -> LLMTaskName:
    if task in FORBIDDEN_TASK_NAMES:
        msg = f"Task '{task}' is forbidden: LLM cannot make final alert decisions"
        raise ValueError(msg)
    if task not in TASK_SCHEMA_REGISTRY:
        msg = f"Unknown LLM task: {task}"
        raise ValueError(msg)
    return task  # type: ignore[return-value]


def task_json_schema(task: LLMTaskName) -> dict[str, Any]:
    return TASK_SCHEMA_REGISTRY[task].model_json_schema()
