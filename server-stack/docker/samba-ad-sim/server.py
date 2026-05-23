#!/usr/bin/env python3
"""Samba AD simulation — emits Windows-style identity logs when full AD DC is unavailable."""

from __future__ import annotations

import json
import os
import threading
import time
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path

LOG_DIR = Path(os.environ.get("LOG_ROOT", "/var/log/corp/identity"))
DOMAIN = os.environ.get("DOMAIN", "corp.local")


def _emit(event_id: int, **fields: object) -> None:
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    row = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "domain": DOMAIN,
        "event_id": event_id,
        **fields,
    }
    with (LOG_DIR / "ad_events.jsonl").open("a", encoding="utf-8") as f:
        f.write(json.dumps(row) + "\n")


def _baseline_loop() -> None:
    while True:
        _emit(4624, user="svc_sql", logon_type=5, result="success")
        time.sleep(60)


class Handler(BaseHTTPRequestHandler):
    def do_GET(self) -> None:
        if self.path == "/health":
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b'{"status":"ok","service":"samba-ad-sim"}')
            return
        self.send_response(404)
        self.end_headers()

    def log_message(self, *_args) -> None:
        return


def main() -> None:
    threading.Thread(target=_baseline_loop, daemon=True).start()
    HTTPServer(("0.0.0.0", 8080), Handler).serve_forever()


if __name__ == "__main__":
    main()
