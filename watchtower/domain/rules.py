"""Feedback events, pending rules, stable feedback rules, and approvals."""

from __future__ import annotations

from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, Field

FeedbackKind = Literal[
    "expected_behavior",
    "false_positive",
    "true_positive",
    "temporary_exception",
    "project_context",
    "role_change",
    "needs_investigation",
]

FeedbackActorRole = Literal["manager", "operator", "security_operator", "system_admin"]

PendingRuleStatus = Literal["pending", "approved", "rejected"]

RuleEffectType = Literal["downrank", "suppress", "severity_modifier"]

ApproverRole = Literal["security_operator", "system_admin"]


class RuleScope(BaseModel):
    """Scoped dimensions for feedback rules."""

    user_id: str | None = None
    role_id: str | None = None
    department_id: str | None = None
    resource: str | None = None
    action: str | None = None
    volume_min: float | None = None
    volume_max: float | None = None
    time_start: str | None = None
    time_end: str | None = None
    feature_id: str | None = None
    pattern_key: str | None = None


class RuleEffect(BaseModel):
    """Effect applied when a scoped rule matches."""

    effect_type: RuleEffectType = "downrank"
    severity_delta: int = Field(default=-2, description="Negative lowers severity")
    suppress_alert: bool = False
    suppression_requested: bool = False
    policy_suppression_approved: bool = False


class FeedbackEvent(BaseModel):
    id: str
    tenant_id: str
    kind: FeedbackKind
    actor_id: str
    actor_role: FeedbackActorRole
    feature_id: str | None = None
    detection_class: str | None = None
    candidate_id: str | None = None
    scope: RuleScope = Field(default_factory=RuleScope)
    comment: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)
    created_at: datetime


class PendingRule(BaseModel):
    id: str
    tenant_id: str
    feedback_event_id: str
    status: PendingRuleStatus = "pending"
    scope: RuleScope
    effect: RuleEffect
    proposed_by: str
    proposed_role: FeedbackActorRole
    requires_policy_suppression_approval: bool = False
    expires_at: datetime | None = None
    created_at: datetime
    reviewed_at: datetime | None = None
    reviewed_by: str | None = None
    review_comment: str | None = None


class FeedbackRule(BaseModel):
    """Stable approved scoped rule."""

    id: str
    tenant_id: str
    pending_rule_id: str
    feedback_event_id: str
    scope: RuleScope
    effect: RuleEffect
    approved_by: str
    approved_at: datetime
    expires_at: datetime | None = None
    active: bool = True


class RuleApproval(BaseModel):
    """Audit trail for approve/reject decisions."""

    id: str
    tenant_id: str
    pending_rule_id: str
    decision: Literal["approved", "rejected"]
    approver_id: str
    approver_role: ApproverRole
    allow_policy_suppression: bool = False
    comment: str | None = None
    created_at: datetime


class DecisionContext(BaseModel):
    """Candidate context for rule matching (Faz 6 input)."""

    tenant_id: str
    feature_id: str
    user_id: str | None = None
    role_id: str | None = None
    department_id: str | None = None
    resource: str | None = None
    action: str | None = None
    volume: float | None = None
    occurred_at: datetime
    detection_class: str | None = None
    pattern_key: str | None = None


class RuleApplicationResult(BaseModel):
    matched: bool = False
    downrank: bool = False
    suppress_alert: bool = False
    severity_delta: int = 0
    applied_rule_id: str | None = None
    pending_rule_id: str | None = None
    reason: str | None = None
    policy_suppression_blocked: bool = False
