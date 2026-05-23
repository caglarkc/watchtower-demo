#!/usr/bin/env python3
"""Lightweight log assertion pipeline (Elasticsearch substitute for Phase 1)."""

from __future__ import annotations

import json
import os
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path

LOG_ROOT = Path(os.environ.get("LOG_ROOT", "/var/log/corp"))


class Handler(BaseHTTPRequestHandler):
    def do_GET(self) -> None:
        if self.path == "/health":
            body = json.dumps({"status": "ok", "log_root": str(LOG_ROOT)}).encode()
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(body)
            return
        if self.path == "/stats":
            count = sum(1 for _ in LOG_ROOT.rglob("*.jsonl")) if LOG_ROOT.exists() else 0
            body = json.dumps({"jsonl_files": count}).encode()
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(body)
            return
        self.send_response(404)
        self.end_headers()

    def log_message(self, *_args) -> None:
        return


def main() -> None:
    LOG_ROOT.mkdir(parents=True, exist_ok=True)
    HTTPServer(("0.0.0.0", 9201), Handler).serve_forever()


if __name__ == "__main__":
    main()
