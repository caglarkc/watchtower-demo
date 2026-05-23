"""81/81 feature replay fixture normalization."""

from __future__ import annotations

import pytest

from tests.normalization.conftest import TENANT_ID, load_feature_replay
from watchtower.normalization.registry import EVENT_TYPE_TO_FEATURE

FEATURE_IDS = [f"F-{i:03d}" for i in range(1, 82)]


@pytest.mark.parametrize("feature_id", FEATURE_IDS)
def test_feature_fixture_normalizes(feature_id: str, normalizer):
    data = load_feature_replay(feature_id)
    assert data["feature_id"] == feature_id
    events = data.get("events", [])
    assert events, f"{feature_id} has no events"

    for payload in events:
        outcome = normalizer.normalize_payload(
            payload,
            tenant_id=TENANT_ID,
            connector_type="simulation_fixture",
            context_feature_id=feature_id,
        )
        assert outcome.normalized is not None, outcome.unknown
        assert outcome.unknown is None
        assert outcome.normalized.feature_hint == feature_id
        assert outcome.normalized.action
        assert outcome.normalized.occurred_at is not None

    primary_type = events[0].get("event_type")
    if primary_type:
        assert EVENT_TYPE_TO_FEATURE.get(str(primary_type)) == feature_id
