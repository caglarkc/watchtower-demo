"""Server-stack log ingestion integration tests."""

from __future__ import annotations

from watchtower.config.paths import PROJECT_ROOT


def test_server_stack_log_ingestion(app, tenant_id, settings):
    logs_root = PROJECT_ROOT / "server-stack" / "logs"
    if not logs_root.is_dir():
        return  # skip when server-stack not present

    with app.session() as session:
        source = session.sources.create(
            tenant_id,
            "server_stack",
            "demo-stack",
            {
                "logs_root": str(logs_root),
                "include_globs": ["identity/ad_events.jsonl"],
                "max_files": 1,
            },
        )
        result = session.ingest.ingest_once(tenant_id, source.id, limit=10)
        count = session.raw_events.count_for_source(tenant_id, source.id)

    assert result.error is None
    assert result.polled >= 1
    assert result.stored >= 1
    assert count == result.stored
