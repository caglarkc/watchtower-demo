"""Security audit: masking, read-only connectors, no remediation."""

from __future__ import annotations

import inspect
from pathlib import Path

from watchtower.connectors.server_stack import ServerStackConnector
from watchtower.security.masking import mask_mapping, mask_secret
from watchtower.services.audit import AuditService
from watchtower.storage.repositories.audit import AuditRepository
from watchtower.config.settings import WatchtowerSettings
import watchtower.graph.nodes.pipeline as graph_pipeline


def test_secret_masking_in_audit():
    settings = WatchtowerSettings(audit_log_enabled=True)
    import sqlite3

    conn = sqlite3.connect(":memory:")
    conn.row_factory = sqlite3.Row
    conn.executescript(
        """
        CREATE TABLE audit_log (
            id TEXT PRIMARY KEY, tenant_id TEXT, actor TEXT,
            action TEXT, details_json TEXT, created_at TEXT
        );
        """
    )
    repo = AuditRepository(conn)
    audit = AuditService(repo, settings)
    audit.log(
        "test.action",
        tenant_id="t1",
        details={"api_key": "super-secret", "user": "alice"},
    )
    row = conn.execute("SELECT details_json FROM audit_log").fetchone()
    assert "super-secret" not in row[0]
    assert "***REDACTED***" in row[0]


def test_mask_mapping_and_secret():
    masked = mask_mapping({"password": "x", "nested": {"token": "abc"}})
    assert masked["password"] == "***REDACTED***"
    assert masked["nested"]["token"] == "***REDACTED***"
    assert mask_secret("abcd") is not None


def test_server_stack_connector_is_read_only_poll():
    poll_file_src = inspect.getsource(ServerStackConnector._poll_file)
    assert "readline" in poll_file_src
    assert "open(" in poll_file_src
    assert "'w'" not in poll_file_src and 'mode="w"' not in poll_file_src


def test_no_auto_remediation_in_graph_nodes():
    src = inspect.getsource(graph_pipeline)
    for forbidden in ("remediat", "auto_block", "kill_process", "quarantine_host"):
        assert forbidden not in src.lower()
