"""Retention policy application."""

from __future__ import annotations

from datetime import UTC, datetime, timedelta

from watchtower.retention.service import RetentionService


def test_retention_deletes_old_raw_events(prod_app, bootstrapped_tenant, prod_settings):
    old = (datetime.now(UTC) - timedelta(days=30)).isoformat()
    with prod_app.session() as session:
        session.sources.create(
            bootstrapped_tenant,
            "mock",
            "retention-src",
            source_id="s-ret",
            config={"events": []},
        )
        session.conn.execute(
            """
            INSERT INTO raw_events
                (id, tenant_id, source_id, dedupe_key, payload_json, ingested_at)
            VALUES ('e-old', ?, 's-ret', 'd1', '{}', ?)
            """,
            (bootstrapped_tenant, old),
        )
        session.conn.commit()
        svc = RetentionService(session.conn, prod_settings)
        result = svc.apply(tenant_id=bootstrapped_tenant)
        remaining = session.conn.execute(
            "SELECT COUNT(*) FROM raw_events WHERE id = 'e-old'"
        ).fetchone()[0]
    assert result.deleted.get("raw_events", 0) >= 1
    assert remaining == 0
