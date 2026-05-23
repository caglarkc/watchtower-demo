#!/usr/bin/env python3
"""Synthetic Zeek conn.log writer for closed LAN simulation."""

from __future__ import annotations

import json
import os
import threading
import time
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path

LOG_DIR = Path(os.environ.get("LOG_ROOT", "/var/log/corp/zeek"))
CONN_LOG = LOG_DIR / "conn.log"


def write_baseline_conn() -> None:
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    ts = datetime.now(timezone.utc).isoformat()
    line = {
        "ts": ts,
        "id.orig_h": "172.28.0.100",
        "id.resp_h": "172.28.0.11",
        "id.resp_p": 445,
        "proto": "tcp",
        "service": "smb",
        "duration": 1.2,
        "orig_bytes": 1024,
        "resp_bytes": 4096,
    }
    with CONN_LOG.open("a", encoding="utf-8") as f:
        f.write(json.dumps(line) + "\n")


class Handler(BaseHTTPRequestHandler):
    def do_GET(self) -> None:
        if self.path == "/health":
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b'{"status":"ok"}')
            return
        self.send_response(404)
        self.end_headers()

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
