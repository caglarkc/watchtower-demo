"""Load-style ingest batch against mock connector."""

from __future__ import annotations

from watchtower.domain.events import RawEventRecord


def test_load_batch_ingest(prod_app, bootstrapped_tenant):
    events = [
        RawEventRecord(
            dedupe_key=f"load-{i}",
            payload={"event_type": "sql_query", "user": f"u{i}"},
        ).model_dump()
        for i in range(200)
    ]
    with prod_app.session() as session:
        source = session.sources.create(
            bootstrapped_tenant,
            "mock",
            "load-source",
            config={"events": events},
            source_id="src-load",
        )
        result = session.ingest.ingest_once(
            bootstrapped_tenant, source.id, limit=500
        )
        assert result.stored == 200
