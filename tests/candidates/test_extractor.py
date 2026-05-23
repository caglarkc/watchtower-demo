"""Candidate extractor unit tests."""

from __future__ import annotations

from datetime import UTC, datetime

from watchtower.candidates.extractor import CandidateExtractor
from watchtower.domain.normalized_event import NormalizedEvent


def test_candidate_has_required_fields():
    extractor = CandidateExtractor()
    normalized = NormalizedEvent(
        id="norm-1",
        tenant_id="t1",
        schema_format="simulation_fixture",
        event_type="smb_read_volume",
        actor="cfo",
        action="smb_read_volume",
        resource="finance-share",
        occurred_at=datetime.now(UTC),
        feature_hint="F-001",
        anomaly_flag=True,
    )
    candidate = extractor.extract(normalized)
    assert candidate is not None
    assert candidate.actor == "cfo"
    assert candidate.action == "smb_read_volume"
    assert candidate.resource == "finance-share"
    assert candidate.occurred_at == normalized.occurred_at
    assert candidate.feature_hint == "F-001"


def test_scenario_anchor_not_a_candidate():
    extractor = CandidateExtractor()
    normalized = NormalizedEvent(
        tenant_id="t1",
        schema_format="simulation_fixture",
        event_type="scenario_anchor",
        action="scenario_anchor",
        resource="scenario",
        occurred_at=datetime.now(UTC),
        feature_hint="F-001",
    )
    assert extractor.extract(normalized) is None


def test_missing_feature_hint_not_candidate():
    extractor = CandidateExtractor()
    normalized = NormalizedEvent(
        tenant_id="t1",
        schema_format="server_stack",
        event_type="mystery",
        action="mystery",
        resource="x",
        occurred_at=datetime.now(UTC),
        feature_hint=None,
    )
    assert extractor.extract(normalized) is None
