#!/usr/bin/env python3
"""Squid-style proxy sink — egress, tunnel, cloud upload audit logs."""

from __future__ import annotations

import json
import os
import time
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from urllib.parse import urlparse

LOG_DIR = Path(os.environ.get("LOG_ROOT", "/var/log/corp/proxy"))
AUDIT = LOG_DIR / "proxy_sink.jsonl"
SQUID_LOG = LOG_DIR / "access.log"


def _log(action: str, body: dict) -> None:
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    row = {"service": "proxy_sink", "action": action, "timestamp": time.time(), **body}
    with AUDIT.open("a", encoding="utf-8") as f:
        f.write(json.dumps(row, ensure_ascii=False) + "\n")
    method = body.get("method", "CONNECT")
    url = body.get("url", "https://unknown.example/")
    code = body.get("status", 200)
    with SQUID_LOG.open("a", encoding="utf-8") as f:
        f.write(f'{time.time()} {body.get("client", "172.28.0.100")} {method} {url} {code}\n')


class Handler(BaseHTTPRequestHandler):
    def _json(self, code: int, body: dict) -> None:
        data = json.dumps(body).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(data)

    def _body(self) -> dict:
        length = int(self.headers.get("Content-Length", 0))
        return json.loads((self.rfile.read(length) if length else b"{}").decode() or "{}")

    def do_GET(self) -> None:
        if self.path == "/health":
            self._json(200, {"status": "ok", "service": "proxy-sink"})
            return
        self._json(404, {"error": "not found"})

    def do_POST(self) -> None:
        path = urlparse(self.path).path
        try:
            body = self._body()
        except json.JSONDecodeError:
            self._json(400, {"error": "invalid json"})
            return
        if path in ("/upload", "/action/cloud-upload"):
            body.setdefault("url", "https://dropbox.mock/upload")
            _log("cloud_upload", body)
            self._json(200, {"stored": True})
            return
        if path in ("/tunnel", "/action/tunnel"):
            body.setdefault("url", "https://tunnel.mock:443")
            body.setdefault("protocol", "TLS")
            _log("encrypted_tunnel", body)
            self._json(200, {"tunnel": "established"})
            return
        if path == "/action/external-access":
            body.setdefault("url", body.get("domain", "https://chatgpt.mock/"))
            body.setdefault("status", 403 if body.get("blocked") else 200)
            _log("external_access", body)
            self._json(200, {"allowed": not body.get("blocked")})
            return
        if path == "/action/first-seen-transfer":
            body.setdefault("bytes", 50_000_000)
            _log("first_seen_transfer", body)
            self._json(200, {"logged": True})
            return
        self._json(404, {"error": "not found"})

    def log_message(self, *_args) -> None:
        return


def main() -> None:
    _log("startup", {})
    HTTPServer(("0.0.0.0", 8080), Handler).serve_forever()


if __name__ == "__main__":
    main()
