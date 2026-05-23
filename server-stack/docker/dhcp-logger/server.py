#!/usr/bin/env python3
"""DHCP/Kea-style lease log writer for real integration tests."""

from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from urllib.parse import urlparse

LOG_DIR = Path(os.environ.get("LOG_ROOT", "/var/log/corp/dhcp"))
DHCP_LOG = LOG_DIR / "dhcpd.log"


def _write(row: dict) -> None:
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    row.setdefault("ts", datetime.now(timezone.utc).isoformat())
    with DHCP_LOG.open("a", encoding="utf-8") as f:
        f.write(json.dumps(row) + "\n")


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
        self._json(404, {})

    def do_POST(self) -> None:
        if urlparse(self.path).path != "/action/rogue-dhcp":
            self._json(404, {})
            return
        length = int(self.headers.get("Content-Length", 0))
        body = json.loads((self.rfile.read(length) if length else b"{}").decode() or "{}")
        count = int(body.get("count", 2))
        for i in range(count):
            _write(
                {
                    "event": "DHCPDISCOVER",
                    "mac": body.get("mac", f"aa:bb:cc:dd:ee:{i:02x}"),
                    "server": body.get("rogue_server", "172.28.0.199"),
                    "anomaly": "duplicate_scope",
                }
            )
        self._json(200, {"events": count})

    def log_message(self, *_args) -> None:
        return


def main() -> None:
    HTTPServer(("0.0.0.0", 8080), Handler).serve_forever()


if __name__ == "__main__":
    main()
