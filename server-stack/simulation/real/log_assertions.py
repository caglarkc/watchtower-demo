"""Assert real service logs after RI-1 actions."""

from __future__ import annotations

import json
import time
from pathlib import Path

from config import LOG_PATHS


def _tail_lines(path: Path, since: float, min_lines: int = 1) -> list[str]:
    if not path.exists():
        return []
    lines: list[str] = []
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        lines.append(line)
    return lines[-max(min_lines, 20) :]


def _grep_jsonl(path: Path, needle: str, since: float) -> bool:
    for line in _tail_lines(path, since):
        if needle in line:
            try:
                row = json.loads(line)
                if row:
                    return True
            except json.JSONDecodeError:
                return True
    return False


def assert_ad_event(since: float, event_id: int | None = None, user: str | None = None) -> dict:
    path = LOG_PATHS["samba-ad"]
    ok = path.exists() and path.stat().st_size > 0
    if event_id is not None:
        ok = ok and _grep_jsonl(path, f'"event_id": {event_id}', since)
    if user:
        ok = ok and _grep_jsonl(path, f'"{user}"', since)
    return {"path": str(path), "result": "PASS" if ok else "FAIL"}


def assert_samba_audit(since: float, op: str | None = None, user: str | None = None) -> dict:
    path = LOG_PATHS["samba-audit"]
    text = path.read_text(encoding="utf-8", errors="replace") if path.exists() else ""
    ok = len(text) > 0
    if op:
        ok = ok and op in text
    if user:
        ok = ok and user in text
    return {"path": str(path), "result": "PASS" if ok else "FAIL"}


def assert_zeek_conn(since: float, min_records: int = 1) -> dict:
    path = LOG_PATHS["zeek-conn"]
    lines = _tail_lines(path, since, min_records)
    ok = len(lines) >= min_records
    return {"path": str(path), "records": len(lines), "result": "PASS" if ok else "FAIL"}


def assert_bind_query(since: float, min_bytes: int = 10) -> dict:
    path = LOG_PATHS["bind-query"]
    ok = path.exists() and path.stat().st_size >= min_bytes
    return {"path": str(path), "result": "PASS" if ok else "FAIL"}


def assert_dhcp_log(since: float, event: str = "DHCPDISCOVER") -> dict:
    path = LOG_PATHS["dhcp"]
    text = path.read_text(encoding="utf-8", errors="replace") if path.exists() else ""
    ok = event in text
    return {"path": str(path), "result": "PASS" if ok else "FAIL"}


def assert_endpoint_event(since: float, event_type: str) -> dict:
    path = LOG_PATHS["endpoint"] / f"{event_type}.jsonl"
    ok = _grep_jsonl(path, event_type, since) if path.exists() else False
    return {"path": str(path), "result": "PASS" if ok else "FAIL"}


def wait_for_log(check_fn, since: float, retries: int = 5, delay: float = 0.5) -> dict:
    last: dict = {"result": "FAIL"}
    for _ in range(retries):
        last = check_fn(since)
        if last.get("result") == "PASS":
            return last
        time.sleep(delay)
    return last
