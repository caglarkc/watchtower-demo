#!/usr/bin/env python3
"""HRIS mock — DB-backed lifecycle audit (offboarding, leave, role-change)."""

from __future__ import annotations

import json
import os
import sqlite3
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from urllib.parse import urlparse

LOG_DIR = Path(os.environ.get("LOG_ROOT", "/var/log/corp/hris"))
DB_PATH = Path(os.environ.get("HRIS_DB", str(LOG_DIR / "hris.db")))
AUDIT = LOG_DIR / "hris.jsonl"


def _init_db() -> None:
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.executescript(
        """
        CREATE TABLE IF NOT EXISTS employees (
            emp_id TEXT PRIMARY KEY,
            display_name TEXT,
            status TEXT,
            role TEXT,
            on_leave INTEGER DEFAULT 0
        );
        CREATE TABLE IF NOT EXISTS lifecycle_events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            emp_id TEXT,
            event_type TEXT,
            payload TEXT,
            created_at TEXT
        );
        """
    )
    rows = [
        ("E001", "Alice CFO", "active", "finance", 0),
        ("E002", "Bob Dev", "active", "engineering", 0),
        ("E003", "Carol Leaver", "terminated", "finance", 0),
        ("E004", "Dan Contractor", "active", "contractor", 0),
        ("E005", "Eve Newhire", "active", "engineering", 0),
    ]
    for row in rows:
        conn.execute(
            "INSERT OR IGNORE INTO employees VALUES (?,?,?,?,?)",
            row,
        )
    conn.commit()
    conn.close()


def _log(body: dict) -> None:
    row = {"service": "hris_mock", "timestamp": datetime.now(timezone.utc).isoformat(), **body}
    with AUDIT.open("a", encoding="utf-8") as f:
        f.write(json.dumps(row, ensure_ascii=False) + "\n")


def _record_event(emp_id: str, event_type: str, payload: dict) -> None:
    conn = sqlite3.connect(DB_PATH)
    conn.execute(
        "INSERT INTO lifecycle_events (emp_id, event_type, payload, created_at) VALUES (?,?,?,?)",
        (emp_id, event_type, json.dumps(payload), datetime.now(timezone.utc).isoformat()),
    )
    conn.commit()
    conn.close()
    _log({"event_type": event_type, "emp_id": emp_id, **payload})


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
            self._json(200, {"status": "ok", "service": "hris_mock", "db": str(DB_PATH)})
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
            "/lifecycle": self._lifecycle_generic,
            "/action/credential-reset-burst": self._credential_reset_burst,
            "/action/offboarding-activity": self._offboarding_activity,
            "/action/new-hire-access": self._new_hire_access,
            "/action/role-change-entitlement": self._role_change_entitlement,
            "/action/leave-activity": self._leave_activity,
            "/action/contractor-scope": self._contractor_scope,
        }
        fn = handlers.get(path)
        if not fn:
            self._json(404, {"error": "unknown action"})
            return
        self._json(200, fn(body))

    def _lifecycle_generic(self, body: dict) -> dict:
        event_type = body.get("event_type", "lifecycle")
        _record_event(body.get("emp_id", "E001"), event_type, body)
        return {"recorded": True}

    def _credential_reset_burst(self, body: dict) -> dict:
        resets = int(body.get("resets", 12 if body.get("anomaly") else 1))
        unlocks = int(body.get("unlocks", 8 if body.get("anomaly") else 0))
        _record_event(
            "E001",
            "credential_reset_burst",
            {"resets": resets, "unlocks": unlocks, "anomaly": body.get("anomaly", False)},
        )
        return {"resets": resets, "unlocks": unlocks}

    def _offboarding_activity(self, body: dict) -> dict:
        logins = int(body.get("logins_after", 6 if body.get("anomaly") else 0))
        status = "terminated" if body.get("anomaly") else "active"
        conn = sqlite3.connect(DB_PATH)
        conn.execute("UPDATE employees SET status=? WHERE emp_id='E003'", (status,))
        conn.commit()
        conn.close()
        _record_event("E003", "offboarding_activity", {"status": status, "logins_after": logins, "anomaly": body.get("anomaly", False)})
        return {"status": status, "logins_after": logins}

    def _new_hire_access(self, body: dict) -> dict:
        systems = int(body.get("systems_accessed", 28 if body.get("anomaly") else 6))
        _record_event("E005", "new_hire_excess_access", {"day": body.get("day", 1), "systems_accessed": systems, "anomaly": body.get("anomaly", False)})
        return {"systems_accessed": systems}

    def _role_change_entitlement(self, body: dict) -> dict:
        used = bool(body.get("old_group_used", body.get("anomaly", False)))
        _record_event(
            "E002",
            "old_entitlement_use",
            {"role_changed": True, "old_group_used": used, "anomaly": body.get("anomaly", False)},
        )
        return {"old_group_used": used}

    def _leave_activity(self, body: dict) -> dict:
        events = int(body.get("keyboard_events", 900 if body.get("anomaly") else 0))
        conn = sqlite3.connect(DB_PATH)
        conn.execute("UPDATE employees SET on_leave=1 WHERE emp_id='E001'")
        conn.commit()
        conn.close()
        _record_event("E001", "leave_activity", {"on_leave": True, "keyboard_events": events, "anomaly": body.get("anomaly", False)})
        return {"keyboard_events": events}

    def _contractor_scope(self, body: dict) -> dict:
        systems = body.get("systems", ["payroll-db", "dc-admin"] if body.get("anomaly") else ["dev-git"])
        _record_event("E004", "contractor_out_of_scope", {"identity": "contractor", "systems": systems, "anomaly": body.get("anomaly", False)})
        return {"systems": systems}

    def log_message(self, *_args) -> None:
        return


def main() -> None:
    _init_db()
    _log({"event_type": "startup"})
    HTTPServer(("0.0.0.0", 8080), Handler).serve_forever()


if __name__ == "__main__":
    main()
