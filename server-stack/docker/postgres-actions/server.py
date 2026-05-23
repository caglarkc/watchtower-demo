#!/usr/bin/env python3
"""PostgreSQL real actions + pg_audit-style log writer."""

from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from urllib.parse import urlparse

import psycopg2

LOG_ROOT = Path(os.environ.get("LOG_ROOT", "/var/log/corp/postgres"))
AUDIT_LOG = LOG_ROOT / "pg_audit.log"

PG = {
    "host": os.environ.get("PGHOST", "corp-postgres"),
    "user": os.environ.get("PGUSER", "corp"),
    "password": os.environ.get("PGPASSWORD", "Watchtower1!"),
    "dbname": os.environ.get("PGDATABASE", "corpdb"),
}


def _audit(statement: str, rows: int, anomaly: bool) -> None:
    LOG_ROOT.mkdir(parents=True, exist_ok=True)
    row = {
        "ts": datetime.now(timezone.utc).isoformat(),
        "user": PG["user"],
        "database": PG["dbname"],
        "statement": statement,
        "rows": rows,
        "anomaly": anomaly,
    }
    with AUDIT_LOG.open("a", encoding="utf-8") as f:
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
        if urlparse(self.path).path != "/action/bulk-select":
            self._json(404, {})
            return
        length = int(self.headers.get("Content-Length", 0))
        body = json.loads((self.rfile.read(length) if length else b"{}").decode() or "{}")
        limit = int(body.get("limit", 10 if body.get("anomaly") else 2))
        sql = f"SELECT * FROM customers LIMIT {limit}"
        try:
            with psycopg2.connect(**PG) as conn:
                with conn.cursor() as cur:
                    cur.execute(sql)
                    rows = cur.fetchall()
            _audit(sql, len(rows), bool(body.get("anomaly")))
            self._json(200, {"rows": len(rows), "sql": sql})
        except Exception as exc:
            self._json(500, {"error": str(exc)})

    def log_message(self, *_args) -> None:
        return


def main() -> None:
    _audit("SELECT 1", 1, False)
    HTTPServer(("0.0.0.0", 8080), Handler).serve_forever()


if __name__ == "__main__":
    main()
