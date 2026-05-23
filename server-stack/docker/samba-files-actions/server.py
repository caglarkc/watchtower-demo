#!/usr/bin/env python3
"""Samba file real actions — smbclient + full_audit style log lines."""

from __future__ import annotations

import json
import os
import shutil
import subprocess
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from urllib.parse import urlparse

LOG_DIR = Path(os.environ.get("LOG_ROOT", "/var/log/corp/samba"))
AUDIT_LOG = LOG_DIR / "audit.log"
SAMBA_HOST = os.environ.get("SAMBA_HOST", "corp-samba-files")
SAMBA_USER = os.environ.get("SAMBA_USER", "cfo")
SAMBA_PASS = os.environ.get("SAMBA_PASS", "Watchtower1!")
SEED_ROOT = Path(os.environ.get("SEED_ROOT", "/seeds"))


def _audit(user: str, op: str, path: str, **extra: object) -> None:
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    row = {
        "ts": datetime.now(timezone.utc).isoformat(),
        "user": user,
        "op": op,
        "path": path,
        "vfs": "full_audit",
        **extra,
    }
    with AUDIT_LOG.open("a", encoding="utf-8") as f:
        f.write(json.dumps(row) + "\n")


def _smb_url(share: str) -> str:
    return f"//{SAMBA_HOST}/{share}"


def _smb_ls(share: str, user: str | None = None) -> bool:
    u = user or SAMBA_USER
    cmd = [
        "smbclient",
        _smb_url(share),
        "-U",
        f"{u}%{SAMBA_PASS}",
        "-c",
        "ls",
    ]
    try:
        subprocess.run(cmd, capture_output=True, timeout=15, check=False)
        return True
    except (subprocess.TimeoutExpired, FileNotFoundError):
        return False


class Handler(BaseHTTPRequestHandler):
    def _json(self, code: int, body: dict) -> None:
        data = json.dumps(body).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def _body(self) -> dict:
        length = int(self.headers.get("Content-Length", 0))
        raw = self.rfile.read(length) if length else b"{}"
        return json.loads(raw.decode() or "{}")

    def do_GET(self) -> None:
        if self.path == "/health":
            self._json(200, {"status": "ok", "service": "samba-files-actions"})
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
            "/action/read-volume": self._read_volume,
            "/action/bulk-io": self._bulk_io,
            "/action/rename-storm": self._rename_storm,
            "/action/dir-traversal": self._dir_traversal,
            "/action/acl-change": self._acl_change,
            "/action/cross-dept-access": self._cross_dept,
            "/action/seed-files": self._seed_files,
        }
        fn = handlers.get(path)
        if not fn:
            self._json(404, {"error": "unknown action"})
            return
        self._json(200, fn(body))

    def _read_volume(self, body: dict) -> dict:
        user = body.get("user", "cfo")
        share = body.get("share", "Finance")
        bytes_read = int(body.get("bytes_read", 14_000_000_000))
        count = int(body.get("count", 3))
        _smb_ls(share, user)
        for i in range(count):
            _audit(user, "read", f"/share/{share.lower()}/bulk_{i}.dat", bytes=bytes_read // count)
        return {"events": count, "smb_attempted": True}

    def _bulk_io(self, body: dict) -> dict:
        user = body.get("user", "cfo")
        share = body.get("share", "Finance")
        read_b = int(body.get("read_bytes", 18_400_000_000))
        write_b = int(body.get("write_bytes", 0))
        _smb_ls(share, user)
        _audit(user, "read", f"/share/{share.lower()}/bulk_io", bytes=read_b)
        if write_b:
            _audit(user, "write", f"/share/{share.lower()}/bulk_io", bytes=write_b)
        return {"read_bytes": read_b, "write_bytes": write_b}

    def _rename_storm(self, body: dict) -> dict:
        user = body.get("user", "dev1")
        share = body.get("share", "Dev")
        count = int(body.get("count", 12))
        _smb_ls(share, user)
        for i in range(count):
            _audit(user, "rename", f"/share/{share.lower()}/file_{i}.txt", new_name=f"renamed_{i}.txt")
        return {"renames": count}

    def _dir_traversal(self, body: dict) -> dict:
        user = body.get("user", "legal1")
        paths = body.get("paths", ["/share/legal/confidential", "/share/hr/payroll"])
        for p in paths:
            _audit(user, "list", p, sensitive=True)
        return {"paths": len(paths)}

    def _acl_change(self, body: dict) -> dict:
        user = body.get("user", "admin")
        path = body.get("path", "/share/public")
        _audit(user, "acl_set", path, acl="Everyone:FULL")
        return {"acl": "Everyone:FULL"}

    def _cross_dept(self, body: dict) -> dict:
        user = body.get("user", "finance1")
        dept = body.get("department", "hr")
        _audit(user, "read", f"/share/{dept}/payroll.xlsx", cross_department=True)
        return {"cross_department": True}

    def _seed_files(self, body: dict) -> dict:
        copied = 0
        dest_root = Path("/mnt/share")
        if not dest_root.exists():
            return {"copied": 0, "note": "share mount optional"}
        for src_dir in SEED_ROOT.iterdir() if SEED_ROOT.exists() else []:
            if not src_dir.is_dir():
                continue
            target = dest_root / src_dir.name
            target.mkdir(parents=True, exist_ok=True)
            for f in src_dir.glob("*"):
                if f.is_file():
                    shutil.copy2(f, target / f.name)
                    copied += 1
        return {"copied": copied}

    def log_message(self, *_args) -> None:
        return


def main() -> None:
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    HTTPServer(("0.0.0.0", 8080), Handler).serve_forever()


if __name__ == "__main__":
    main()
