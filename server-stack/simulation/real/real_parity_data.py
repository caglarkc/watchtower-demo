"""Real parity metadata for 81 features (RI-0 foundation)."""

from __future__ import annotations

# P0 core — target L2/L3 in later RI phases; RI-0 declares L0 current parity.
P0_FEATURES = {
    "F-001", "F-002", "F-003", "F-005", "F-006", "F-007", "F-008",
    "F-010", "F-011", "F-015", "F-037", "F-038", "F-039", "F-040", "F-041",
    "F-055", "F-057", "F-063", "F-079", "F-080", "F-081",
}

P1_FEATURES = {
    "F-016", "F-017", "F-018", "F-019", "F-020", "F-021", "F-022", "F-023",
    "F-024", "F-025", "F-026", "F-027", "F-028", "F-029",
    "F-045", "F-046", "F-047", "F-048", "F-049", "F-050", "F-051", "F-052", "F-053", "F-054",
}

P2_FEATURES = {
    "F-012", "F-013", "F-030", "F-031", "F-032", "F-033", "F-034", "F-035", "F-036",
    "F-042", "F-043", "F-044", "F-058", "F-059", "F-060", "F-061", "F-062",
    "F-064", "F-065", "F-066", "F-067", "F-068", "F-069",
}

P3_FEATURES = {
    "F-009", "F-014", "F-056", "F-070", "F-071", "F-072", "F-073", "F-074",
    "F-075", "F-076", "F-077", "F-078",
}

# F-004 and others not in P0-P3 lists fall through to default L0.
RI0_CURRENT_LEVEL = "L0"
RI1_FEATURES = frozenset(
    {
        "F-001", "F-002", "F-003", "F-004", "F-005", "F-006", "F-007", "F-008",
        "F-010", "F-011", "F-015", "F-037", "F-038", "F-039", "F-040", "F-041",
        "F-055", "F-057", "F-063", "F-079", "F-080", "F-081",
    }
)
RI1_CURRENT_LEVEL = "L2"
RI2_FEATURES = frozenset(
    {f"F-{i:03d}" for i in range(16, 30)} | {f"F-{i:03d}" for i in range(45, 55)}
)
RI2_CURRENT_LEVEL = "L2"
RI3_FEATURES = frozenset(
    {"F-012", "F-013"}
    | {f"F-{i:03d}" for i in range(30, 37)}
    | {"F-042", "F-043", "F-044"}
    | {f"F-{i:03d}" for i in range(58, 63)}
    | {f"F-{i:03d}" for i in range(64, 67)}
    | {f"F-{i:03d}" for i in range(67, 70)}
)
RI3_CURRENT_LEVEL = "L2"
RI4_FEATURES = frozenset(P3_FEATURES)
RI4_CURRENT_LEVEL = "L2"
RI6_L3_FEATURES = RI1_FEATURES | RI2_FEATURES

INGEST_L3_FEATURES = RI6_L3_FEATURES

TARGET_LEVEL_BY_PRIORITY = {
    "P0": "L2",
    "P1": "L2",
    "P2": "L2",
    "P3": "L2",
}

def _priority(feature_id: str) -> str:
    if feature_id in P0_FEATURES:
        return "P0"
    if feature_id in P1_FEATURES:
        return "P1"
    if feature_id in P2_FEATURES:
        return "P2"
    if feature_id in P3_FEATURES:
        return "P3"
    return "P4"


def _infer_real_tool(simulation_source: str) -> str:
    src = simulation_source.lower()
    rules: list[tuple[str, str]] = [
        ("samba ad", "samba-ad"),
        ("samba", "samba-files"),
        ("zeek", "zeek"),
        ("bind", "bind9"),
        ("dhcp", "dhcp-server"),
        ("postfix", "postfix"),
        ("dovecot", "dovecot"),
        ("roundcube", "roundcube"),
        ("postgresql", "postgres"),
        ("gitea", "gitea"),
        ("nginx", "nginx"),
        ("vault", "vault"),
        ("badge", "badge-api"),
        ("hris", "hris-app"),
        ("ai gateway", "ai-gateway"),
        ("proxy sink", "squid-proxy"),
        ("cloud/object", "minio-s3"),
        ("cups", "cups"),
        ("dlp", "dlp-agent"),
        ("mattermost", "mattermost"),
        ("suitecrm", "suitecrm"),
        ("crm", "suitecrm"),
        ("wiki/intranet", "wiki-app"),
        ("siem", "wazuh-siem"),
        ("hypervisor", "hypervisor-console"),
        ("artifact registry", "artifact-registry"),
        ("internal api", "internal-app"),
        ("endpoint", "wazuh-agent"),
        ("api gateway", "app-gateway"),
        ("mail", "postfix"),
        ("helpdesk", "samba-ad"),
        ("hr/", "hris-app"),
        ("multi-signal", "mattermost"),
        ("record access", "suitecrm"),
        ("helpdesk", "hris-app"),
    ]
    for needle, tool in rules:
        if needle in src:
            return tool
    return "endpoint-synthetic"


def _raw_log_assertion(tool: str, evidence_expected: str) -> str:
    log_paths = {
        "samba-ad": "/var/log/samba/auth.log",
        "samba-files": "/var/log/samba/audit.log",
        "zeek": "/opt/zeek/logs/current/conn.log",
        "bind9": "/var/log/named/query.log",
        "dhcp-server": "/var/log/dhcpd.log",
        "postfix": "/var/log/mail.log",
        "dovecot": "/var/log/dovecot.log",
        "roundcube": "/var/log/roundcube/errors.log",
        "postgres": "/var/log/postgresql/pg_audit.log",
        "gitea": "/var/log/gitea/access.log",
        "nginx": "/var/log/nginx/access.log",
        "vault": "/vault/logs/audit.log",
        "wazuh-agent": "/var/ossec/logs/ossec.log",
        "wazuh-siem": "/var/ossec/logs/api.log",
        "squid-proxy": "/var/log/squid/access.log",
        "minio-s3": "/var/log/minio/audit.log",
        "badge-api": "/var/log/badge-api/audit.log",
        "hris-app": "/var/log/hris/audit.log",
        "cups": "/var/log/cups/access_log",
        "dlp-agent": "/var/log/dlp/health.log",
        "ai-gateway": "/var/log/ai-gateway/audit.log",
        "mattermost": "/var/log/mattermost/chat.jsonl",
        "suitecrm": "/var/log/suitecrm/crm.jsonl",
    }
    path = log_paths.get(tool, "/var/log/endpoint/events.jsonl")
    return f"{tool}:{path}:{evidence_expected}"


def _ingest_assertion(feature_id: str, priority: str) -> str:
    if feature_id in INGEST_L3_FEATURES:
        return f"L3:elasticsearch:corp-logs-{feature_id.lower()}"
    if feature_id in RI3_FEATURES or feature_id in RI4_FEATURES:
        return f"L2:log-pipeline:corp-events:{feature_id}"
    return "none:L0:synthetic-authoritative"


def real_metadata_for(feature_id: str, simulation_source: str, evidence_expected: str) -> dict:
    priority = _priority(feature_id)
    tool = _infer_real_tool(simulation_source)
    target = TARGET_LEVEL_BY_PRIORITY.get(priority, "L2")
    if feature_id in RI4_FEATURES:
        current = RI4_CURRENT_LEVEL
    elif feature_id in RI3_FEATURES:
        current = RI3_CURRENT_LEVEL
    elif feature_id in RI2_FEATURES:
        current = RI2_CURRENT_LEVEL
    elif feature_id in RI1_FEATURES:
        current = RI1_CURRENT_LEVEL
    else:
        current = RI0_CURRENT_LEVEL
    return {
        "real_parity_level": current,
        "real_parity_target": target,
        "real_priority": priority,
        "real_tool": tool,
        "real_action_command": f"make real-feature FEATURE={feature_id}",
        "real_negative_command": f"make real-feature-negative FEATURE={feature_id}",
        "raw_log_assertion": _raw_log_assertion(tool, evidence_expected),
        "ingest_assertion": _ingest_assertion(feature_id, priority),
        "real_evidence_positive": f"reports/real/features/{feature_id}-positive.json",
        "real_evidence_negative": f"reports/real/features/{feature_id}-negative.json",
    }
