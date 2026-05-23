"""Cursor deduplication integration tests."""

from __future__ import annotations

import json
from pathlib import Path


def test_cursor_duplicate_event_not_written_twice(app, tenant_id, tmp_path: Path):
    log_file = tmp_path / "dup.jsonl"
    log_file.write_text(
        json.dumps({"timestamp": "2026-05-23T10:00:00+00:00", "n": 1}) + "\n",
        encoding="utf-8",
    )

    with app.session() as session:
        source = session.sources.create(
            tenant_id,
            "file_jsonl",
            "dup-file",
            {"file_path": str(log_file)},
        )
        first = session.ingest.ingest_once(tenant_id, source.id, limit=10)
        second = session.ingest.ingest_once(tenant_id, source.id, limit=10)
        total = session.raw_events.count_for_source(tenant_id, source.id)

    assert first.stored == 1
    assert second.stored == 0
    assert second.duplicates == 0
    assert total == 1
