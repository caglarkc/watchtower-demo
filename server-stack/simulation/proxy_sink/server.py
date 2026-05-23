#!/usr/bin/env python3
"""Proxy sink — cloud upload and tunnel protocol simulation."""

from __future__ import annotations

import json
import os
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path

LOG_DIR = Path(os.environ.get("LOG_ROOT", "/var/log/corp/proxy"))
AUDIT = LOG_DIR / "proxy_sink.jsonl"


def _log(action: str, body: dict) -> None:
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    row = {"service": "proxy_sink", "action": action, **body}
    with AUDIT.open("a", encoding="utf-8") as f:
        f.write(json.dumps(row, ensure_ascii=False) + "\n")


class Handler(BaseHTTPRequestHandler):
    def _json(self, code: int, body: dict) -> None:
        data = json.dumps(body).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(data)

    def do_GET(self) -> None:
        if self.path == "/health":
            self._json(200, {"status": "ok"})
            return
        self.send_response(404)
        self.end_headers()

    def do_POST(self) -> None:
        length = int(self.headers.get("Content-Length", 0))
        raw = self.rfile.read(length) if length else b"{}"
        body = json.loads(raw.decode() or "{}")
        if self.path == "/upload":
            _log("cloud_upload", body)
            self._json(200, {"stored": True})
            return
        if self.path == "/tunnel":
            _log("encrypted_tunnel", body)
            self._json(200, {"tunnel": "established"})
            return
        self._json(404, {"error": "not found"})

    def log_message(self, *_args) -> None:
        return


def main() -> None:
    _log("startup", {})
    HTTPServer(("0.0.0.0", 8080), Handler).serve_forever()


if __name__ == "__main__":
    main()
