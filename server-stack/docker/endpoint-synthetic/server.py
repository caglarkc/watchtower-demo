#!/usr/bin/env python3
"""Synthetic endpoint / AD / USB event API for closed LAN."""

from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

LOG_ROOT = Path(os.environ.get("LOG_ROOT", "/var/log/corp/endpoint"))
DOMAIN = os.environ.get("DOMAIN", "corp.local")


def _write(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    payload.setdefault("timestamp", datetime.now(timezone.utc).isoformat())
    payload.setdefault("domain", DOMAIN)
    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(payload, ensure_ascii=False) + "\n")


class Handler(BaseHTTPRequestHandler):
    def _json(self, code: int, body: dict) -> None:
        data = json.dumps(body).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def do_GET(self) -> None:
        if self.path == "/health":
            self._json(200, {"status": "ok", "service": "endpoint-synthetic"})
            return
        self._json(404, {"error": "not found"})

    def do_POST(self) -> None:
        parsed = urlparse(self.path)
        length = int(self.headers.get("Content-Length", 0))
        raw = self.rfile.read(length) if length else b"{}"
        try:
            body = json.loads(raw.decode() or "{}")
        except json.JSONDecodeError:
            self._json(400, {"error": "invalid json"})
            return

        if parsed.path == "/emit":
            event_type = body.get("event_type", "generic")
            log_file = LOG_ROOT / f"{event_type}.jsonl"
            _write(log_file, body)
            self._json(200, {"written": str(log_file), "event_type": event_type})
            return

        self._json(404, {"error": "not found"})

    def log_message(self, *_args) -> None:
        return


def main() -> None:
    LOG_ROOT.mkdir(parents=True, exist_ok=True)
    HTTPServer(("0.0.0.0", 8080), Handler).serve_forever()


if __name__ == "__main__":
    main()
