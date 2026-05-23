"""Wazuh connector skeleton tests."""

from __future__ import annotations

from watchtower.connectors.wazuh import WazuhConnector
from watchtower.domain.events import ConnectorCursor


def test_wazuh_health_and_poll_mocked():
    def fake_get(url: str, headers: dict | None = None) -> dict:
        if url.endswith("/"):
            return {"title": "Wazuh API", "api_version": "4.0"}
        assert headers and headers.get("Authorization", "").startswith("Bearer ")
        return {
            "data": {
                "affected_items": [
                    {"id": "a1", "timestamp": "2026-05-23T08:00:00+00:00", "rule": {"id": 1}},
                ]
            }
        }

    connector = WazuhConnector(
        "wazuh-1",
        api_url="https://wazuh.local:55000",
        config={"token": "token"},
        http_get=fake_get,
    )
    assert connector.health().status == "healthy"
    batch = connector.poll(ConnectorCursor(), limit=10)
    assert len(batch.events) == 1
    assert batch.events[0].payload["id"] == "a1"
