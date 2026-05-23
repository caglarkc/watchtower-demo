#!/usr/bin/env python3
"""Samba AD simulation — real-action API + Windows-style identity logs."""

from __future__ import annotations

import json
import os
import threading
import time
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from urllib.parse import urlparse

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
    def _json(self, code: int, body: dict) -> None:
        data = json.dumps(body).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def _read_body(self) -> dict:
        length = int(self.headers.get("Content-Length", 0))
        raw = self.rfile.read(length) if length else b"{}"
        return json.loads(raw.decode() or "{}")

    def do_GET(self) -> None:
        if self.path == "/health":
            self._json(200, {"status": "ok", "service": "samba-ad-sim"})
            return
        self._json(404, {"error": "not found"})

    def do_POST(self) -> None:
        path = urlparse(self.path).path
        try:
            body = self._read_body()
        except json.JSONDecodeError:
            self._json(400, {"error": "invalid json"})
            return

        actions = {
            "/action/auth-fail-burst": self._auth_fail_burst,
            "/action/auth-success": self._auth_success,
            "/action/kerberos-diversity": self._kerberos_diversity,
            "/action/service-account-interactive": self._service_account_interactive,
            "/action/group-change": self._group_change,
            "/action/credential-reset-burst": self._credential_reset_burst,
        }
        handler = actions.get(path)
        if not handler:
            self._json(404, {"error": "unknown action"})
            return
        result = handler(body)
        self._json(200, result)

    def _auth_fail_burst(self, body: dict) -> dict:
        user = body.get("user", "attacker")
        count = int(body.get("count", 8))
        for _ in range(count):
            _emit(4625, user=user, logon_type=3, result="failure")
        _emit(4624, user=user, logon_type=3, result="success")
        return {"events": count + 1, "pattern": "4625_burst_then_4624"}

    def _auth_success(self, body: dict) -> dict:
        user = body.get("user", "cfo")
        _emit(4624, user=user, logon_type=int(body.get("logon_type", 2)), result="success")
        return {"events": 1}

    def _kerberos_diversity(self, body: dict) -> dict:
        user = body.get("user", "svc_sql")
        targets = body.get("targets", ["dc1", "files1", "sql1", "app1"])
        for tgt in targets:
            _emit(4768, user=user, service=tgt, ticket_type="TGT")
        return {"events": len(targets)}

    def _service_account_interactive(self, body: dict) -> dict:
        user = body.get("user", "svc_sql")
        _emit(4624, user=user, logon_type=2, interactive=True, result="success")
        return {"events": 1, "anomaly": "service_account_interactive"}

    def _group_change(self, body: dict) -> dict:
        user = body.get("user", "admin")
        group = body.get("group", "Domain Admins")
        action = body.get("action", "add")
        _emit(4728, user=user, group=group, member=body.get("member", "contractor1"), action=action)
        return {"events": 1}

    def _credential_reset_burst(self, body: dict) -> dict:
        actor = body.get("actor", "helpdesk")
        target = body.get("target", "user42")
        for _ in range(int(body.get("count", 5))):
            _emit(4724, actor=actor, target=target, action="password_reset")
        return {"events": int(body.get("count", 5))}

    def log_message(self, *_args) -> None:
        return


def main() -> None:
    threading.Thread(target=_baseline_loop, daemon=True).start()
    HTTPServer(("0.0.0.0", 8080), Handler).serve_forever()


if __name__ == "__main__":
    main()
