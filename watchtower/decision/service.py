"""Deterministic decision orchestration across all engines."""

from __future__ import annotations

from watchtower.baseline.query import BaselineQueryAPI
from watchtower.correlation.engine import CorrelationEngine
from watchtower.domain.assessment import AssessmentInput, CandidateAssessment
from watchtower.feedback.engine import FeedbackEngine
from watchtower.policy.engine import PolicyEngine
from watchtower.severity.engine import SeverityEngine
from watchtower.taxonomy.loader import load_feature_taxonomy
from watchtower.taxonomy.models import FeatureTaxonomyEntry


class DecisionService:
    """
    Decision order (deterministic, no LLM):
    1. policy / hard-rule
    2. approved feedback exception
    3. baseline deviation
    4. cross-signal correlation
    5. severity + score breakdown
    """

    def __init__(
        self,
        *,
        policy: PolicyEngine | None = None,
        baseline: BaselineQueryAPI | None = None,
        feedback: FeedbackEngine | None = None,
        correlation: CorrelationEngine | None = None,
        severity: SeverityEngine | None = None,
    ) -> None:
        self._taxonomy = load_feature_taxonomy()
        self._policy = policy or PolicyEngine()
        self._baseline = baseline
        self._feedback = feedback
        self._correlation = correlation or CorrelationEngine()
        self._severity = severity or SeverityEngine()

    def assess(self, inp: AssessmentInput) -> CandidateAssessment:
        entry = self._require_entry(inp.feature_id)

        policy = self._policy.evaluate(inp, entry)

        feedback_result = self._empty_feedback()
        if self._feedback is not None:
            feedback_result = self._feedback.apply(
                inp, detection_class=entry.primary_detection_class
            )

        baseline_eval = None
        if self._baseline is not None and entry.requires_baseline:
            value = inp.volume if inp.volume is not None else 0.0
            baseline_eval = self._baseline.evaluate_metric(
                inp.tenant_id,
                inp.metric_name,
                value,
                user_id=inp.user_id,
                department_id=inp.department_id,
                role_id=inp.role_id,
                seniority=inp.seniority,
            )

        correlation = self._correlation.evaluate(inp, entry)

        return self._severity.assess(
            inp,
            entry=entry,
            policy=policy,
            baseline=baseline_eval,
            feedback=feedback_result,
            correlation=correlation,
        )

    def _require_entry(self, feature_id: str) -> FeatureTaxonomyEntry:
        entry = self._taxonomy.by_id().get(feature_id)
        if entry is None:
            msg = f"Unknown feature_id: {feature_id}"
            raise ValueError(msg)
        return entry

    @staticmethod
    def _empty_feedback():
        from watchtower.domain.rules import RuleApplicationResult

        return RuleApplicationResult(matched=False)
