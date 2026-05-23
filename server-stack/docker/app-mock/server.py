#!/usr/bin/env python3
"""internal-app / artifact / siem / hypervisor real-action audit logs."""

from __future__ import annotations

import json
import os
import threading
import time
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from urllib.parse import urlparse

ROLE = os.environ.get("ROLE", "internal-app")
LOG_MAP = {
    "internal-app": "/var/log/corp/app",
    "artifact": "/var/log/corp/artifact",
    "siem": "/var/log/corp/siem",
    "hypervisor": "/var/log/corp/hypervisor",
}
LOG_ROOT = Path(os.environ.get("LOG_ROOT", LOG_MAP.get(ROLE, "/var/log/corp/app")))
AUDIT = LOG_ROOT / "audit.jsonl"


def _write(row: dict) -> None:
    LOG_ROOT.mkdir(parents=True, exist_ok=True)
    row.setdefault("timestamp", datetime.now(timezone.utc).isoformat())
    row.setdefault("service", ROLE)
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
        if self.path in ("/health", "/"):
            self._json(200, {"status": "ok", "role": ROLE})
            return
        if ROLE == "internal-app" and self.path.startswith("/api/"):
            _write({"action": "api_request", "path": self.path, "method": "GET"})
            self._json(200, {"path": self.path})
            return
        self._json(404, {"error": "not found"})

    def do_POST(self) -> None:
        path = urlparse(self.path).path
        try:
            body = self._body()
        except json.JSONDecodeError:
            self._json(400, {"error": "invalid json"})
            return
        handlers = {
            "/action/api-pattern": self._api_pattern,
            "/action/siem-suppress": self._siem_suppress,
            "/action/hypervisor-access": self._hypervisor_access,
            "/action/artifact-download": self._artifact_download,
            "/emit": lambda b: (_write(b), {"ok": True})[1],
        }
        fn = handlers.get(path)
        if not fn:
            self._json(404, {"error": "unknown action"})
            return
        self._json(200, fn(body))

    def _api_pattern(self, body: dict) -> dict:
        _write({"action": "api_pattern", "calls": body.get("calls", 1), "anomaly": body.get("anomaly", False)})
        return {"role": ROLE}

    def _siem_suppress(self, body: dict) -> dict:
        _write({"action": "suppress_rule_change", "rule": body.get("rule"), "anomaly": body.get("anomaly", False)})
        return {"role": ROLE}

    def _hypervisor_access(self, body: dict) -> dict:
        _write({"action": "console_access", "user": body.get("user"), "anomaly": body.get("anomaly", False)})
        return {"role": ROLE}

    def _artifact_download(self, body: dict) -> dict:
        _write({"action": "artifact_download", "bytes": body.get("bytes", 0), "anomaly": body.get("anomaly", False)})
        return {"role": ROLE}

    def log_message(self, *_args) -> None:
        return


def main() -> None:
    _write({"action": "startup"})

    def loop() -> None:
        while True:
            _write({"action": "heartbeat"})
            time.sleep(60)

    threading.Thread(target=loop, daemon=True).start()
    HTTPServer(("0.0.0.0", 8080), Handler).serve_forever()


if __name__ == "__main__":
    main()
