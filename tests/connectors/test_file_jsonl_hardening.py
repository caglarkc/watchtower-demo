"""File JSONL production behaviors: rotation, truncation, partial lines, resume."""

from __future__ import annotations

import json
from pathlib import Path

from watchtower.connectors.file_jsonl import FileJsonlConnector
from watchtower.domain.events import ConnectorCursor
def test_file_jsonl_cursor_resume_no_duplicates(tmp_path: Path):
    log_file = tmp_path / "resume.jsonl"
    rows = [{"timestamp": f"2026-05-23T10:0{i}:00+00:00", "event_type": "ping", "i": i} for i in range(5)]
    log_file.write_text("\n".join(json.dumps(r) for r in rows) + "\n", encoding="utf-8")

    connector = FileJsonlConnector("file-resume", log_file)
    first = connector.poll(ConnectorCursor(), limit=2)
    second = connector.poll(first.next_cursor, limit=2)
    third = connector.poll(second.next_cursor, limit=10)

    keys = [e.dedupe_key for e in first.events + second.events + third.events]
    assert len(keys) == len(set(keys)) == 5


def test_file_jsonl_truncation_rotation_restarts_without_duplicate(tmp_path: Path):
    log_file = tmp_path / "rotating.jsonl"
    log_file.write_text(
        json.dumps({"event_type": "a", "user": "u1"}) + "\n"
        + json.dumps({"event_type": "b", "user": "u2"}) + "\n",
        encoding="utf-8",
    )
    connector = FileJsonlConnector("rot", log_file)
    batch1 = connector.poll(ConnectorCursor(), limit=10)
    assert len(batch1.events) == 2

    # simulate truncation + new writer (same path)
    log_file.write_text(
        json.dumps({"event_type": "c", "user": "u3"}) + "\n",
        encoding="utf-8",
    )
    batch2 = connector.poll(batch1.next_cursor, limit=10)
    assert len(batch2.events) == 1
    assert batch2.events[0].payload["event_type"] == "c"
    assert batch2.events[0].dedupe_key != batch1.events[0].dedupe_key


def test_file_jsonl_partial_line_then_complete(tmp_path: Path):
    log_file = tmp_path / "partial.jsonl"
    log_file.write_bytes(b'{"event_type": "partial", "user":')
    connector = FileJsonlConnector("part", log_file)
    first = connector.poll(ConnectorCursor(), limit=5)
    assert len(first.events) == 0

    with log_file.open("ab") as handle:
        handle.write(b'"x"}\n{"event_type": "done", "user": "ok"}\n')

    second = connector.poll(first.next_cursor, limit=5)
    assert len(second.events) >= 1
    assert any(e.payload.get("event_type") == "done" for e in second.events)


def test_large_file_pagination_by_cursor(tmp_path: Path):
    log_file = tmp_path / "large.jsonl"
    with log_file.open("w", encoding="utf-8") as handle:
        for i in range(200):
            handle.write(json.dumps({"event_type": "bulk", "seq": i}) + "\n")

    connector = FileJsonlConnector("large", log_file)
    cursor = ConnectorCursor()
    total = 0
    while True:
        batch = connector.poll(cursor, limit=25)
        total += len(batch.events)
        cursor = batch.next_cursor
        if not batch.has_more and not batch.events:
            break
        if total >= 200:
            break
    assert total == 200
