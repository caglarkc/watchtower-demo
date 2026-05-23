"""Cross-signal correlation scoring."""

from __future__ import annotations

from pydantic import BaseModel

from watchtower.domain.assessment import AssessmentInput
from watchtower.taxonomy.models import FeatureTaxonomyEntry


class CorrelationResult(BaseModel):
    correlated: bool = False
    signal_count: int = 1
    severity_boost: int = 0
    reason: str | None = None


class CorrelationEngine:
    """Raise severity when multiple correlated signals are present."""

    BOOST_PER_EXTRA_SIGNAL = 15
    MAX_BOOST = 30

    def evaluate(
        self,
        inp: AssessmentInput,
        entry: FeatureTaxonomyEntry,
    ) -> CorrelationResult:
        signals = list(inp.related_signals)
        if inp.feature_id not in signals:
            signals = [inp.feature_id, *signals]

        is_cross = entry.primary_detection_class == "cross-signal"
        group_present = bool(inp.correlation_group)
        multi = len(signals) >= 2

        if not (is_cross or group_present or multi):
            return CorrelationResult(signal_count=1)

        count = max(len(signals), 2 if is_cross else len(signals))
        extra = max(0, count - 1)
        boost = min(self.MAX_BOOST, extra * self.BOOST_PER_EXTRA_SIGNAL)

        return CorrelationResult(
            correlated=True,
            signal_count=count,
            severity_boost=boost,
            reason=f"{count} correlated signals",
        )
