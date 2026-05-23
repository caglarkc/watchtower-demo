"""83/83 server-stack scenario replay ingest + normalize E2E."""

from __future__ import annotations

import pytest

from watchtower.e2e.replay import SCENARIO_IDS, ingest_scenario_replay

TENANT = "e2e-scenario-tenant"


@pytest.mark.parametrize("scenario_id", SCENARIO_IDS)
def test_scenario_replay_ingested_and_normalized(
    scenario_id: str,
    normalizer,
    extractor,
    server_stack_preflight,
):
    del server_stack_preflight
    result = ingest_scenario_replay(
        normalizer,
        extractor,
        tenant_id=TENANT,
        scenario_id=scenario_id,
    )
    assert result.replay_id == scenario_id
    assert result.events_total >= 1
    assert result.normalized_count >= 1, f"{scenario_id}: no normalized events"
