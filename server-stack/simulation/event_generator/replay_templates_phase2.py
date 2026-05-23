"""Phase 2 feature replay event templates."""

from __future__ import annotations

PHASE2_TEMPLATES: dict[str, tuple[list[dict], list[dict]]] = {
    "F-016": (
        [{"event_type": "mail_send_volume", "log_channel": "postfix", "messages": 450, "attachment_mb": 120}],
        [{"event_type": "mail_send_volume", "log_channel": "postfix", "messages": 12, "attachment_mb": 5}],
    ),
    "F-017": (
        [{"event_type": "mail_rule_change", "log_channel": "dovecot", "forward_rules_added": 3}],
        [{"event_type": "mail_rule_change", "log_channel": "dovecot", "forward_rules_added": 0}],
    ),
    "F-018": (
        [{"event_type": "imap_mailbox_access", "log_channel": "dovecot", "foreign_mailbox": "ceo@corp.local"}],
        [{"event_type": "imap_mailbox_access", "log_channel": "dovecot", "foreign_mailbox": "self"}],
    ),
    "F-019": (
        [{"event_type": "mail_attachment_entropy", "log_channel": "postfix", "entropy": 7.8, "declared_type": "pdf", "actual_type": "zip"}],
        [{"event_type": "mail_attachment_entropy", "log_channel": "postfix", "entropy": 4.1, "declared_type": "pdf", "actual_type": "pdf"}],
    ),
    "F-020": (
        [{"event_type": "mail_bcc_anomaly", "log_channel": "postfix", "bcc_count": 11, "distribution_list": True}],
        [{"event_type": "mail_bcc_anomaly", "log_channel": "postfix", "bcc_count": 0, "distribution_list": False}],
    ),
    "F-021": (
        [{"event_type": "mail_personal_domain", "log_channel": "postfix", "recipient_domain": "gmail.com", "has_attachment": True}],
        [{"event_type": "mail_personal_domain", "log_channel": "postfix", "recipient_domain": "corp.local", "has_attachment": False}],
    ),
    "F-022": (
        [{"event_type": "mail_external_competitor", "log_channel": "postfix", "recipient_domain": "rival-corp.com"}],
        [{"event_type": "mail_external_competitor", "log_channel": "postfix", "recipient_domain": "partner-approved.com"}],
    ),
    "F-023": (
        [{"event_type": "mail_sensitive_keyword", "log_channel": "postfix", "keywords": ["bordro", "maaş", "confidential"]}],
        [{"event_type": "mail_sensitive_keyword", "log_channel": "postfix", "keywords": []}],
    ),
    "F-024": (
        [{"event_type": "imap_archive_bulk_read", "log_channel": "dovecot", "messages_read": 14000, "years_span": 14}],
        [{"event_type": "imap_archive_bulk_read", "log_channel": "dovecot", "messages_read": 40, "years_span": 1}],
    ),
    "F-025": (
        [{"event_type": "address_book_export", "log_channel": "roundcube", "contacts_exported": 4800}],
        [{"event_type": "address_book_export", "log_channel": "roundcube", "contacts_exported": 5}],
    ),
    "F-026": (
        [{"event_type": "mail_style_deviation", "log_channel": "postfix", "tone_score": 0.92}],
        [{"event_type": "mail_style_deviation", "log_channel": "postfix", "tone_score": 0.12}],
    ),
    "F-027": (
        [{"event_type": "mail_banned_phrase", "log_channel": "postfix", "phrase": "gizli iç bilgi"}],
        [{"event_type": "mail_banned_phrase", "log_channel": "postfix", "phrase": None}],
    ),
    "F-028": (
        [{"event_type": "mail_first_external_sensitive", "log_channel": "postfix", "first_time_recipient": True, "subject_sensitive": True}],
        [{"event_type": "mail_first_external_sensitive", "log_channel": "postfix", "first_time_recipient": False, "subject_sensitive": False}],
    ),
    "F-029": (
        [{"event_type": "webmail_login_attempt", "log_channel": "roundcube", "account": "personal@gmail.com"}],
        [{"event_type": "webmail_login_attempt", "log_channel": "roundcube", "account": "user@corp.local"}],
    ),
    "F-045": (
        [{"event_type": "postgres_bulk_select", "log_channel": "postgres", "tables": 12, "rows_scanned": 4_500_000}],
        [{"event_type": "postgres_bulk_select", "log_channel": "postgres", "tables": 1, "rows_scanned": 1200}],
    ),
    "F-046": (
        [{"event_type": "process_tree_anomaly", "log_channel": "endpoint", "duration_hours": 18, "child_processes": 42}],
        [{"event_type": "process_tree_anomaly", "log_channel": "endpoint", "duration_hours": 1, "child_processes": 3}],
    ),
    "F-047": (
        [{"event_type": "api_pattern_deviation", "log_channel": "app", "calls_per_hour": 430, "baseline": 40}],
        [{"event_type": "api_pattern_deviation", "log_channel": "app", "calls_per_hour": 38, "baseline": 40}],
    ),
    "F-048": (
        [{"event_type": "http_4xx_spike", "log_channel": "nginx", "status_4xx": 5200, "window_minutes": 5}],
        [{"event_type": "http_4xx_spike", "log_channel": "nginx", "status_4xx": 12, "window_minutes": 5}],
    ),
    "F-049": (
        [{"event_type": "git_clone_volume", "log_channel": "gitea", "repos_cloned": 40, "bytes": 4_700_000_000}],
        [{"event_type": "git_clone_volume", "log_channel": "gitea", "repos_cloned": 1, "bytes": 150_000_000}],
    ),
    "F-050": (
        [{"event_type": "siem_suppress_rule", "log_channel": "siem", "self_ip_suppress": True}],
        [{"event_type": "siem_suppress_rule", "log_channel": "siem", "self_ip_suppress": False}],
    ),
    "F-051": (
        [{"event_type": "hypervisor_console_access", "log_channel": "hypervisor", "user": "pm", "console": "proxmox"}],
        [{"event_type": "hypervisor_console_access", "log_channel": "hypervisor", "user": "it-admin", "console": "proxmox"}],
    ),
    "F-052": (
        [{"event_type": "scheduled_task_created", "log_channel": "endpoint", "task_name": "svc_sync_shadow"}],
        [{"event_type": "scheduled_task_created", "log_channel": "endpoint", "task_name": None}],
    ),
    "F-053": (
        [{"event_type": "backup_shadow_delete", "log_channel": "endpoint", "shadow_copies_deleted": 48}],
        [{"event_type": "backup_shadow_delete", "log_channel": "endpoint", "shadow_copies_deleted": 0}],
    ),
    "F-054": (
        [{"event_type": "encoded_powershell", "log_channel": "endpoint", "encoded_command": True, "bypass_policy": True}],
        [{"event_type": "encoded_powershell", "log_channel": "endpoint", "encoded_command": False, "bypass_policy": False}],
    ),
}

LOG_CHANNEL_DIRS: dict[str, str] = {
    "postfix": "postfix",
    "dovecot": "dovecot",
    "roundcube": "roundcube",
    "postgres": "postgres",
    "gitea": "gitea",
    "nginx": "nginx",
    "app": "app",
    "artifact": "artifact",
    "siem": "siem",
    "hypervisor": "hypervisor",
    "endpoint": "endpoint",
}
