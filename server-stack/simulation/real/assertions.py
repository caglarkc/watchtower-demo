"""Post-action log + ingest assertions for RI-1 and RI-2 features."""

from __future__ import annotations

from config import ALL_REAL_FEATURES, INGEST_FEATURES, INGEST_L3_FEATURES, RI1_FEATURES, RI2_FEATURES, RI3_FEATURES, RI4_FEATURES
from ingest_assertions import assert_ingest_for_feature
from log_assertions import (
    assert_activity,
    assert_badge,
    assert_cups,
    assert_hris,
    assert_mattermost,
    assert_suitecrm,
    assert_ad_event,
    assert_ai_gateway,
    assert_app_audit,
    assert_bind_query,
    assert_cloud_upload,
    assert_dhcp_log,
    assert_dlp_health,
    assert_endpoint_event,
    assert_gitea_access,
    assert_mail_log,
    assert_nginx_access,
    assert_postgres_audit,
    assert_proxy_log,
    assert_samba_audit,
    assert_vault_audit,
    assert_wiki_access,
    assert_zeek_conn,
    wait_for_log,
)


def _checks_ri1(feature_id: str, positive: bool) -> list:
    if feature_id == "F-001":
        return [lambda s: assert_samba_audit(s, op="read"), lambda s: assert_zeek_conn(s)]
    if feature_id == "F-002":
        return [lambda s: assert_zeek_conn(s, min_records=3 if positive else 1)]
    if feature_id == "F-003":
        return [lambda s: assert_bind_query(s, min_bytes=20 if positive else 1)]
    if feature_id == "F-004":
        return [lambda s: assert_endpoint_event(s, "smb_downgrade")]
    if feature_id == "F-005":
        return [lambda s: assert_dhcp_log(s) if positive else {"result": "PASS", "note": "negative"}]
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


def _checks_ri2(feature_id: str, positive: bool) -> list:
    if feature_id in ("F-016", "F-019", "F-020", "F-021", "F-022", "F-023", "F-026", "F-027", "F-028"):
        return [lambda s: assert_mail_log("postfix", "smtp_send")]
    if feature_id == "F-017":
        return [lambda s: assert_mail_log("dovecot", "rule_change")]
    if feature_id in ("F-018", "F-024"):
        return [lambda s: assert_mail_log("dovecot", "imap_fetch")]
    if feature_id == "F-025":
        return [lambda s: assert_mail_log("roundcube", "contact_export")]
    if feature_id == "F-029":
        return [lambda s: assert_mail_log("roundcube", "webmail_login")]
    if feature_id == "F-045":
        return [lambda s: assert_postgres_audit(s)]
    if feature_id == "F-046":
        return [lambda s: assert_endpoint_event(s, "process_tree_anomaly")]
    if feature_id == "F-047":
        return [lambda s: assert_app_audit("internal-app", "api_pattern")]
    if feature_id == "F-048":
        return [lambda s: assert_nginx_access(s, "403" if positive else "404")]
    if feature_id == "F-049":
        return [lambda s: assert_gitea_access(s), lambda s: assert_app_audit("artifact", "artifact_download")]
    if feature_id == "F-050":
        return [lambda s: assert_app_audit("siem", "suppress_rule_change")]
    if feature_id == "F-051":
        return [lambda s: assert_app_audit("hypervisor", "console_access")]
    if feature_id == "F-052":
        return [lambda s: assert_endpoint_event(s, "scheduled_task_new")]
    if feature_id == "F-053":
        return [lambda s: assert_endpoint_event(s, "backup_disabled")]
    if feature_id == "F-054":
        return [lambda s: assert_endpoint_event(s, "encoded_script")]
    return []


def _checks_ri3(feature_id: str, positive: bool) -> list:
    if feature_id == "F-012":
        return [lambda s: assert_vault_audit(s), lambda s: assert_app_audit("internal-app", "api_pattern")]
    if feature_id == "F-013":
        return [lambda s: assert_vault_audit(s)]
    if feature_id in ("F-030", "F-031", "F-032", "F-035", "F-036"):
        return [lambda s: assert_ai_gateway(s, "prompt")]
    if feature_id == "F-033":
        return [lambda s: assert_proxy_log(s, "external_access")]
    if feature_id == "F-034":
        return [lambda s: assert_ai_gateway(s, "upload")]
    if feature_id in ("F-042", "F-043", "F-059", "F-060", "F-061", "F-065"):
        et = {
            "F-042": "local_sensitive_accumulation",
            "F-043": "labeled_file_move",
            "F-059": "clipboard_large_copy",
            "F-060": "screenshot_spike",
            "F-061": "role_server_map_deviation",
            "F-065": "dormant_system_access",
        }[feature_id]
        return [lambda s: assert_endpoint_event(s, et)]
    if feature_id == "F-044":
        return [lambda s: assert_wiki_access(s)]
    if feature_id == "F-058":
        return [lambda s: assert_dlp_health(s, disabled=positive)]
    if feature_id == "F-062":
        return [lambda s: assert_app_audit("siem", "risky_log_search")]
    if feature_id == "F-064":
        return [lambda s: assert_activity(s, "activity_burst")]
    if feature_id == "F-066":
        return [lambda s: assert_activity(s, "peer_group_deviation")]
    if feature_id == "F-067":
        return [lambda s: assert_cloud_upload(s), lambda s: assert_proxy_log(s, "cloud_upload")]
    if feature_id == "F-068":
        return [lambda s: assert_proxy_log(s, "first_seen_transfer")]
    if feature_id == "F-069":
        return [lambda s: assert_proxy_log(s, "encrypted_tunnel")]
    return []


def _checks_ri4(feature_id: str, positive: bool) -> list:
    if feature_id == "F-009":
        return [lambda s: assert_badge(s, "concurrent_session")]
    if feature_id == "F-014":
        return [lambda s: assert_hris(s, "credential_reset_burst"), lambda s: assert_ad_event(s)]
    if feature_id == "F-056":
        return [lambda s: assert_cups(s, "print_sensitive_correlation")]
    if feature_id == "F-070":
        return [lambda s: assert_badge(s, "badge_login_mismatch")]
    if feature_id == "F-071":
        return [lambda s: assert_mattermost(s, "composite_signal")]
    if feature_id == "F-072":
        return [lambda s: assert_hris(s, "offboarding_activity")]
    if feature_id == "F-073":
        return [lambda s: assert_suitecrm(s, "multi_user_record_chain")]
    if feature_id == "F-074":
        return [lambda s: assert_badge(s, "off_shift_access")]
    if feature_id == "F-075":
        return [lambda s: assert_hris(s, "new_hire_excess_access")]
    if feature_id == "F-076":
        return [lambda s: assert_hris(s, "old_entitlement_use")]
    if feature_id == "F-077":
        return [lambda s: assert_hris(s, "leave_activity")]
    if feature_id == "F-078":
        return [lambda s: assert_hris(s, "contractor_out_of_scope")]
    return []


def _resolve_checks(feature_id: str, positive: bool) -> list:
    if feature_id in RI1_FEATURES:
        return _checks_ri1(feature_id, positive)
    if feature_id in RI2_FEATURES:
        return _checks_ri2(feature_id, positive)
    if feature_id in RI3_FEATURES:
        return _checks_ri3(feature_id, positive)
    if feature_id in RI4_FEATURES:
        return _checks_ri4(feature_id, positive)
    return []


def run_assertions(feature_id: str, mode: str, since: float) -> tuple[list[dict], list[dict], bool]:
    if feature_id not in ALL_REAL_FEATURES:
        return [], [], False

    positive = mode == "positive"
    checks = _resolve_checks(feature_id, positive)
    raw: list[dict] = []
    for check in checks:
        result = check(since)
        if result.get("result") != "PASS":
            result = wait_for_log(check, since)
        raw.append(result)

    ingest: list[dict] = []
    if feature_id in INGEST_FEATURES:
        ing = assert_ingest_for_feature(feature_id)
        if feature_id in INGEST_L3_FEATURES and ing.get("result") == "PASS":
            ing["assertion"] = f"L3:elasticsearch:corp-logs:{feature_id}"
            ing["parity_level"] = "L3"
        ingest.append(ing)

    ok = all(r.get("result") == "PASS" for r in raw) and all(
        i.get("result") in ("PASS", "SKIP") for i in ingest
    )
    return raw, ingest, ok
