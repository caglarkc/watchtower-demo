#!/usr/bin/env python3
"""Zeek conn.log writer with real-action emit API."""

from __future__ import annotations

import json
import os
import threading
import time
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from urllib.parse import urlparse

LOG_DIR = Path(os.environ.get("LOG_ROOT", "/var/log/corp/zeek"))
CONN_LOG = LOG_DIR / "conn.log"
DNS_LOG = LOG_DIR / "dns.log"


def _write_conn(line: dict) -> None:
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    line.setdefault("ts", datetime.now(timezone.utc).isoformat())
    with CONN_LOG.open("a", encoding="utf-8") as f:
        f.write(json.dumps(line) + "\n")


def write_baseline_conn() -> None:
    _write_conn(
        {
            "id.orig_h": "172.28.0.100",
            "id.resp_h": "172.28.0.11",
            "id.resp_p": 445,
            "proto": "tcp",
            "service": "smb",
            "duration": 1.2,
            "orig_bytes": 1024,
            "resp_bytes": 4096,
        }
    )


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
            self._json(200, {"status": "ok", "service": "zeek-synthetic"})
            return
        self._json(404, {"error": "not found"})

    def do_POST(self) -> None:
        if urlparse(self.path).path != "/emit":
            self._json(404, {"error": "not found"})
            return
        length = int(self.headers.get("Content-Length", 0))
        raw = self.rfile.read(length) if length else b"{}"
        try:
            body = json.loads(raw.decode() or "{}")
        except json.JSONDecodeError:
            self._json(400, {"error": "invalid json"})
            return
        records = body.get("records", [body])
        for rec in records:
            _write_conn(rec)
        self._json(200, {"written": len(records), "log": str(CONN_LOG)})

    def log_message(self, *_args) -> None:
        return


def _writer_loop() -> None:
    while True:
        write_baseline_conn()
        time.sleep(30)


def main() -> None:
    threading.Thread(target=_writer_loop, daemon=True).start()
    HTTPServer(("0.0.0.0", 8080), Handler).serve_forever()


if __name__ == "__main__":
    main()
