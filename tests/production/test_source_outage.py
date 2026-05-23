"""Source outage graceful degradation."""

from __future__ import annotations

from watchtower.domain.events import RawEventRecord


def test_source_outage_graceful_degradation(prod_app, bootstrapped_tenant):
    with prod_app.session() as session:
        source = session.sources.create(
            bootstrapped_tenant,
            "mock",
            "failing-source",
            config={"events": [], "fail_health": True},
            source_id="src-fail",
        )
        health = session.ingest.check_health(source)
        assert health.status == "unhealthy"

        result = session.ingest.ingest_once(
            bootstrapped_tenant, source.id, limit=10
        )
        assert result.degraded is True
        assert result.stored == 0


def test_disabled_source_does_not_ingest(prod_app, bootstrapped_tenant):
    with prod_app.session() as session:
        source = session.sources.create(
            bootstrapped_tenant,
            "mock",
            "disabled",
            config={
                "events": [
                    RawEventRecord(
                        dedupe_key="e1",
                        payload={"event_type": "sql_query"},
                    ).model_dump()
                ]
            },
            source_id="src-off",
            enabled=False,
        )
        result = session.ingest.ingest_once(bootstrapped_tenant, source.id)
        assert result.error == "source is disabled"
        assert result.degraded is True
