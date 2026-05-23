"""83/83 scenario replay normalization."""

from __future__ import annotations

import pytest

from tests.normalization.conftest import TENANT_ID, load_scenario_replay
from watchtower.normalization.registry import NON_CANDIDATE_EVENT_TYPES

SCENARIO_IDS = [f"S-{i:03d}" for i in range(1, 84)]


@pytest.mark.parametrize("scenario_id", SCENARIO_IDS)
def test_scenario_fixture_normalizes(scenario_id: str, normalizer):
    data = load_scenario_replay(scenario_id)
    assert data["scenario_id"] == scenario_id
    events = data.get("events", [])
    assert events

    for payload in events:
        outcome = normalizer.normalize_payload(
            payload,
            tenant_id=TENANT_ID,
            connector_type="simulation_fixture",
        )
        assert outcome.normalized is not None, outcome.unknown
        assert outcome.unknown is None
        if payload.get("scenario_id"):
            assert outcome.normalized.scenario_id == payload["scenario_id"]

        source_feature = payload.get("source_feature")
        if source_feature:
            assert outcome.normalized.feature_hint == source_feature

        if payload.get("event_type") not in NON_CANDIDATE_EVENT_TYPES:
            assert outcome.normalized.feature_hint is not None
