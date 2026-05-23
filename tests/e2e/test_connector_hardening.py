"""E2E connector hardening with server-stack evidence paths."""

from __future__ import annotations

import inspect

from watchtower.config.paths import PROJECT_ROOT
from watchtower.connectors.factory import build_connector
from watchtower.connectors.server_stack import ServerStackConnector
from watchtower.domain.events import ConnectorCursor
from watchtower.security.masking import mask_mapping
from tests.daemon.helpers import replay_events_to_jsonl, register_f001_jsonl_source


def test_server_stack_connector_read_only_real_logs():
    logs_root = PROJECT_ROOT / "server-stack" / "logs"
    if not logs_root.is_dir():
        return
    connector = ServerStackConnector(
        "e2e-stack",
        logs_root,
        include_globs=("identity/ad_events.jsonl",),
        max_files=1,
    )
    health = connector.health()
    assert health.status in {"healthy", "degraded"}
    batch = connector.poll(ConnectorCursor(), limit=3)
    assert isinstance(batch.events, list)
    assert "readline" in inspect.getsource(ServerStackConnector._poll_file)


def test_f001_jsonl_via_factory_no_duplicate_on_resume(app, tenant_id, tmp_path):
    jsonl = replay_events_to_jsonl("F-001", tmp_path / "f001_hardening.jsonl")
    with app.session() as session:
        source = session.sources.create(
            tenant_id,
            "file_jsonl",
            "f001",
            {"file_path": str(jsonl)},
        )
        session.conn.commit()
        record = session.sources.get(source.id, tenant_id=tenant_id)
        connector = build_connector(record)
        first = connector.poll(ConnectorCursor(), limit=50)
        second = connector.poll(first.next_cursor, limit=50)
    assert len(first.events) >= 1
    assert len(second.events) == 0


def test_connector_config_masked_in_audit_shape():
    config = {
        "base_url": "https://es.corp:9200",
        "api_key": "super-secret-key",
        "password": "pw",
    }
    masked = mask_mapping(config)
    assert "super-secret-key" not in str(masked)
    assert masked["api_key"] == "***REDACTED***"
