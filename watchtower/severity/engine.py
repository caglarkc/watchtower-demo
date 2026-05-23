"""Severity scoring with explainable breakdown (no LLM)."""

from __future__ import annotations

from watchtower.baseline.query import BaselineQueryAPI
from watchtower.correlation.engine import CorrelationResult
from watchtower.domain.assessment import (
    SEVERITY_ORDER,
    AssessmentInput,
    CandidateAssessment,
    ScoreBreakdown,
    ScoreComponent,
    SeverityLevel,
)
from watchtower.domain.profiles import BaselineEvaluation
from watchtower.domain.rules import RuleApplicationResult
from watchtower.policy.engine import PolicyResult
from watchtower.taxonomy.models import FeatureTaxonomyEntry

_POINTS_TO_SEVERITY: list[tuple[int, SeverityLevel]] = [
    (40, "CRITICAL"),
    (25, "ALERT"),
    (10, "WARNING"),
    (0, "LOG"),
]

_SEVERITY_TO_POINTS: dict[SeverityLevel, int] = {
    "LOG": 0,
    "WARNING": 10,
    "ALERT": 25,
    "CRITICAL": 40,
}


def _max_severity(a: SeverityLevel, b: SeverityLevel) -> SeverityLevel:
    return a if SEVERITY_ORDER[a] >= SEVERITY_ORDER[b] else b


def _points_to_severity(points: int) -> SeverityLevel:
    for threshold, level in _POINTS_TO_SEVERITY:
        if points >= threshold:
            return level
    return "LOG"


def _apply_delta(level: SeverityLevel, delta: int) -> SeverityLevel:
    order = SEVERITY_ORDER[level] + delta
    order = max(0, min(3, order))
    for name, idx in SEVERITY_ORDER.items():
        if idx == order:
            return name
    return "LOG"


class SeverityEngine:
    """Combine engine outputs into final severity and score breakdown."""

    def assess(
        self,
        inp: AssessmentInput,
        *,
        entry: FeatureTaxonomyEntry,
        policy: PolicyResult,
        baseline: BaselineEvaluation | None,
        feedback: RuleApplicationResult,
        correlation: CorrelationResult,
    ) -> CandidateAssessment:
        components: list[ScoreComponent] = []
        raw = 0
        floor: SeverityLevel = entry.default_severity_floor

        if policy.violated:
            pts = _SEVERITY_TO_POINTS[policy.severity_floor]
            components.append(
                ScoreComponent(
                    source="policy",
                    points=pts,
                    reason=policy.reason or "policy violation",
                    metadata={"rule_key": policy.rule_key},
                )
            )
            raw += pts
            floor = _max_severity(floor, policy.severity_floor)

        baseline_anomaly = False
        if entry.requires_baseline and baseline is not None:
            if not baseline.is_normal and baseline.source != "none":
                pts = 20
                baseline_anomaly = True
                components.append(
                    ScoreComponent(
                        source="baseline",
                        points=pts,
                        reason=(
                            f"metric {baseline.metric_name}={baseline.value} "
                            f"outside [{baseline.effective_low:.1f}, {baseline.effective_high:.1f}] "
                            f"({baseline.source} baseline)"
                        ),
                        metadata=baseline.details,
                    )
                )
                raw += pts
            elif baseline.is_normal:
                components.append(
                    ScoreComponent(
                        source="baseline",
                        points=0,
                        reason=f"within {baseline.source} baseline for {baseline.metric_name}",
                        metadata=baseline.details,
                    )
                )

        if correlation.correlated and correlation.severity_boost > 0:
            components.append(
                ScoreComponent(
                    source="correlation",
                    points=correlation.severity_boost,
                    reason=correlation.reason or "cross-signal correlation",
                    metadata={"signal_count": correlation.signal_count},
                )
            )
            raw += correlation.severity_boost

        if feedback.matched:
            delta_pts = feedback.severity_delta * 5
            components.append(
                ScoreComponent(
                    source="feedback",
                    points=delta_pts,
                    reason=feedback.reason or "feedback rule",
                    metadata={
                        "rule_id": feedback.applied_rule_id,
                        "suppress": feedback.suppress_alert,
                        "downrank": feedback.downrank,
                    },
                )
            )
            raw += delta_pts

        if not components:
            components.append(
                ScoreComponent(
                    source="taxonomy",
                    points=_SEVERITY_TO_POINTS[floor],
                    reason=f"default floor for {entry.feature_id}",
                )
            )
            raw = _SEVERITY_TO_POINTS[floor]

        computed = _points_to_severity(raw)
        final = _max_severity(computed, floor)

        suppressed = feedback.suppress_alert and not feedback.policy_suppression_blocked
        downranked = feedback.downrank
        policy_blocked = feedback.policy_suppression_blocked

        if suppressed:
            final = "LOG"
        elif downranked:
            final = _apply_delta(final, -1)

        if policy.violated and policy_blocked:
            suppressed = False
            final = _max_severity(final, policy.severity_floor)

        should_alert = SEVERITY_ORDER[final] >= SEVERITY_ORDER["ALERT"] and not suppressed

        if baseline is not None and baseline.is_normal and not policy.violated:
            should_alert = False
            if SEVERITY_ORDER[final] >= SEVERITY_ORDER["ALERT"]:
                final = "WARNING"
                downranked = True

        breakdown = ScoreBreakdown(
            components=components,
            raw_total=raw,
            severity_floor=floor,
            final_severity=final,
            suppressed=suppressed,
            downranked=downranked,
            policy_suppression_blocked=policy_blocked,
        )

        return CandidateAssessment(
            tenant_id=inp.tenant_id,
            feature_id=inp.feature_id,
            severity=final,
            should_alert=should_alert,
            breakdown=breakdown,
            detection_class=entry.primary_detection_class,
            policy_violated=policy.violated,
            baseline_anomaly=baseline_anomaly,
            correlation_boost=correlation.correlated,
            feedback_applied=feedback.matched,
            details={
                "baseline_source": baseline.source if baseline else None,
                "feedback_rule_id": feedback.applied_rule_id,
            },
        )
