#!/usr/bin/env python3
"""Phase 3 auxiliary mocks: vault, mattermost, cups, wiki, suitecrm, dlp, cloud, activity."""

from __future__ import annotations

import json
import os
import threading
import time
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path

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
    def loop() -> None:
        while True:
            _log({"action": "heartbeat"})
            time.sleep(45)

    _log({"action": "startup"})
    threading.Thread(target=loop, daemon=True).start()
    HTTPServer(("0.0.0.0", 8080), Handler).serve_forever()


if __name__ == "__main__":
    main()
