"""Correlation engine unit tests."""

from __future__ import annotations

from datetime import UTC, datetime

from watchtower.correlation.engine import CorrelationEngine
from watchtower.domain.assessment import AssessmentInput
from watchtower.taxonomy.loader import load_feature_taxonomy


def test_extra_signals_increase_boost():
    taxonomy = load_feature_taxonomy()
    entry = taxonomy.by_id()["F-009"]
    engine = CorrelationEngine()
    base = AssessmentInput(
        tenant_id="t1",
        feature_id="F-009",
        occurred_at=datetime(2026, 5, 23, 10, 0, 0, tzinfo=UTC),
        related_signals=[],
    )
    multi = base.model_copy(update={"related_signals": ["F-001", "F-002", "F-003"]})
    single = engine.evaluate(base, entry)
    boosted = engine.evaluate(multi, entry)
    assert boosted.severity_boost > single.severity_boost
    assert boosted.correlated is True
