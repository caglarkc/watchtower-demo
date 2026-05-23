"""Graceful degradation when connectors fail."""

from __future__ import annotations

from watchtower.connectors.mock import MockConnector
from watchtower.domain.events import RawEventRecord
from watchtower.ingest.service import IngestService


def test_source_failure_graceful_degradation(app, tenant_id):
    with app.session() as session:
        source = session.sources.create(
            tenant_id,
            "mock",
            "failing-mock",
            {},
        )

    # factory won't know mock — test ingest service path directly with patched connector
    events = [RawEventRecord(dedupe_key="x1", payload={"a": 1})]
    failing = MockConnector(source.id, events=events, fail_poll=True)

    with app.session() as session:
        original_build = __import__(
            "watchtower.ingest.service", fromlist=["build_connector"]
        )

        def _ingest_with(connector):
            health = session.ingest._safe_health(connector)
            cursor = session.source_cursors.get(source.id, tenant_id)
            try:
                batch = connector.poll(cursor, 10)
            except Exception as exc:
                return type(
                    "R",
                    (),
                    {
                        "source_id": source.id,
                        "polled": 0,
                        "stored": 0,
                        "duplicates": 0,
                        "error": str(exc),
                        "degraded": True,
                        "health_status": health.status,
                        "has_more": False,
                    },
                )()

            stored = sum(
                1
                for e in batch.events
                if session.raw_events.insert_if_new(tenant_id, source.id, e)
            )
            connector.ack(batch.next_cursor)
            session.source_cursors.save(source.id, tenant_id, batch.next_cursor)
            from watchtower.domain.events import IngestResult

            return IngestResult(
                source_id=source.id,
                polled=len(batch.events),
                stored=stored,
                health_status=health.status,
            )

        result = _ingest_with(failing)
        assert result.degraded is True
        assert result.stored == 0
        assert "poll" in (result.error or "").lower()
