"""Elasticsearch connector tests (mocked HTTP)."""

from __future__ import annotations

from watchtower.connectors.elasticsearch import ElasticsearchConnector
from watchtower.domain.events import ConnectorCursor


def test_elasticsearch_health_and_query_mocked():
    hits = [
        {
            "_id": "1",
            "_source": {"@timestamp": "2026-05-23T12:00:00+00:00", "user": "u1"},
            "sort": ["2026-05-23T12:00:00+00:00", "1"],
        },
        {
            "_id": "2",
            "_source": {"@timestamp": "2026-05-23T12:01:00+00:00", "user": "u2"},
            "sort": ["2026-05-23T12:01:00+00:00", "2"],
        },
    ]

    def fake_post(url: str, body: dict, headers: dict | None = None) -> dict:
        assert "/_search" in url
        assert body["size"] == 2
        return {"hits": {"hits": hits}}

    def fake_get(url: str, headers: dict | None = None) -> dict:
        return fake_get_health(url)

    def fake_get_health(url: str) -> dict:
        assert "_cluster/health" in url
        return {"status": "green", "cluster_name": "test"}

    connector = ElasticsearchConnector(
        "es-1",
        base_url="http://localhost:9200",
        index="corp-logs-test",
        http_get=fake_get,
        http_post=fake_post,
    )

    health = connector.health()
    assert health.status == "healthy"

    batch = connector.poll(ConnectorCursor(), limit=2)
    assert len(batch.events) == 2
    assert batch.events[0].payload["user"] == "u1"
    assert batch.next_cursor.es_search_after() == hits[-1]["sort"]
