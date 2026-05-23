#!/usr/bin/env python3
"""Phase 3 real-action mocks: vault, wiki, dlp, cloud, activity."""

from __future__ import annotations

import json
import os
import threading
import time
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from urllib.parse import urlparse

ROLE = os.environ.get("ROLE", "vault")
LOG_PATHS = {
    "vault": "/var/log/corp/vault/audit.jsonl",
    "mattermost": "/var/log/corp/mattermost/chat.jsonl",
    "cups": "/var/log/corp/cups/print.jsonl",
    "wiki": "/var/log/corp/wiki/access.jsonl",
    "suitecrm": "/var/log/corp/suitecrm/crm.jsonl",
    "dlp": "/var/log/corp/dlp/health.jsonl",
    "cloud": "/var/log/corp/cloud/upload.jsonl",
    "activity": "/var/log/corp/activity/input.jsonl",
}
AUDIT = Path(LOG_PATHS.get(ROLE, LOG_PATHS["vault"]))


def _log(extra: dict | None = None) -> None:
    AUDIT.parent.mkdir(parents=True, exist_ok=True)
    row = {"service": ROLE, "timestamp": datetime.now(timezone.utc).isoformat(), **(extra or {})}
    with AUDIT.open("a", encoding="utf-8") as f:
        f.write(json.dumps(row, ensure_ascii=False) + "\n")


class Handler(BaseHTTPRequestHandler):
    def _json(self, code: int, body: dict) -> None:
        data = json.dumps(body).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(data)

    def _body(self) -> dict:
        length = int(self.headers.get("Content-Length", 0))
        return json.loads((self.rfile.read(length) if length else b"{}").decode() or "{}")

    def do_GET(self) -> None:
        if self.path == "/health":
            self._json(200, {"status": "ok", "role": ROLE})
            return
        if ROLE == "wiki" and self.path.startswith("/download"):
            _log({"action": "wiki_download", "path": self.path})
            self._json(200, {"bytes": 1024})
            return
        self._json(404, {"error": "not found"})

    def do_POST(self) -> None:
        path = urlparse(self.path).path
        try:
            body = self._body()
        except json.JSONDecodeError:
            self._json(400, {"error": "invalid json"})
            return
        common = {"/emit": lambda b: (_log(b), {"ok": True})[1]}
        role_handlers: dict[str, dict] = {
            "vault": {
                "/action/secret-read-burst": self._vault_secret_burst,
            },
            "cloud": {"/action/s3-upload": self._cloud_upload},
            "dlp": {"/action/dlp-health": self._dlp_health},
            "wiki": {"/action/wiki-bulk-download": self._wiki_bulk},
            "activity": {
                "/action/activity-burst": self._activity_burst,
                "/action/peer-deviation": self._peer_deviation,
            },
            "cups": {"/action/print-job": self._print_job},
            "mattermost": {
                "/action/channel-export": self._mattermost_export,
                "/action/composite-bundle": self._composite_bundle,
            },
            "suitecrm": {"/action/record-chain": self._record_chain},
        }
        handlers = {**common, **role_handlers.get(ROLE, {})}
        fn = handlers.get(path)
        if not fn:
            self._json(404, {"error": "unknown action"})
            return
        self._json(200, fn(body))

    def _vault_secret_burst(self, body: dict) -> dict:
        count = int(body.get("count", 10 if body.get("anomaly") else 1))
        for i in range(count):
            _log({"action": "secret_read", "path": body.get("path", f"secret/app/{i}"), "anomaly": body.get("anomaly", False)})
        return {"reads": count}

    def _cloud_upload(self, body: dict) -> dict:
        _log(
            {
                "action": "s3_put_object",
                "bucket": body.get("bucket", "personal-cloud"),
                "bytes": body.get("bytes", 5_000_000),
                "anomaly": body.get("anomaly", False),
            }
        )
        return {"stored": True}

    def _dlp_health(self, body: dict) -> dict:
        _log({"action": "dlp_agent_health", "status": "disabled" if body.get("anomaly") else "healthy", "anomaly": body.get("anomaly", False)})
        return {"status": "logged"}

    def _wiki_bulk(self, body: dict) -> dict:
        pages = int(body.get("pages", 50 if body.get("anomaly") else 2))
        for i in range(pages):
            _log({"action": "wiki_page_download", "page_id": i, "anomaly": body.get("anomaly", False)})
        return {"pages": pages}

    def _activity_burst(self, body: dict) -> dict:
        _log({"action": "activity_burst", "events": body.get("events", 100), "anomaly": body.get("anomaly", False)})
        return {"logged": True}

    def _peer_deviation(self, body: dict) -> dict:
        _log({"action": "peer_group_deviation", "z_score": body.get("z_score", 4.2), "anomaly": body.get("anomaly", False)})
        return {"logged": True}

    def log_message(self, *_args) -> None:
        return


def main() -> None:
    _log({"action": "startup"})

    def loop() -> None:
        while True:
            _log({"action": "heartbeat"})
            time.sleep(45)

    threading.Thread(target=loop, daemon=True).start()
    HTTPServer(("0.0.0.0", 8080), Handler).serve_forever()


if __name__ == "__main__":
    main()
