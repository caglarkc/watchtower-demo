#!/usr/bin/env python3
"""HRIS mock — offboarding, leave, role-change, new-hire lifecycle events."""

from __future__ import annotations

import json
import os
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path

LOG_DIR = Path(os.environ.get("LOG_ROOT", "/var/log/corp/hris"))
AUDIT = LOG_DIR / "hris.jsonl"


def _log(body: dict) -> None:
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    row = {"service": "hris_mock", **body}
    with AUDIT.open("a", encoding="utf-8") as f:
        f.write(json.dumps(row, ensure_ascii=False) + "\n")


class Handler(BaseHTTPRequestHandler):
    def do_GET(self) -> None:
        if self.path == "/health":
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b'{"status":"ok"}')
            return
        self.send_response(404)
        self.end_headers()

    def do_POST(self) -> None:
        length = int(self.headers.get("Content-Length", 0))
        body = json.loads((self.rfile.read(length) if length else b"{}").decode() or "{}")
        if self.path.startswith("/lifecycle"):
            _log(body)
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b'{"recorded":true}')
            return
        self.send_response(404)
        self.end_headers()

    def log_message(self, *_args) -> None:
        return


def main() -> None:
    _log({"event": "startup"})
    HTTPServer(("0.0.0.0", 8080), Handler).serve_forever()


if __name__ == "__main__":
    main()
