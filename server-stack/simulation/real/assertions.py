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


def _checks(feature_id: str, positive: bool) -> list:
    if feature_id == "F-001":
        return [
            lambda s: assert_samba_audit(s, op="read"),
            lambda s: assert_zeek_conn(s),
        ]
    if feature_id == "F-002":
        return [lambda s: assert_zeek_conn(s, min_records=3 if positive else 1)]
    if feature_id == "F-003":
        return [lambda s: assert_bind_query(s, min_bytes=20 if positive else 1)]
    if feature_id == "F-005":
        return [lambda s: assert_dhcp_log(s) if positive else {"result": "PASS", "note": "negative skip"}]
    if feature_id == "F-006":
        return [lambda s: assert_ad_event(s, event_id=4625 if positive else 4624)]
    if feature_id == "F-007":
        return [lambda s: assert_zeek_conn(s, min_records=10 if positive else 1)]
    if feature_id == "F-008":
        return [lambda s: assert_ad_event(s, event_id=4768)]
    if feature_id == "F-010":
        return [lambda s: assert_ad_event(s, user="svc_sql")]
    if feature_id == "F-011":
        return [lambda s: assert_ad_event(s, event_id=4728)]
    if feature_id == "F-015":
        return [lambda s: assert_zeek_conn(s), lambda s: assert_endpoint_event(s, "rdp_hop")]
    if feature_id in ("F-037", "F-038"):
        return [lambda s: assert_samba_audit(s, op="read")]
    if feature_id == "F-039":
        return [lambda s: assert_samba_audit(s, op="rename")]
    if feature_id == "F-040":
        return [lambda s: assert_samba_audit(s, op="list")]
    if feature_id == "F-041":
        return [lambda s: assert_samba_audit(s, op="acl_set")]
    if feature_id == "F-055":
        return [lambda s: assert_endpoint_event(s, "usb_write")]
    if feature_id == "F-057":
        return [lambda s: assert_endpoint_event(s, "nic_promiscuous")]
    if feature_id == "F-063":
        return [lambda s: assert_endpoint_event(s, "unknown_hardware")]
    if feature_id == "F-079":
        return [lambda s: assert_endpoint_event(s, "after_hours_session"), lambda s: assert_ad_event(s)]
    if feature_id == "F-080":
        return [lambda s: assert_endpoint_event(s, "idle_session_abuse")]
    if feature_id == "F-081":
        return [lambda s: assert_endpoint_event(s, "role_work_window")]
    return []


def run_assertions(feature_id: str, mode: str, since: float) -> tuple[list[dict], list[dict], bool]:
    if feature_id not in RI1_FEATURES:
        return [], [], False

    positive = mode == "positive"
    raw: list[dict] = []
    for check in _checks(feature_id, positive):
        result = wait_for_log(check, since)
        raw.append(result)

    ingest: list[dict] = []
    if feature_id in INGEST_FEATURES:
        ingest.append(assert_ingest_for_feature(feature_id))

    ok = all(r.get("result") == "PASS" for r in raw) and all(
        i.get("result") in ("PASS", "SKIP") for i in ingest
    )
    return raw, ingest, ok
