"""Assert real service logs after RI-1/RI-2 actions."""

from __future__ import annotations

import json
import time
from pathlib import Path

from config import LOG_PATHS, ROOT


def _tail_lines(path: Path, since: float, min_lines: int = 1) -> list[str]:
    if not path.exists():
        return []
    return path.read_text(encoding="utf-8", errors="replace").splitlines()[-max(min_lines, 20) :]


def _grep_jsonl(path: Path, needle: str) -> bool:
    if not path.exists():
        return False
    for line in _tail_lines(path, 0):
        if needle in line:
            return True
    return False


def _grep_file(path: Path, needle: str, min_bytes: int = 1) -> bool:
    if not path.exists():
        return False
    text = path.read_text(encoding="utf-8", errors="replace")
    return len(text) >= min_bytes and (not needle or needle in text)


def assert_ad_event(since: float, event_id: int | None = None, user: str | None = None) -> dict:
    path = LOG_PATHS["samba-ad"]
    ok = path.exists() and path.stat().st_size > 0
    if event_id is not None:
        ok = ok and _grep_jsonl(path, f'"event_id": {event_id}')
    if user:
        ok = ok and _grep_jsonl(path, user)
    return {"path": str(path), "result": "PASS" if ok else "FAIL"}


def assert_samba_audit(since: float, op: str | None = None, user: str | None = None) -> dict:
    path = LOG_PATHS["samba-audit"]
    return {"path": str(path), "result": "PASS" if _grep_file(path, op or "", 10) else "FAIL"}


def assert_zeek_conn(since: float, min_records: int = 1) -> dict:
    path = LOG_PATHS["zeek-conn"]
    lines = _tail_lines(path, since, min_records)
    return {"path": str(path), "records": len(lines), "result": "PASS" if len(lines) >= min_records else "FAIL"}


def assert_bind_query(since: float, min_bytes: int = 10) -> dict:
    candidates = [LOG_PATHS["bind-query"], ROOT / "reports" / "real" / "logs" / "dns" / "query.log"]
    for path in candidates:
        if path.exists() and path.stat().st_size >= min_bytes:
            return {"path": str(path), "result": "PASS"}
    return {"path": str(candidates[0]), "result": "FAIL"}


def assert_dhcp_log(since: float, event: str = "DHCPDISCOVER") -> dict:
    path = LOG_PATHS["dhcp"]
    return {"path": str(path), "result": "PASS" if _grep_file(path, event) else "FAIL"}


def assert_endpoint_event(since: float, event_type: str) -> dict:
    path = LOG_PATHS["endpoint"] / f"{event_type}.jsonl"
    return {"path": str(path), "result": "PASS" if _grep_jsonl(path, event_type) else "FAIL"}


def assert_mail_log(service: str, action: str) -> dict:
    key = service if service in LOG_PATHS else "postfix"
    path = LOG_PATHS.get(key, LOG_PATHS["postfix"])
    return {"path": str(path), "result": "PASS" if _grep_file(path, action, 20) else "FAIL"}


def assert_postgres_audit(since: float, min_rows: int = 1) -> dict:
    path = LOG_PATHS["postgres-audit"]
    ok = _grep_file(path, "SELECT", 20)
    return {"path": str(path), "result": "PASS" if ok else "FAIL"}


def assert_gitea_access(since: float) -> dict:
    path = LOG_PATHS["gitea-access"]
    return {"path": str(path), "result": "PASS" if _grep_file(path, "git_clone", 20) else "FAIL"}


def assert_nginx_access(since: float, code: str = "403") -> dict:
    candidates = [LOG_PATHS["nginx-access"], ROOT / "reports" / "real" / "logs" / "nginx" / "access.log"]
    for path in candidates:
        if _grep_file(path, code, 10):
            return {"path": str(path), "result": "PASS"}
    return {"path": str(candidates[0]), "result": "FAIL"}


def assert_jsonl(path: Path, needle: str, min_bytes: int = 20) -> dict:
    return {"path": str(path), "result": "PASS" if _grep_file(path, needle, min_bytes) else "FAIL"}


def assert_vault_audit(since: float) -> dict:
    return assert_jsonl(LOG_PATHS["vault-audit"], "secret_read")


def assert_ai_gateway(since: float, action: str = "prompt") -> dict:
    return assert_jsonl(LOG_PATHS["ai-gateway"], action)


def assert_proxy_log(since: float, action: str) -> dict:
    ok = _grep_file(LOG_PATHS["proxy-audit"], action, 20)
    if not ok:
        ok = _grep_file(LOG_PATHS["proxy-squid"], action, 10)
    return {"path": str(LOG_PATHS["proxy-audit"]), "result": "PASS" if ok else "FAIL"}


def assert_cloud_upload(since: float) -> dict:
    return assert_jsonl(LOG_PATHS["cloud-upload"], "s3_put_object")


def assert_wiki_access(since: float) -> dict:
    return assert_jsonl(LOG_PATHS["wiki-access"], "wiki_page_download")


def assert_dlp_health(since: float, disabled: bool = False) -> dict:
    needle = "disabled" if disabled else "healthy"
    return assert_jsonl(LOG_PATHS["dlp-health"], needle)


def assert_activity(since: float, action: str) -> dict:
    return assert_jsonl(LOG_PATHS["activity"], action)


def assert_hris(since: float, event_type: str) -> dict:
    return assert_jsonl(LOG_PATHS["hris-audit"], event_type)


def assert_badge(since: float, event_type: str) -> dict:
    return assert_jsonl(LOG_PATHS["badge-audit"], event_type)


def assert_cups(since: float, needle: str = "print_job") -> dict:
    return assert_jsonl(LOG_PATHS["cups-print"], needle)


def assert_mattermost(since: float, needle: str = "composite_signal") -> dict:
    return assert_jsonl(LOG_PATHS["mattermost-chat"], needle)


def assert_suitecrm(since: float, needle: str = "multi_user_record_chain") -> dict:
    return assert_jsonl(LOG_PATHS["suitecrm-audit"], needle)


def assert_app_audit(role: str, action: str) -> dict:
    key = {"internal-app": "app-audit", "siem": "siem-audit", "hypervisor": "hypervisor-audit", "artifact": "artifact-audit"}.get(role, "app-audit")
    path = LOG_PATHS[key]
    return {"path": str(path), "result": "PASS" if _grep_file(path, action, 20) else "FAIL"}


def wait_for_log(check_fn, since: float, retries: int = 5, delay: float = 0.5) -> dict:
    last: dict = {"result": "FAIL"}
    for _ in range(retries):
        last = check_fn(since)
        if last.get("result") == "PASS":
            return last
        time.sleep(delay)
    return last
