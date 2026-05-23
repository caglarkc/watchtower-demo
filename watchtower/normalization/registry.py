"""Event-type to feature_id registry (81 Watchtower features)."""

from __future__ import annotations

# Built from server-stack/simulation/feature_replays/*_positive.yaml
EVENT_TYPE_TO_FEATURE: dict[str, str] = {
    "smb_read_volume": "F-001",
    "east_west_flow": "F-002",
    "dns_entropy": "F-003",
    "smb_downgrade": "F-004",
    "dhcp_anomaly": "F-005",
    "ad_auth": "F-006",
    "port_scan": "F-007",
    "kerberos_tgt": "F-008",
    "concurrent_session": "F-009",
    "service_interactive": "F-010",
    "ad_group_change": "F-011",
    "api_key_usage": "F-012",
    "vault_read_burst": "F-013",
    "credential_reset_burst": "F-014",
    "rdp_hop": "F-015",
    "mail_send_volume": "F-016",
    "mail_rule_change": "F-017",
    "imap_mailbox_access": "F-018",
    "mail_attachment_entropy": "F-019",
    "mail_bcc_anomaly": "F-020",
    "mail_personal_domain": "F-021",
    "mail_external_competitor": "F-022",
    "mail_sensitive_keyword": "F-023",
    "imap_archive_bulk_read": "F-024",
    "address_book_export": "F-025",
    "mail_style_deviation": "F-026",
    "mail_banned_phrase": "F-027",
    "mail_first_external_sensitive": "F-028",
    "webmail_login_attempt": "F-029",
    "ai_confidential_prompt": "F-030",
    "ai_source_code_paste": "F-031",
    "ai_internal_info_prompt": "F-032",
    "unapproved_ai_domain": "F-033",
    "ai_file_upload": "F-034",
    "ai_procedure_discovery": "F-035",
    "ai_strategy_content": "F-036",
    "smb_access": "F-037",
    "smb_bulk_io": "F-038",
    "smb_rename_storm": "F-039",
    "directory_traversal": "F-040",
    "acl_change": "F-041",
    "local_sensitive_accumulation": "F-042",
    "sensitive_file_move": "F-043",
    "wiki_bulk_download": "F-044",
    "postgres_bulk_select": "F-045",
    "process_tree_anomaly": "F-046",
    "api_pattern_deviation": "F-047",
    "http_4xx_spike": "F-048",
    "git_clone_volume": "F-049",
    "siem_suppress_rule": "F-050",
    "hypervisor_console_access": "F-051",
    "scheduled_task_created": "F-052",
    "backup_shadow_delete": "F-053",
    "encoded_powershell": "F-054",
    "usb_write": "F-055",
    "print_sensitive_correlation": "F-056",
    "nic_promiscuous": "F-057",
    "dlp_bypass": "F-058",
    "clipboard_large_copy": "F-059",
    "screenshot_spike": "F-060",
    "role_server_map_deviation": "F-061",
    "risky_log_search": "F-062",
    "unknown_hardware": "F-063",
    "activity_burst": "F-064",
    "dormant_system_access": "F-065",
    "peer_group_deviation": "F-066",
    "personal_cloud_upload": "F-067",
    "first_external_transfer": "F-068",
    "proxy_tunnel": "F-069",
    "badge_login_mismatch": "F-070",
    "composite_signal": "F-071",
    "offboarding_activity": "F-072",
    "multi_user_file_chain": "F-073",
    "off_shift_access": "F-074",
    "new_hire_excess_access": "F-075",
    "old_entitlement_use": "F-076",
    "leave_activity": "F-077",
    "contractor_out_of_scope": "F-078",
    "after_hours_session": "F-079",
    "idle_session_abuse": "F-080",
    "role_work_window": "F-081",
    # Windows security event_id shortcuts (corp AD logs)
    "4624": "F-008",
    "4625": "F-006",
    "4728": "F-011",
    "4729": "F-011",
    "4732": "F-011",
}

# Metadata-only; normalized but not promoted to graph candidates
NON_CANDIDATE_EVENT_TYPES: frozenset[str] = frozenset({"scenario_anchor"})


def resolve_feature_hint(
    payload: dict,
    *,
    context_feature_id: str | None = None,
) -> str | None:
    if context_feature_id:
        return context_feature_id
    if payload.get("source_feature"):
        return str(payload["source_feature"])
    event_type = payload.get("event_type") or payload.get("detection_type")
    if event_type is None and payload.get("event_id") is not None:
        event_type = str(payload["event_id"])
    if event_type is None:
        return None
    key = str(event_type)
    return EVENT_TYPE_TO_FEATURE.get(key)
