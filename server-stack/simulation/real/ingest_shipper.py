"""Ship real feature log paths to log-pipeline → Elasticsearch."""

from __future__ import annotations

import json
from pathlib import Path

from config import LOG_PIPELINE_URL
from http_client import post_json


def ship_feature_logs(feature_id: str, raw_assertions: list[dict]) -> dict:
    paths = [r["path"] for r in raw_assertions if r.get("result") == "PASS" and r.get("path")]
    documents: list[dict] = []
    for path_str in paths:
        path = Path(path_str)
        if not path.exists():
            continue
        for line in path.read_text(encoding="utf-8", errors="replace").splitlines()[-80:]:
            line = line.strip()
            if not line:
                continue
            try:
                row = json.loads(line)
                row.setdefault("feature_id", feature_id)
                documents.append(row)
            except json.JSONDecodeError:
                documents.append({"feature_id": feature_id, "message": line, "log_path": str(path)})
    if not documents and not paths:
        return {"shipped": False, "indexed": 0, "note": "no log paths"}
    try:
        resp = post_json(
            f"{LOG_PIPELINE_URL}/ingest",
            {
                "feature_id": feature_id,
                "index": f"corp-logs-{feature_id.lower()}",
                "paths": paths,
                "documents": documents[:200],
            },
        )
        return {"shipped": True, "indexed": resp.get("indexed", 0), "index": resp.get("index"), "pipeline": resp}
    except Exception as exc:  # noqa: BLE001
        return {"shipped": False, "error": str(exc), "indexed": 0}
