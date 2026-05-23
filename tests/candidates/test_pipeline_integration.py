"""Raw → normalized → candidate pipeline integration."""

from __future__ import annotations

import json
from pathlib import Path

from watchtower.domain.events import RawEventRecord


def test_pipeline_raw_to_candidate(app, tenant_id, tmp_path: Path):
    log_file = tmp_path / "pipe.jsonl"
    log_file.write_text(
        json.dumps(
            {
                "timestamp": "2026-05-23T12:00:00+00:00",
                "event_type": "smb_read_volume",
                "user": "cfo",
                "bytes_read": 999,
                "anomaly": True,
            }
        )
        + "\n",
        encoding="utf-8",
    )

    with app.session() as session:
        source = session.sources.create(
            tenant_id,
            "file_jsonl",
            "pipe-src",
            {"file_path": str(log_file)},
        )
        session.ingest.ingest_once(tenant_id, source.id, limit=10)
        result = session.pipeline.process_raw_batch(tenant_id, limit=10)
        raw_count = session.raw_events.count_for_source(tenant_id, source.id)
        candidate_count = session.candidate_events.count_for_tenant(tenant_id)

    assert raw_count >= 1
    assert result.normalized >= 1
    assert result.candidates >= 1
    assert candidate_count >= 1


def test_duplicate_raw_reprocess_does_not_duplicate_candidates(app, tenant_id):
    event = RawEventRecord(
        dedupe_key="dup-pipe-1",
        payload={
            "timestamp": "2026-05-23T12:00:00+00:00",
            "event_type": "port_scan",
            "user": "alice",
            "anomaly": True,
        },
    )
    with app.session() as session:
        source = session.sources.create(tenant_id, "mock", "m", {"events": []})
        session.raw_events.insert_if_new(tenant_id, source.id, event)
        first = session.pipeline.process_raw_batch(tenant_id, limit=10)
        second = session.pipeline.process_raw_batch(tenant_id, limit=10)
        count = session.candidate_events.count_for_tenant(tenant_id)

    assert first.candidates == 1
    assert second.candidates == 0
    assert count == 1
