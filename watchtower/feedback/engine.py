"""Feedback engine — applies approved scoped rules in the decision path."""

from __future__ import annotations

from datetime import datetime

from watchtower.domain.assessment import AssessmentInput
from watchtower.domain.rules import DecisionContext, RuleApplicationResult
from watchtower.rules.engine import RuleEngine


class FeedbackEngine:
    """Wraps RuleEngine for deterministic decision orchestration."""

    def __init__(self, rules: RuleEngine) -> None:
        self._rules = rules

    def apply(
        self,
        inp: AssessmentInput,
        *,
        detection_class: str | None = None,
        as_of: datetime | None = None,
    ) -> RuleApplicationResult:
        ctx = DecisionContext(
            tenant_id=inp.tenant_id,
            feature_id=inp.feature_id,
            user_id=inp.user_id,
            role_id=inp.role_id,
            department_id=inp.department_id,
            resource=inp.resource,
            action=inp.action,
            volume=inp.volume,
            occurred_at=inp.occurred_at,
            detection_class=detection_class,
            pattern_key=inp.correlation_group,
        )
        return self._rules.apply_feedback_rules(ctx, as_of=as_of)
