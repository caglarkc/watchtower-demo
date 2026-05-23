"""Server-stack lab preflight and connector health."""

from __future__ import annotations

from watchtower.e2e.preflight import run_preflight
from watchtower.e2e.replay import server_stack_connector_health
from tests.fixtures.server_stack.paths import LOGS_ROOT


def test_server_stack_preflight(server_stack_preflight):
    assert server_stack_preflight.ok is True
    assert server_stack_preflight.feature_replay_count == 81
    assert server_stack_preflight.scenario_replay_count == 83


def test_preflight_direct():
    result = run_preflight()
    assert result.ok
    assert result.feature_replay_count == 81
    assert result.scenario_replay_count == 83


def test_server_stack_connector_health():
    status = server_stack_connector_health(LOGS_ROOT)
    assert status in ("healthy", "degraded")
