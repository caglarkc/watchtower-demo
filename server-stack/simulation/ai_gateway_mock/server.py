#!/usr/bin/env python3
"""AI gateway mock — prompt and upload audit logs (no external internet)."""

from __future__ import annotations

import json
import os
from http.server import BaseHTTPRequestHandler
from pathlib import Path

LOG_DIR = Path(os.environ.get("LOG_ROOT", "/var/log/corp/ai_gateway"))
AUDIT = LOG_DIR / "ai_gateway.jsonl"


def _log(action: str, body: dict) -> None:
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    row = {"service": "ai_gateway", "action": action, **body}
    with AUDIT.open("a", encoding="utf-8") as f:
        f.write(json.dumps(row, ensure_ascii=False) + "\n")


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
            self._json(200, {"status": "ok", "service": "ai_gateway_mock"})
            return
        self._json(404, {"error": "not found"})

    def do_POST(self) -> None:
        length = int(self.headers.get("Content-Length", 0))
        raw = self.rfile.read(length) if length else b"{}"
        try:
            body = json.loads(raw.decode() or "{}")
        except json.JSONDecodeError:
            self._json(400, {"error": "invalid json"})
            return
        routes = {
            "/v1/prompt": ("prompt", {"accepted": True, "tokens": len(str(body.get("prompt", "")))}),
            "/v1/upload": ("upload", {"accepted": True, "bytes": body.get("bytes", 0)}),
            "/action/prompt": ("prompt", {"accepted": True}),
            "/action/upload": ("upload", {"accepted": True, "bytes": body.get("bytes", 0)}),
        }
        if self.path in routes:
            action, resp = routes[self.path]
            body.setdefault("anomaly", body.get("sensitive", False))
            _log(action, body)
            self._json(200, resp)
            return
        self._json(404, {"error": "not found"})

    def log_message(self, *_args) -> None:
        return


def main() -> None:
    _log("startup", {"status": "ok"})
    from http.server import HTTPServer
    HTTPServer(("0.0.0.0", 8080), Handler).serve_forever()


if __name__ == "__main__":
    main()
