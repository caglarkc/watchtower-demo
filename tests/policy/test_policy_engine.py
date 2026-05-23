"""Policy engine tests."""

from __future__ import annotations

from watchtower.domain.assessment import AssessmentInput
from watchtower.policy.engine import PolicyEngine
from watchtower.taxonomy.loader import load_feature_taxonomy
from datetime import UTC, datetime


def test_frontend_direct_db_access_policy_critical():
    taxonomy = load_feature_taxonomy()
    entry = taxonomy.by_id()["F-010"]
    engine = PolicyEngine()
    inp = AssessmentInput(
        tenant_id="t1",
        feature_id="F-010",
        user_id="dev-1",
        role_id="frontend",
        department_id="engineering",
        resource="PROD-DB-01",
        action="direct_sql",
        occurred_at=datetime(2026, 5, 23, 12, 0, 0, tzinfo=UTC),
    )
    result = engine.evaluate(inp, entry)
    assert result.violated is True
    assert result.severity_floor == "CRITICAL"
    assert result.rule_key == "frontend_direct_db_access"
