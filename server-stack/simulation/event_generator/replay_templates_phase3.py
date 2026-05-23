"""Phase 3 feature replay event templates."""

from __future__ import annotations

PHASE3_LOG_CHANNELS = {
    "ai_gateway": "ai_gateway",
    "proxy": "proxy",
    "cloud": "cloud",
    "vault": "vault",
    "mattermost": "mattermost",
    "cups": "cups",
    "badge": "badge",
    "hris": "hris",
    "wiki": "wiki",
    "suitecrm": "suitecrm",
    "dlp": "dlp",
    "activity": "activity",
    "endpoint": "endpoint",
    "app": "app",
    "siem": "siem",
}

# Extend channel dirs for run_feature
PHASE3_CHANNEL_DIRS: dict[str, str] = PHASE3_LOG_CHANNELS

PHASE3_TEMPLATES: dict[str, tuple[list[dict], list[dict]]] = {
    "F-009": (
        [{"event_type": "concurrent_session", "log_channel": "badge", "locations": ["floor-3", "floor-b1"], "minutes_apart": 12}],
        [{"event_type": "concurrent_session", "log_channel": "badge", "locations": ["floor-3"], "minutes_apart": 0}],
    ),
    "F-012": (
        [{"event_type": "api_key_usage", "log_channel": "app", "key_id": "svc-deploy", "source_ips": 3}],
        [{"event_type": "api_key_usage", "log_channel": "app", "key_id": "svc-deploy", "source_ips": 1}],
    ),
    "F-013": (
        [{"event_type": "vault_read_burst", "log_channel": "vault", "reads": 200, "window_minutes": 60}],
        [{"event_type": "vault_read_burst", "log_channel": "vault", "reads": 5, "window_minutes": 60}],
    ),
    "F-014": (
        [{"event_type": "credential_reset_burst", "log_channel": "hris", "resets": 12, "unlocks": 8}],
        [{"event_type": "credential_reset_burst", "log_channel": "hris", "resets": 1, "unlocks": 0}],
    ),
    "F-030": (
        [{"event_type": "ai_confidential_prompt", "log_channel": "ai_gateway", "contains_pii": True, "bytes": 42000}],
        [{"event_type": "ai_confidential_prompt", "log_channel": "ai_gateway", "contains_pii": False, "bytes": 200}],
    ),
    "F-031": (
        [{"event_type": "ai_source_code_paste", "log_channel": "ai_gateway", "lines": 2400, "language": "python"}],
        [{"event_type": "ai_source_code_paste", "log_channel": "ai_gateway", "lines": 40, "language": "python"}],
    ),
    "F-032": (
        [{"event_type": "ai_internal_info_prompt", "log_channel": "ai_gateway", "hosts_disclosed": 8, "users_disclosed": 5}],
        [{"event_type": "ai_internal_info_prompt", "log_channel": "ai_gateway", "hosts_disclosed": 0, "users_disclosed": 0}],
    ),
    "F-033": (
        [{"event_type": "unapproved_ai_domain", "log_channel": "proxy", "domain": "chatgpt-unapproved.example", "allowed": False}],
        [{"event_type": "unapproved_ai_domain", "log_channel": "proxy", "domain": "ai-approved.corp.local", "allowed": True}],
    ),
    "F-034": (
        [{"event_type": "ai_file_upload", "log_channel": "ai_gateway", "files": 12, "total_mb": 890}],
        [{"event_type": "ai_file_upload", "log_channel": "ai_gateway", "files": 1, "total_mb": 2}],
    ),
    "F-035": (
        [{"event_type": "ai_procedure_discovery", "log_channel": "ai_gateway", "topics": ["incident_response", "password_policy"]}],
        [{"event_type": "ai_procedure_discovery", "log_channel": "ai_gateway", "topics": ["general_help"]}],
    ),
    "F-036": (
        [{"event_type": "ai_strategy_content", "log_channel": "ai_gateway", "legal_terms": 14, "strategy_terms": 22}],
        [{"event_type": "ai_strategy_content", "log_channel": "ai_gateway", "legal_terms": 0, "strategy_terms": 0}],
    ),
    "F-042": (
        [{"event_type": "local_sensitive_accumulation", "log_channel": "endpoint", "labeled_files": 420, "gb": 18}],
        [{"event_type": "local_sensitive_accumulation", "log_channel": "endpoint", "labeled_files": 5, "gb": 0.4}],
    ),
    "F-043": (
        [{"event_type": "sensitive_file_move", "log_channel": "endpoint", "from_zone": "restricted", "to_zone": "public"}],
        [{"event_type": "sensitive_file_move", "log_channel": "endpoint", "from_zone": "restricted", "to_zone": "restricted"}],
    ),
    "F-044": (
        [{"event_type": "wiki_bulk_download", "log_channel": "wiki", "pages": 3200, "mb": 2400}],
        [{"event_type": "wiki_bulk_download", "log_channel": "wiki", "pages": 12, "mb": 8}],
    ),
    "F-056": (
        [{"event_type": "print_sensitive_correlation", "log_channel": "cups", "pages": 180, "sensitive_labels": 45}],
        [{"event_type": "print_sensitive_correlation", "log_channel": "cups", "pages": 4, "sensitive_labels": 0}],
    ),
    "F-058": (
        [{"event_type": "dlp_bypass", "log_channel": "dlp", "agent_healthy": False, "bypass_attempt": True}],
        [{"event_type": "dlp_bypass", "log_channel": "dlp", "agent_healthy": True, "bypass_attempt": False}],
    ),
    "F-059": (
        [{"event_type": "clipboard_large_copy", "log_channel": "activity", "bytes": 48_000_000}],
        [{"event_type": "clipboard_large_copy", "log_channel": "activity", "bytes": 1200}],
    ),
    "F-060": (
        [{"event_type": "screenshot_spike", "log_channel": "activity", "count_per_hour": 85}],
        [{"event_type": "screenshot_spike", "log_channel": "activity", "count_per_hour": 3}],
    ),
    "F-061": (
        [{"event_type": "role_server_map_deviation", "log_channel": "endpoint", "unexpected_hosts": 14}],
        [{"event_type": "role_server_map_deviation", "log_channel": "endpoint", "unexpected_hosts": 1}],
    ),
    "F-062": (
        [{"event_type": "risky_log_search", "log_channel": "siem", "keywords": ["password", "token", "suppress"]}],
        [{"event_type": "risky_log_search", "log_channel": "siem", "keywords": ["dashboard"]}],
    ),
    "F-064": (
        [{"event_type": "activity_burst", "log_channel": "activity", "events_per_hour": 4200, "baseline": 400}],
        [{"event_type": "activity_burst", "log_channel": "activity", "events_per_hour": 380, "baseline": 400}],
    ),
    "F-065": (
        [{"event_type": "dormant_system_access", "log_channel": "endpoint", "idle_days": 120, "access_count": 15}],
        [{"event_type": "dormant_system_access", "log_channel": "endpoint", "idle_days": 2, "access_count": 1}],
    ),
    "F-066": (
        [{"event_type": "peer_group_deviation", "log_channel": "app", "z_score": 4.2, "metric": "file_reads"}],
        [{"event_type": "peer_group_deviation", "log_channel": "app", "z_score": 0.3, "metric": "file_reads"}],
    ),
    "F-067": (
        [{"event_type": "personal_cloud_upload", "log_channel": "cloud", "provider": "dropbox-personal", "mb": 2100}],
        [{"event_type": "personal_cloud_upload", "log_channel": "cloud", "provider": "corp-onedrive", "mb": 12}],
    ),
    "F-068": (
        [{"event_type": "first_external_transfer", "log_channel": "proxy", "destination": "203.0.113.50", "mb": 3200, "first_seen": True}],
        [{"event_type": "first_external_transfer", "log_channel": "proxy", "destination": "partner.corp.local", "mb": 50, "first_seen": False}],
    ),
    "F-069": (
        [{"event_type": "proxy_tunnel", "log_channel": "proxy", "protocol": "unknown-tls-tunnel", "duration_minutes": 45}],
        [{"event_type": "proxy_tunnel", "log_channel": "proxy", "protocol": "https", "duration_minutes": 2}],
    ),
    "F-070": (
        [{"event_type": "badge_login_mismatch", "log_channel": "badge", "badge_present": False, "login_success": True}],
        [{"event_type": "badge_login_mismatch", "log_channel": "badge", "badge_present": True, "login_success": True}],
    ),
    "F-071": (
        [
            {"event_type": "composite_signal", "log_channel": "ai_gateway", "signal": "ai_leak", "weight": 0.4},
            {"event_type": "composite_signal", "log_channel": "proxy", "signal": "exfil", "weight": 0.35},
            {"event_type": "composite_signal", "log_channel": "vault", "signal": "secret_burst", "weight": 0.25},
        ],
        [{"event_type": "composite_signal", "log_channel": "endpoint", "signal": "baseline", "weight": 0.1}],
    ),
    "F-072": (
        [{"event_type": "offboarding_activity", "log_channel": "hris", "status": "terminated", "logins_after": 6}],
        [{"event_type": "offboarding_activity", "log_channel": "hris", "status": "active", "logins_after": 0}],
    ),
    "F-073": (
        [{"event_type": "multi_user_file_chain", "log_channel": "wiki", "file_id": "contract-991", "users": 3, "window_minutes": 30}],
        [{"event_type": "multi_user_file_chain", "log_channel": "wiki", "file_id": "contract-991", "users": 1, "window_minutes": 30}],
    ),
    "F-074": (
        [{"event_type": "off_shift_access", "log_channel": "badge", "shift": "off", "login_hour": 2, "badge_swipe": True}],
        [{"event_type": "off_shift_access", "log_channel": "badge", "shift": "day", "login_hour": 10, "badge_swipe": True}],
    ),
    "F-075": (
        [{"event_type": "new_hire_excess_access", "log_channel": "hris", "day": 1, "systems_accessed": 28}],
        [{"event_type": "new_hire_excess_access", "log_channel": "hris", "day": 1, "systems_accessed": 6}],
    ),
    "F-076": (
        [{"event_type": "old_entitlement_use", "log_channel": "hris", "role_changed": True, "old_group_used": True}],
        [{"event_type": "old_entitlement_use", "log_channel": "hris", "role_changed": True, "old_group_used": False}],
    ),
    "F-077": (
        [{"event_type": "leave_activity", "log_channel": "hris", "on_leave": True, "keyboard_events": 900}],
        [{"event_type": "leave_activity", "log_channel": "hris", "on_leave": True, "keyboard_events": 0}],
    ),
    "F-078": (
        [{"event_type": "contractor_out_of_scope", "log_channel": "hris", "identity": "contractor", "systems": ["payroll-db", "dc-admin"]}],
        [{"event_type": "contractor_out_of_scope", "log_channel": "hris", "identity": "contractor", "systems": ["dev-git"]}],
    ),
}
