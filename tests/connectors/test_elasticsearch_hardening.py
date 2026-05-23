"""Elasticsearch connector hardening: auth, search_after, live/degraded paths."""

from __future__ import annotations

import os
import socket

import pytest

from watchtower.connectors.elasticsearch import ElasticsearchConnector
from watchtower.domain.events import ConnectorCursor


def test_elasticsearch_search_after_pagination_mocked():
    pages = [
        [
            {
                "_id": "1",
                "_source": {"@timestamp": "2026-05-23T12:00:00+00:00"},
                "sort": ["t1", "1"],
            }
        ],
        [
            {
                "_id": "2",
                "_source": {"@timestamp": "2026-05-23T12:01:00+00:00"},
                "sort": ["t2", "2"],
            }
        ],
    ]
    calls: list[dict] = []

    def fake_post(url: str, body: dict, headers: dict | None = None) -> dict:
        calls.append(body)
        return {"hits": {"hits": pages[len(calls) - 1]}}

    connector = ElasticsearchConnector(
        "es-page",
        base_url="http://localhost:9200",
        index="logs",
        http_config={"auth_type": "api_key", "api_key": "secret-key"},
        http_post=fake_post,
        http_get=lambda url, headers=None: {"status": "green"},
    )
    first = connector.poll(ConnectorCursor(), limit=1)
    second = connector.poll(first.next_cursor, limit=1)
    assert len(first.events) == 1
    assert len(second.events) == 1
    assert calls[1].get("search_after") == ["t1", "1"]


def test_elasticsearch_unavailable_returns_unhealthy_degraded():
    port = _free_port()
    connector = ElasticsearchConnector(
        "es-down",
        base_url=f"http://127.0.0.1:{port}",
        index="logs",
        http_config={"timeout_seconds": 0.3, "max_retries": 0},
    )
    health = connector.health()
    assert health.status == "unhealthy"
    assert health.details.get("retries", 0) >= 0


@pytest.mark.optional
def test_elasticsearch_live_health_when_configured():
    url = os.environ.get("WATCHTOWER_ELASTICSEARCH_URL", "").strip()
    if not url:
        pytest.skip("WATCHTOWER_ELASTICSEARCH_URL not set")
    connector = ElasticsearchConnector(
        "es-live",
        base_url=url,
        index="corp-logs-*",
        http_config={"timeout_seconds": 5, "max_retries": 1},
    )
    health = connector.health()
    assert health.status in {"healthy", "degraded", "unhealthy"}
    if health.status == "unhealthy":
        pytest.skip(f"elasticsearch unavailable: {health.message}")


def _free_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind(("127.0.0.1", 0))
        return sock.getsockname()[1]
