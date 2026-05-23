"""Graceful degradation when connectors fail."""

from __future__ import annotations

from watchtower.connectors.mock import MockConnector


def test_source_poll_failure_does_not_crash_ingest(app, tenant_id):
    with app.session() as session:
        source = session.sources.create(
            tenant_id,
            "mock",
            "failing-mock",
            {"fail_poll": True},
        )
        result = session.ingest.ingest_once(tenant_id, source.id, limit=10)
        count = session.raw_events.count_for_source(tenant_id, source.id)

    assert result.degraded is True
    assert result.stored == 0
    assert result.error is not None
    assert "poll" in result.error.lower()
    assert count == 0


def test_unhealthy_source_skips_poll(app, tenant_id, monkeypatch):
    with app.session() as session:
        source = session.sources.create(
            tenant_id,
            "mock",
            "unhealthy-mock",
            {},
        )

        unhealthy = MockConnector(source.id, fail_health=False)

        def _health_override() -> object:
            from watchtower.domain.events import SourceHealth

            return SourceHealth(status="unhealthy", message="down")

        unhealthy.health = _health_override  # type: ignore[method-assign]

        monkeypatch.setattr(
            "watchtower.ingest.service.build_connector",
            lambda _src: unhealthy,
        )
        result = session.ingest.ingest_once(tenant_id, source.id, limit=10)

    assert result.degraded is True
    assert result.stored == 0
    assert result.health_status == "unhealthy"
