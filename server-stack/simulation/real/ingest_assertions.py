"""Elasticsearch / log-pipeline L3 ingest assertions."""

from __future__ import annotations

import json
import time
import urllib.error
import urllib.request

from config import ELASTICSEARCH_URL, LOG_PIPELINE_URL


def _http_json(url: str, timeout: float = 8) -> dict:
    with urllib.request.urlopen(url, timeout=timeout) as resp:
        return json.loads(resp.read().decode())


def assert_log_pipeline_health() -> dict:
    try:
        body = _http_json(f"{LOG_PIPELINE_URL}/health")
        ok = body.get("status") == "ok" and body.get("elasticsearch") in ("green", "yellow", "unknown")
        return {"target": LOG_PIPELINE_URL, "elasticsearch": body.get("elasticsearch"), "result": "PASS" if ok else "FAIL"}
    except (urllib.error.URLError, TimeoutError, json.JSONDecodeError) as exc:
        return {"target": LOG_PIPELINE_URL, "result": "FAIL", "error": str(exc)}


def assert_elasticsearch_health() -> dict:
    try:
        body = _http_json(f"{ELASTICSEARCH_URL}/_cluster/health", timeout=10)
        status = body.get("status", "red")
        ok = status in ("green", "yellow")
        return {"target": ELASTICSEARCH_URL, "cluster_status": status, "result": "PASS" if ok else "FAIL"}
    except (urllib.error.URLError, TimeoutError, json.JSONDecodeError) as exc:
        return {"target": ELASTICSEARCH_URL, "result": "FAIL", "error": str(exc)}


def _index_name(feature_id: str) -> str:
    return f"corp-logs-{feature_id.lower()}"


def assert_index_document_count(feature_id: str, min_count: int = 1, retries: int = 5) -> dict:
    index = _index_name(feature_id)
    last: dict = {"index": index, "count": 0, "result": "FAIL"}
    for _ in range(retries):
        try:
            body = _http_json(f"{ELASTICSEARCH_URL}/{index}/_count", timeout=8)
            count = int(body.get("count", 0))
            last = {"index": index, "count": count, "result": "PASS" if count >= min_count else "FAIL"}
            if last["result"] == "PASS":
                return last
        except urllib.error.HTTPError as exc:
            if exc.code == 404:
                last = {"index": index, "count": 0, "result": "FAIL", "error": "index_not_found"}
            else:
                last = {"index": index, "result": "FAIL", "error": str(exc)}
        except (urllib.error.URLError, TimeoutError, json.JSONDecodeError) as exc:
            last = {"index": index, "result": "FAIL", "error": str(exc)}
        time.sleep(0.6)
    return last


def assert_ingest_for_feature(feature_id: str, *, l3: bool = False) -> dict:
    es = assert_elasticsearch_health()
    lp = assert_log_pipeline_health()
    index = _index_name(feature_id)

    if es["result"] != "PASS":
        return {
            "assertion": f"L3:elasticsearch:{index}" if l3 else f"L2:log-pipeline:{feature_id}",
            "elasticsearch": es,
            "log_pipeline": lp,
            "result": "FAIL",
        }

    if not l3:
        return {
            "assertion": f"L2:log-pipeline:corp-events:{feature_id}",
            "elasticsearch": es,
            "log_pipeline": lp,
            "result": "PASS",
            "parity_level": "L2",
            "note": "RI-6: cluster healthy; L2 ingest gate",
        }

    count = assert_index_document_count(feature_id, min_count=1)
    ok = count["result"] == "PASS"
    return {
        "assertion": f"L3:elasticsearch:{index}",
        "elasticsearch": es,
        "log_pipeline": lp,
        "index_query": count,
        "result": "PASS" if ok else "FAIL",
        "parity_level": "L3" if ok else "L2",
    }
