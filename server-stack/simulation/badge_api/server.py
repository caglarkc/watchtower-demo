#!/usr/bin/env python3
"""Badge API — DB-backed physical access audit."""

from __future__ import annotations

import json
import os
import sqlite3
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from urllib.parse import urlparse

LOG_DIR = Path(os.environ.get("LOG_ROOT", "/var/log/corp/badge"))
DB_PATH = Path(os.environ.get("BADGE_DB", str(LOG_DIR / "badge.db")))
AUDIT = LOG_DIR / "badge.jsonl"


def _init_db() -> None:
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.executescript(
        """
        CREATE TABLE IF NOT EXISTS badges (
            badge_id TEXT PRIMARY KEY,
            emp_id TEXT,
            shift TEXT
        );
        CREATE TABLE IF NOT EXISTS swipes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            badge_id TEXT,
            location TEXT,
            event_type TEXT,
            payload TEXT,
            created_at TEXT
        );
        """
    )
    for bid, emp, shift in [("B001", "E001", "day"), ("B002", "E002", "day"), ("B003", "E003", "off")]:
        conn.execute("INSERT OR IGNORE INTO badges VALUES (?,?,?)", (bid, emp, shift))
    conn.commit()
    conn.close()


def _log(body: dict) -> None:
    row = {"service": "badge_api", "timestamp": datetime.now(timezone.utc).isoformat(), **body}
    with AUDIT.open("a", encoding="utf-8") as f:
        f.write(json.dumps(row, ensure_ascii=False) + "\n")


def _record_swipe(badge_id: str, event_type: str, payload: dict) -> None:
    conn = sqlite3.connect(DB_PATH)
    conn.execute(
        "INSERT INTO swipes (badge_id, location, event_type, payload, created_at) VALUES (?,?,?,?,?)",
        (
            badge_id,
            payload.get("location", "lobby"),
            event_type,
            json.dumps(payload),
            datetime.now(timezone.utc).isoformat(),
        ),
    )
    conn.commit()
    conn.close()
    _log({"event_type": event_type, "badge_id": badge_id, **payload})


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
            self._json(200, {"status": "ok", "service": "badge_api", "db": str(DB_PATH)})
            return
        self._json(404, {"error": "not found"})

    def do_POST(self) -> None:
        path = urlparse(self.path).path
        try:
            body = self._body()
        except json.JSONDecodeError:
            self._json(400, {"error": "invalid json"})
            return
        if path == "/swipe":
            _record_swipe(body.get("badge_id", "B001"), body.get("event_type", "swipe"), body)
            self._json(200, {"recorded": True})
            return
        handlers = {
            "/action/concurrent-session": self._concurrent_session,
            "/action/badge-login-mismatch": self._badge_login_mismatch,
            "/action/off-shift-access": self._off_shift_access,
        }
        fn = handlers.get(path)
        if not fn:
            self._json(404, {"error": "unknown action"})
            return
        self._json(200, fn(body))

    def _concurrent_session(self, body: dict) -> dict:
        locations = body.get("locations", ["floor-3", "floor-b1"] if body.get("anomaly") else ["floor-3"])
        for loc in locations:
            _record_swipe("B001", "concurrent_session", {"location": loc, "minutes_apart": body.get("minutes_apart", 12), "anomaly": body.get("anomaly", False)})
        return {"locations": locations}

    def _badge_login_mismatch(self, body: dict) -> dict:
        present = bool(body.get("badge_present", not body.get("anomaly", True)))
        login_ok = bool(body.get("login_success", True))
        _record_swipe(
            "B001",
            "badge_login_mismatch",
            {"badge_present": present, "login_success": login_ok, "anomaly": body.get("anomaly", False)},
        )
        return {"mismatch": (not present) and login_ok}

    def _off_shift_access(self, body: dict) -> dict:
        shift = body.get("shift", "off" if body.get("anomaly") else "day")
        _record_swipe(
            "B003",
            "off_shift_access",
            {"shift": shift, "login_hour": body.get("login_hour", 2 if body.get("anomaly") else 10), "badge_swipe": True, "anomaly": body.get("anomaly", False)},
        )
        return {"shift": shift}

    def log_message(self, *_args) -> None:
        return


def main() -> None:
    _init_db()
    _log({"event_type": "startup"})
    HTTPServer(("0.0.0.0", 8080), Handler).serve_forever()


if __name__ == "__main__":
    main()
