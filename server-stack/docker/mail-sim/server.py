#!/usr/bin/env python3
"""Postfix / Dovecot / Roundcube synthetic log emitter (ROLE env selects channel)."""

from __future__ import annotations

import json
import os
import threading
import time
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path

ROLE = os.environ.get("ROLE", "postfix")
LOG_ROOT = Path(os.environ.get("LOG_ROOT", f"/var/log/corp/{ROLE}"))


def _baseline() -> None:
    LOG_ROOT.mkdir(parents=True, exist_ok=True)
    row = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "service": ROLE,
        "action": "baseline",
        "status": "ok",
    }
    with (LOG_ROOT / f"{ROLE}.jsonl").open("a", encoding="utf-8") as f:
        f.write(json.dumps(row) + "\n")


class Handler(BaseHTTPRequestHandler):
    def do_GET(self) -> None:
        if self.path == "/health":
            self.send_response(200)
            self.end_headers()
            self.wfile.write(json.dumps({"status": "ok", "role": ROLE}).encode())
            return
        self.send_response(404)
        self.end_headers()

    def log_message(self, *_args) -> None:
        return


def main() -> None:
    _baseline()
    threading.Thread(target=lambda: [(_baseline(), time.sleep(45)) for _ in iter(int, 1)], daemon=True).start()
    HTTPServer(("0.0.0.0", 8080), Handler).serve_forever()


if __name__ == "__main__":
    main()
