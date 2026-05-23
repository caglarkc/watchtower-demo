#!/usr/bin/env python3
"""Log pipeline — ship host logs to Elasticsearch (corp-logs-* indices)."""

from __future__ import annotations

import json
import os
import urllib.error
import urllib.request
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path

LOG_ROOT = Path(os.environ.get("LOG_ROOT", "/var/log/corp"))
ES_URL = os.environ.get("ELASTICSEARCH_URL", "http://172.28.0.17:9200").rstrip("/")
HOST_LOG_PREFIX = Path(os.environ.get("HOST_LOG_PREFIX", "/var/log/corp/host"))


def _es_request(method: str, path: str, body: bytes | None = None) -> dict:
    url = f"{ES_URL}{path}"
    headers = {"Content-Type": "application/json"}
    req = urllib.request.Request(url, data=body, method=method, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            return json.loads(resp.read().decode())
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode(errors="replace")
        raise RuntimeError(f"ES {method} {path}: {exc.code} {detail}") from exc


def _ensure_index(index: str) -> None:
    try:
        _es_request("GET", f"/{index}")
        return
    except RuntimeError:
        _es_request(
            "PUT",
            f"/{index}",
            json.dumps(
                {
                    "settings": {"number_of_shards": 1, "number_of_replicas": 0},
                    "mappings": {"properties": {"feature_id": {"type": "keyword"}, "@timestamp": {"type": "date"}}},
                }
            ).encode(),
        )


def _bulk_index(index: str, documents: list[dict]) -> int:
    if not documents:
        return 0
    _ensure_index(index)
    lines: list[str] = []
    for doc in documents:
        lines.append(json.dumps({"index": {"_index": index}}))
        lines.append(json.dumps(doc, ensure_ascii=False))
    payload = ("\n".join(lines) + "\n").encode()
    req = urllib.request.Request(
        f"{ES_URL}/_bulk",
        data=payload,
        method="POST",
        headers={"Content-Type": "application/x-ndjson"},
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        result = json.loads(resp.read().decode())
    if result.get("errors"):
        raise RuntimeError(f"bulk index errors for {index}")
    return len(documents)


def _resolve_path(path_str: str) -> Path:
    p = Path(path_str)
    if p.is_absolute() and p.exists():
        return p
    host = HOST_LOG_PREFIX / path_str.lstrip("/")
    if host.exists():
        return host
    return p


def _read_documents(feature_id: str, paths: list[str], inline: list[dict]) -> list[dict]:
    docs: list[dict] = []
    for item in inline:
        docs.append({**item, "feature_id": feature_id})
    for path_str in paths:
        path = _resolve_path(path_str)
        if not path.exists():
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        for line in text.splitlines()[-100:]:
            line = line.strip()
            if not line:
                continue
            try:
                row = json.loads(line)
                row.setdefault("feature_id", feature_id)
                docs.append(row)
            except json.JSONDecodeError:
                docs.append({"feature_id": feature_id, "message": line, "log_path": str(path)})
    return docs


class Handler(BaseHTTPRequestHandler):
    def _json_response(self, code: int, body: dict) -> None:
        data = json.dumps(body).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(data)

    def _read_body(self) -> dict:
        length = int(self.headers.get("Content-Length", 0))
        raw = self.rfile.read(length) if length else b"{}"
        return json.loads(raw.decode() or "{}")

    def do_GET(self) -> None:
        if self.path == "/health":
            es_status = "unknown"
            try:
                h = _es_request("GET", "/_cluster/health")
                es_status = h.get("status", "red")
            except (RuntimeError, urllib.error.URLError):
                es_status = "unreachable"
            self._json_response(
                200,
                {"status": "ok", "log_root": str(LOG_ROOT), "elasticsearch": es_status, "es_url": ES_URL},
            )
            return
        if self.path.startswith("/count/"):
            index = self.path.split("/count/", 1)[1]
            try:
                c = _es_request("GET", f"/{index}/_count")
                self._json_response(200, {"index": index, "count": c.get("count", 0)})
            except RuntimeError as exc:
                self._json_response(404, {"index": index, "error": str(exc)})
            return
        self.send_response(404)
        self.end_headers()

    def do_POST(self) -> None:
        if self.path != "/ingest":
            self.send_response(404)
            self.end_headers()
            return
        try:
            body = self._read_body()
        except json.JSONDecodeError:
            self._json_response(400, {"error": "invalid json"})
            return
        feature_id = body.get("feature_id", "F-000")
        index = body.get("index", f"corp-logs-{feature_id.lower()}")
        docs = _read_documents(feature_id, body.get("paths", []), body.get("documents", []))
        try:
            indexed = _bulk_index(index, docs)
            self._json_response(200, {"feature_id": feature_id, "index": index, "indexed": indexed})
        except (RuntimeError, urllib.error.URLError) as exc:
            self._json_response(502, {"error": str(exc)})

    def log_message(self, *_args) -> None:
        return


def main() -> None:
    LOG_ROOT.mkdir(parents=True, exist_ok=True)
    HOST_LOG_PREFIX.mkdir(parents=True, exist_ok=True)
    HTTPServer(("0.0.0.0", 9201), Handler).serve_forever()


if __name__ == "__main__":
    main()
