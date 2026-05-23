"""Server-stack connector tests."""

from __future__ import annotations

from watchtower.config.paths import PROJECT_ROOT
from watchtower.connectors.server_stack import ServerStackConnector
from watchtower.domain.events import ConnectorCursor


def test_server_stack_health_and_poll():
    logs_root = PROJECT_ROOT / "server-stack" / "logs"
    connector = ServerStackConnector(
        "ss-1",
        logs_root,
        include_globs=("identity/ad_events.jsonl",),
        max_files=1,
    )
    health = connector.health()
    assert health.status in {"healthy", "degraded"}

    batch = connector.poll(ConnectorCursor(), limit=5)
    assert len(batch.events) <= 5
    if batch.events:
        assert "user" in batch.events[0].payload or "_raw" in batch.events[0].payload
