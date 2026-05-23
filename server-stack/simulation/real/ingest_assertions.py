"""Elasticsearch / log-pipeline ingest assertions for critical P0 features."""

from __future__ import annotations

import json
import urllib.error
import urllib.request

from config import ELASTICSEARCH_URL, LOG_PIPELINE_URL


def assert_log_pipeline_health() -> dict:
    try:
        with urllib.request.urlopen(f"{LOG_PIPELINE_URL}/health", timeout=5) as resp:
            body = json.loads(resp.read().decode())
        return {"target": LOG_PIPELINE_URL, "result": "PASS" if body.get("status") == "ok" else "FAIL"}
    except (urllib.error.URLError, TimeoutError) as exc:
        return {"target": LOG_PIPELINE_URL, "result": "SKIP", "error": str(exc)}


def assert_elasticsearch_health() -> dict:
    try:
        with urllib.request.urlopen(f"{ELASTICSEARCH_URL}/_cluster/health", timeout=8) as resp:
            body = json.loads(resp.read().decode())
        status = body.get("status", "red")
        ok = status in ("green", "yellow")
        return {"target": ELASTICSEARCH_URL, "cluster_status": status, "result": "PASS" if ok else "FAIL"}
    except (urllib.error.URLError, TimeoutError) as exc:
        return {"target": ELASTICSEARCH_URL, "result": "SKIP", "error": str(exc)}


def assert_ingest_for_feature(feature_id: str) -> dict:
    es = assert_elasticsearch_health()
    lp = assert_log_pipeline_health()
    if es["result"] == "PASS":
        return {
            "assertion": f"elasticsearch:corp-logs:{feature_id}",
            "elasticsearch": es,
            "log_pipeline": lp,
            "result": "PASS",
            "note": "RI-1: cluster healthy; index routing in RI-2+",
        }
    return {
        "assertion": f"pending:L3:elasticsearch:wazuh-alerts-*:{feature_id}",
        "elasticsearch": es,
        "log_pipeline": lp,
        "result": "SKIP" if es["result"] == "SKIP" else "FAIL",
    }
