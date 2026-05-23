#!/usr/bin/env python3
"""Postfix / Dovecot / Roundcube real-action log emitter (ROLE env selects channel)."""

from __future__ import annotations

import json
import os
import threading
import time
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from urllib.parse import urlparse

ROLE = os.environ.get("ROLE", "postfix")
LOG_ROOT = Path(os.environ.get("LOG_ROOT", f"/var/log/corp/{ROLE}"))
LOG_FILE = LOG_ROOT / f"{ROLE}.jsonl"


def _write(row: dict) -> None:
    LOG_ROOT.mkdir(parents=True, exist_ok=True)
    row.setdefault("timestamp", datetime.now(timezone.utc).isoformat())
    row.setdefault("service", ROLE)
    with LOG_FILE.open("a", encoding="utf-8") as f:
        f.write(json.dumps(row, ensure_ascii=False) + "\n")


def _baseline() -> None:
    _write({"action": "baseline", "status": "ok"})


class Handler(BaseHTTPRequestHandler):
    def _json(self, code: int, body: dict) -> None:
        data = json.dumps(body).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(data)

    def _body(self) -> dict:
        length = int(self.headers.get("Content-Length", 0))
        raw = self.rfile.read(length) if length else b"{}"
        return json.loads(raw.decode() or "{}")

    def do_GET(self) -> None:
        if self.path == "/health":
            self._json(200, {"status": "ok", "role": ROLE})
            return
        self._json(404, {"error": "not found"})

    def do_POST(self) -> None:
        path = urlparse(self.path).path
        try:
            body = self._body()
        except json.JSONDecodeError:
            self._json(400, {"error": "invalid json"})
            return

        handlers = {
            "/action/smtp-send": self._smtp_send,
            "/action/imap-fetch": self._imap_fetch,
            "/action/rule-change": self._rule_change,
            "/action/webmail-login": self._webmail_login,
            "/action/contact-export": self._contact_export,
            "/emit": self._emit_generic,
        }
        fn = handlers.get(path)
        if not fn:
            self._json(404, {"error": "unknown action"})
            return
        self._json(200, fn(body))

    def _smtp_send(self, body: dict) -> dict:
        _write(
            {
                "action": "smtp_send",
                "from": body.get("from", "user@corp.local"),
                "to": body.get("to", []),
                "bcc": body.get("bcc", []),
                "size_bytes": body.get("size_bytes", 1024),
                "attachment_entropy": body.get("attachment_entropy"),
                "keywords": body.get("keywords", []),
                "external_domain": body.get("external_domain"),
                "anomaly": body.get("anomaly", False),
            }
        )
        return {"written": str(LOG_FILE)}

    def _imap_fetch(self, body: dict) -> dict:
        _write(
            {
                "action": "imap_fetch",
                "user": body.get("user", "user@corp.local"),
                "mailbox": body.get("mailbox", "INBOX"),
                "messages": body.get("messages", 1),
                "out_of_mailbox": body.get("out_of_mailbox", False),
                "archive_bulk": body.get("archive_bulk", False),
                "anomaly": body.get("anomaly", False),
            }
        )
        return {"written": str(LOG_FILE)}

    def _rule_change(self, body: dict) -> dict:
        _write(
            {
                "action": "rule_change",
                "user": body.get("user"),
                "rule_type": body.get("rule_type", "forward"),
                "anomaly": body.get("anomaly", False),
            }
        )
        return {"written": str(LOG_FILE)}

    def _webmail_login(self, body: dict) -> dict:
        _write(
            {
                "action": "webmail_login",
                "user": body.get("user"),
                "source_ip": body.get("source_ip", "172.28.0.100"),
                "success": body.get("success", True),
                "anomaly": body.get("anomaly", False),
            }
        )
        return {"written": str(LOG_FILE)}

    def _contact_export(self, body: dict) -> dict:
        _write(
            {
                "action": "contact_export",
                "user": body.get("user"),
                "records": body.get("records", 0),
                "anomaly": body.get("anomaly", False),
            }
        )
        return {"written": str(LOG_FILE)}

    def _emit_generic(self, body: dict) -> dict:
        _write(body)
        return {"written": str(LOG_FILE)}

    def log_message(self, *_args) -> None:
        return


def main() -> None:
    _baseline()

    def loop() -> None:
        while True:
            _baseline()
            time.sleep(45)

    threading.Thread(target=loop, daemon=True).start()
    HTTPServer(("0.0.0.0", 8080), Handler).serve_forever()


if __name__ == "__main__":
    main()
