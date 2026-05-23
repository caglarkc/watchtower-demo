"""File JSONL connector tests."""

from __future__ import annotations

import json
from pathlib import Path

from watchtower.connectors.file_jsonl import FileJsonlConnector
from watchtower.domain.events import ConnectorCursor


def test_file_jsonl_ingestion(tmp_path: Path):
    log_file = tmp_path / "events.jsonl"
    lines = [
        {"timestamp": "2026-05-23T10:00:00+00:00", "user": "alice", "event_type": "login"},
        {"timestamp": "2026-05-23T10:01:00+00:00", "user": "bob", "event_type": "logout"},
    ]
    log_file.write_text("\n".join(json.dumps(x) for x in lines) + "\n", encoding="utf-8")

    connector = FileJsonlConnector("file-1", log_file)
    assert connector.health().status == "healthy"

    batch = connector.poll(ConnectorCursor(), limit=10)
    assert len(batch.events) == 2
    assert batch.events[0].payload["user"] == "alice"

    # second poll should return no new events
    batch2 = connector.poll(batch.next_cursor, limit=10)
    assert len(batch2.events) == 0
