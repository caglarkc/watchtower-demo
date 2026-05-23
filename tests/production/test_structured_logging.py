"""Structured JSON logs mask secrets."""

from __future__ import annotations

import json
import logging

from watchtower.observability.logging import emit_structured_log


def test_structured_log_masks_secrets_in_extra(caplog):
    logger = logging.getLogger("watchtower.test.structured")
    with caplog.at_level(logging.INFO, logger="watchtower.test.structured"):
        emit_structured_log(
            logger,
            logging.INFO,
            "poll complete",
            tenant_id="t1",
            source_id="src-1",
            run_id="run-1",
            graph_thread_id="thread-1",
            event_counts={"polled": 3, "stored": 2},
            severity="info",
            extra={"api_key": "super-secret-token", "ok": True},
        )
    assert len(caplog.records) == 1
    payload = json.loads(caplog.records[0].message)
    assert payload["tenant_id"] == "t1"
    assert payload["source_id"] == "src-1"
    assert payload["run_id"] == "run-1"
    assert payload["graph_thread_id"] == "thread-1"
    assert payload["event_counts"]["stored"] == 2
    assert "super-secret" not in caplog.records[0].message
    assert payload["api_key"] == "***REDACTED***"
