"""Phase 1 feature replay event templates (positive / negative)."""

from __future__ import annotations

# feature_id -> (positive_events, negative_events)
PHASE1_TEMPLATES: dict[str, tuple[list[dict], list[dict]]] = {
    "F-001": (
        [{"event_type": "smb_read_volume", "user": "cfo", "bytes_read": 14_000_000_000, "anomaly": True}],
        [{"event_type": "smb_read_volume", "user": "cfo", "bytes_read": 800_000_000, "anomaly": False}],
    ),
    "F-002": (
        [{"event_type": "east_west_flow", "src": "172.28.0.100", "dst_hosts": 42, "bytes": 8_000_000_000}],
        [{"event_type": "east_west_flow", "src": "172.28.0.100", "dst_hosts": 2, "bytes": 5_000_000}],
    ),
    "F-003": (
        [{"event_type": "dns_entropy", "txt_queries": 5000, "nxdomain_ratio": 0.4}],
        [{"event_type": "dns_entropy", "txt_queries": 10, "nxdomain_ratio": 0.01}],
    ),
    "F-004": (
        [{"event_type": "smb_downgrade", "smb_version": "SMB1", "ntlm": "NTLMv1"}],
        [{"event_type": "smb_downgrade", "smb_version": "SMB3", "ntlm": "NTLMv2"}],
    ),
    "F-005": (
        [{"event_type": "dhcp_anomaly", "rogue_scope": True, "duplicate_lease": True}],
        [{"event_type": "dhcp_anomaly", "rogue_scope": False, "duplicate_lease": False}],
    ),
    "F-006": (
        [{"event_type": "ad_auth", "event_id": 4625, "count": 18}, {"event_type": "ad_auth", "event_id": 4624, "count": 1}],
        [{"event_type": "ad_auth", "event_id": 4625, "count": 1}, {"event_type": "ad_auth", "event_id": 4624, "count": 1}],
    ),
    "F-007": (
        [{"event_type": "port_scan", "targets": 200, "ports": 25, "window_minutes": 12}],
        [{"event_type": "port_scan", "targets": 5, "ports": 3, "window_minutes": 12}],
    ),
    "F-008": (
        [{"event_type": "kerberos_tgt", "user": "admin", "targets": 8, "hour": 2}],
        [{"event_type": "kerberos_tgt", "user": "admin", "targets": 0, "hour": 2}],
    ),
    "F-010": (
        [{"event_type": "service_interactive", "account": "svc_sql", "logon_type": 2}],
        [{"event_type": "service_interactive", "account": "svc_sql", "logon_type": 5}],
    ),
    "F-011": (
        [{"event_type": "ad_group_change", "event_id": 4728, "group": "Domain Admins"}],
        [{"event_type": "ad_group_change", "event_id": 4728, "group": "Helpdesk"}],
    ),
    "F-015": (
        [{"event_type": "rdp_hop", "hops": ["ws1", "dc1", "files1", "db1"]}],
        [{"event_type": "rdp_hop", "hops": ["ws1", "files1"]}],
    ),
    "F-037": (
        [{"event_type": "smb_access", "share": "legal", "user_dept": "dev", "files": 41}],
        [{"event_type": "smb_access", "share": "dev", "user_dept": "dev", "files": 3}],
    ),
    "F-038": (
        [{"event_type": "smb_bulk_io", "read_bytes": 18_400_000_000, "write_bytes": 0}],
        [{"event_type": "smb_bulk_io", "read_bytes": 320_000_000, "write_bytes": 0}],
    ),
    "F-039": (
        [{"event_type": "smb_rename_storm", "renames_per_minute": 120}],
        [{"event_type": "smb_rename_storm", "renames_per_minute": 2}],
    ),
    "F-040": (
        [{"event_type": "directory_traversal", "sensitive_paths": 15}],
        [{"event_type": "directory_traversal", "sensitive_paths": 0}],
    ),
    "F-041": (
        [{"event_type": "acl_change", "permission": "Everyone:FullControl"}],
        [{"event_type": "acl_change", "permission": "Finance-RW"}],
    ),
    "F-055": (
        [{"event_type": "usb_write", "device_id": "USB-9F2A", "bytes_written": 2_400_000_000}],
        [{"event_type": "usb_write", "device_id": None, "bytes_written": 0}],
    ),
    "F-057": (
        [{"event_type": "nic_promiscuous", "enabled": True}],
        [{"event_type": "nic_promiscuous", "enabled": False}],
    ),
    "F-063": (
        [{"event_type": "unknown_hardware", "device_id": "NEW-MAC-9912", "success": True}],
        [{"event_type": "unknown_hardware", "device_id": "KNOWN-MAC-001", "success": True}],
    ),
    "F-079": (
        [{"event_type": "after_hours_session", "hour": 2, "interactive": True}],
        [{"event_type": "after_hours_session", "hour": 14, "interactive": True}],
    ),
    "F-080": (
        [{"event_type": "idle_session_abuse", "session_hours": 8, "keyboard_events": 3}],
        [{"event_type": "idle_session_abuse", "session_hours": 2, "keyboard_events": 900}],
    ),
    "F-081": (
        [{"event_type": "role_work_window", "role": "support", "active_hours": [0, 1, 2, 3]}],
        [{"event_type": "role_work_window", "role": "support", "active_hours": [9, 10, 11, 14]}],
    ),
}
