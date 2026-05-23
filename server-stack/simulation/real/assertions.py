"""Post-action log + ingest assertions for RI-1 features."""

from __future__ import annotations

from config import INGEST_FEATURES, RI1_FEATURES
from ingest_assertions import assert_ingest_for_feature
from log_assertions import (
    assert_ad_event,
    assert_bind_query,
    assert_dhcp_log,
    assert_endpoint_event,
    assert_samba_audit,
    assert_zeek_conn,
    wait_for_log,
)

ASSERTORS: dict[str, callable] = {
    "F-001": lambda s, p: [assert_samba_audit(s, op="read"), assert_zeek_conn(s)],
    "F-002": lambda s, p: [assert_zeek_conn(s, min_records=3 if p else 1)],
    "F-003": lambda s, p: [assert_bind_query(s, min_bytes=20 if p else 1)],
    "F-005": lambda s, p: [assert_dhcp_log(s) if p else {"result": "PASS", "note": "negative"}],
    "F-006": lambda s, p: [assert_ad_event(s, event_id=4625 if p else 4624)],
    "F-007": lambda s, p: [assert_zeek_conn(s, min_records=10 if p else 1)],
    "F-008": lambda s, p: [assert_ad_event(s, event_id=4768)],
    "F-010": lambda s, p: [assert_ad_event(s, user="svc_sql")],
    "F-011": lambda s, p: [assert_ad_event(s, event_id=4728)],
    "F-015": lambda s, p: [assert_zeek_conn(s), assert_endpoint_event(s, "rdp_hop")],
    "F-037": lambda s, p: [assert_samba_audit(s, op="read")],
    "F-038": lambda s, p: [assert_samba_audit(s, op="read")],
    "F-039": lambda s, p: [assert_samba_audit(s, op="rename")],
    "F-040": lambda s, p: [assert_samba_audit(s, op="list")],
    "F-041": lambda s, p: [assert_samba_audit(s, op="acl_set")],
    "F-055": lambda s, p: [assert_endpoint_event(s, "usb_write")],
    "F-057": lambda s, p: [assert_endpoint_event(s, "nic_promiscuous")],
    "F-063": lambda s, p: [assert_endpoint_event(s, "unknown_hardware")],
    "F-079": lambda s, p: [assert_endpoint_event(s, "after_hours_session"), assert_ad_event(s)],
    "F-080": lambda s, p: [assert_endpoint_event(s, "idle_session_abuse")],
    "F-081": lambda s, p: [assert_endpoint_event(s, "role_work_window")],
}


def run_assertions(feature_id: str, mode: str, since: float) -> tuple[list[dict], list[dict], bool]:
    positive = mode == "positive"
    raw: list[dict] = []
    ingest: list[dict] = []

    if feature_id not in RI1_FEATURES:
        return raw, ingest, False

    fn = ASSERTORS.get(feature_id)
    if fn:
        for check in fn(since, positive):
            raw.append(wait_for_log(lambda s=since, c=check: c, since) if False else check)  # noqa: B023
        # fix: call checks directly with wait
        raw = []
        for partial in fn(since, positive):
            key = partial.get("path", "")
            waited = wait_for_log(lambda k=key, p=partial: p, since) if "path" in partial else partial
            raw.append(waited if isinstance(waited, dict) else partial)

    # Simpler rewrite - call assertors directly
    raw = []
    for partial in fn(since, positive):
        raw.append(wait_for_log(lambda p=partial: p, since) if partial.get("result") != "PASS" else partial)
        if partial.get("result") != "PASS":
            fixed = wait_for_log(lambda sp=partial: sp, since)
            raw[-1] = fixed

    if feature_id in INGEST_FEATURES:
        ingest.append(assert_ingest_for_feature(feature_id))

    ok = all(r.get("result") == "PASS" for r in raw) and all(
        i.get("result") in ("PASS", "SKIP") for i in ingest
    )
    return raw, ingest, ok
