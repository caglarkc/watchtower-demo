"""File JSONL ingest integration tests."""

from __future__ import annotations

import json
from pathlib import Path


def test_file_jsonl_ingest_stores_raw_events(app, tenant_id, tmp_path: Path):
    log_file = tmp_path / "ingest.jsonl"
    rows = [{"timestamp": f"2026-05-23T10:0{i}:00+00:00", "i": i} for i in range(3)]
    log_file.write_text("\n".join(json.dumps(r) for r in rows) + "\n", encoding="utf-8")

    with app.session() as session:
        source = session.sources.create(
            tenant_id,
            "file_jsonl",
            "test-jsonl",
            {"file_path": str(log_file)},
        )
        result = session.ingest.ingest_once(tenant_id, source.id, limit=50)
        count = session.raw_events.count_for_source(tenant_id, source.id)

    assert result.error is None
    assert result.stored == 3
    assert count == 3
