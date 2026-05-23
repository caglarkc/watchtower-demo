#!/usr/bin/env python3
"""Gitea real clone/fetch actions + access log."""

from __future__ import annotations

import json
import os
import subprocess
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from urllib.parse import urlparse

LOG_ROOT = Path(os.environ.get("LOG_ROOT", "/var/log/corp/gitea"))
ACCESS_LOG = LOG_ROOT / "gitea-access.jsonl"
GITEA_URL = os.environ.get("GITEA_URL", "http://corp-gitea:3000")


def _log(action: str, **fields: object) -> None:
    LOG_ROOT.mkdir(parents=True, exist_ok=True)
    row = {"ts": datetime.now(timezone.utc).isoformat(), "action": action, **fields}
    with ACCESS_LOG.open("a", encoding="utf-8") as f:
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
        if urlparse(self.path).path != "/action/clone":
            self._json(404, {})
            return
        length = int(self.headers.get("Content-Length", 0))
        body = json.loads((self.rfile.read(length) if length else b"{}").decode() or "{}")
        repo = body.get("repo", "corp/demo")
        count = int(body.get("count", 5 if body.get("anomaly") else 1))
        for i in range(count):
            subprocess.run(
                ["curl", "-sf", f"{GITEA_URL}/api/healthz"],
                capture_output=True,
                timeout=10,
            )
            _log("git_clone", repo=repo, iteration=i, bytes=body.get("bytes", 1_000_000))
        self._json(200, {"clones": count})

    def log_message(self, *_args) -> None:
        return


def main() -> None:
    _log("startup")
    HTTPServer(("0.0.0.0", 8080), Handler).serve_forever()


if __name__ == "__main__":
    main()
