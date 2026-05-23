"""Wazuh connector: token auth, time cursor, real timeout/outage."""

from __future__ import annotations

import socket

from watchtower.connectors.wazuh import WazuhConnector
from watchtower.domain.events import ConnectorCursor
from watchtower.daemon.service import DaemonService


def test_wazuh_token_auth_and_time_window_cursor():
    calls: list[str] = []

    def fake_get(url: str, headers: dict | None = None) -> dict:
        calls.append(url)
        if url.endswith("/"):
            return {"title": "Wazuh API", "api_version": "4.0"}
        assert "timestamp>" in url
        assert "offset=0" in url
        return {
            "data": {
                "affected_items": [
                    {"id": "a1", "timestamp": "2026-05-23T08:00:00+00:00"},
                ]
            }
        }

    connector = WazuhConnector(
        "wazuh-1",
        api_url="https://wazuh.local:55000",
        config={"token": "static-token", "time_window_minutes": 30},
        http_get=fake_get,
    )
    health = connector.health()
    assert health.status == "healthy"
    batch = connector.poll(ConnectorCursor(), limit=5)
    assert len(batch.events) == 1
    assert batch.next_cursor.wazuh_state().get("offset") == 1


def test_wazuh_real_timeout_unhealthy():
    port = _free_port()
    connector = WazuhConnector(
        "wazuh-down",
        api_url=f"http://127.0.0.1:{port}",
        config={"token": "x", "timeout_seconds": 0.3, "max_retries": 0},
    )
    health = connector.health()
    assert health.status == "unhealthy"


def test_wazuh_timeout_does_not_stop_daemon_other_sources(app, tenant_id, f001_jsonl):
    from tests.daemon.helpers import register_f001_jsonl_source

    register_f001_jsonl_source(app, tenant_id, f001_jsonl, source_id="src-good")
    port = _free_port()
    with app.session() as session:
        session.sources.create(
            tenant_id,
            "wazuh",
            "wazuh-dead",
            config={
                "api_url": f"http://127.0.0.1:{port}",
                "token": "t",
                "timeout_seconds": 0.3,
                "max_retries": 0,
            },
            source_id="src-wazuh-dead",
        )
        session.conn.commit()

    with app.session() as session:
        summary = DaemonService(session).run_once(tenant_id)
        session.conn.commit()

    assert summary.sources_failed >= 1
    assert summary.raw_stored >= 1


def _free_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind(("127.0.0.1", 0))
        return sock.getsockname()[1]
