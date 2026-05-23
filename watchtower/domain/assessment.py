"""Candidate assessment and explainable score breakdown."""

from __future__ import annotations

from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, Field

SeverityLevel = Literal["LOG", "WARNING", "ALERT", "CRITICAL"]

SEVERITY_ORDER: dict[SeverityLevel, int] = {
    "LOG": 0,
    "WARNING": 1,
    "ALERT": 2,
    "CRITICAL": 3,
}


class ScoreComponent(BaseModel):
    """Single explainable contribution to the final severity."""

    source: str
    points: int
    reason: str
    metadata: dict[str, Any] = Field(default_factory=dict)


class ScoreBreakdown(BaseModel):
    """Mandatory explainable breakdown for every assessment."""

    components: list[ScoreComponent] = Field(min_length=1)
    raw_total: int = 0
    severity_floor: SeverityLevel = "LOG"
    final_severity: SeverityLevel = "LOG"
    suppressed: bool = False
    downranked: bool = False
    policy_suppression_blocked: bool = False

    def max_severity(self) -> SeverityLevel:
        return self.final_severity


class AssessmentInput(BaseModel):
    """Decision input derived from a candidate event."""

    tenant_id: str
    feature_id: str
    user_id: str | None = None
    role_id: str | None = None
    department_id: str | None = None
    seniority: str = "worker"
    resource: str | None = None
    action: str | None = None
    volume: float | None = None
    metric_name: str = "event_volume"
    occurred_at: datetime
    correlation_group: str | None = None
    related_signals: list[str] = Field(default_factory=list)
    attributes: dict[str, Any] = Field(default_factory=dict)


class CandidateAssessment(BaseModel):
    """Deterministic decision output (no LLM)."""

    tenant_id: str
    feature_id: str
    severity: SeverityLevel
    should_alert: bool
    breakdown: ScoreBreakdown
    detection_class: str
    policy_violated: bool = False
    baseline_anomaly: bool = False
    correlation_boost: bool = False
    feedback_applied: bool = False
    details: dict[str, Any] = Field(default_factory=dict)
