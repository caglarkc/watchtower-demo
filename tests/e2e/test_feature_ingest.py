"""81/81 server-stack feature replay ingest + normalize E2E."""

from __future__ import annotations

import pytest

from watchtower.e2e.replay import FEATURE_IDS, ingest_feature_replay

TENANT = "e2e-feature-tenant"


@pytest.mark.parametrize("feature_id", FEATURE_IDS)
def test_feature_replay_ingested_and_normalized(
    feature_id: str,
    normalizer,
    extractor,
    server_stack_preflight,
):
    del server_stack_preflight
    result = ingest_feature_replay(
        normalizer,
        extractor,
        tenant_id=TENANT,
        feature_id=feature_id,
    )
    assert result.replay_id == feature_id
    assert result.events_total >= 1
    assert result.normalized_count >= 1, f"{feature_id}: no normalized events"
