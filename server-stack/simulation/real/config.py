"""Service endpoints for real integration (RI-1+)."""

from __future__ import annotations

import os
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

SAMBA_AD_URL = os.environ.get("SAMBA_AD_URL", "http://172.28.0.10:8080")
ZEEK_URL = os.environ.get("ZEEK_URL", "http://172.28.0.14:8080")
ENDPOINT_URL = os.environ.get("ENDPOINT_URL", "http://172.28.0.15:8080")
FILES_ACTIONS_URL = os.environ.get("FILES_ACTIONS_URL", "http://172.28.0.42:8080")
DHCP_LOGGER_URL = os.environ.get("DHCP_LOGGER_URL", "http://172.28.0.43:8080")
BIND_DNS_IP = os.environ.get("BIND_DNS_IP", "172.28.0.12")
ELASTICSEARCH_URL = os.environ.get("ELASTICSEARCH_URL", "http://172.28.0.17:9200")
LOG_PIPELINE_URL = os.environ.get("LOG_PIPELINE_URL", "http://172.28.0.16:9201")

POSTFIX_URL = os.environ.get("POSTFIX_URL", "http://172.28.0.20:8080")
DOVECOT_URL = os.environ.get("DOVECOT_URL", "http://172.28.0.21:8080")
ROUNDCUBE_URL = os.environ.get("ROUNDCUBE_URL", "http://172.28.0.22:8080")
POSTGRES_ACTIONS_URL = os.environ.get("POSTGRES_ACTIONS_URL", "http://172.28.0.44:8080")
GITEA_ACTIONS_URL = os.environ.get("GITEA_ACTIONS_URL", "http://172.28.0.45:8080")
NGINX_URL = os.environ.get("NGINX_URL", "http://172.28.0.25")
INTERNAL_APP_URL = os.environ.get("INTERNAL_APP_URL", "http://172.28.0.26:8080")
ARTIFACT_URL = os.environ.get("ARTIFACT_URL", "http://172.28.0.27:8080")
SIEM_URL = os.environ.get("SIEM_URL", "http://172.28.0.28:8080")
HYPERVISOR_URL = os.environ.get("HYPERVISOR_URL", "http://172.28.0.29:8080")

LOG_PATHS = {
    "samba-ad": ROOT / "logs" / "identity" / "ad_events.jsonl",
    "samba-audit": ROOT / "logs" / "samba" / "audit.log",
    "zeek-conn": ROOT / "logs" / "zeek" / "conn.log",
    "bind-query": ROOT / "logs" / "dns" / "query.log",
    "dhcp": ROOT / "logs" / "dhcp" / "dhcpd.log",
    "endpoint": ROOT / "logs" / "endpoint",
    "postfix": ROOT / "logs" / "postfix" / "postfix.jsonl",
    "dovecot": ROOT / "logs" / "dovecot" / "dovecot.jsonl",
    "roundcube": ROOT / "logs" / "roundcube" / "roundcube.jsonl",
    "postgres-audit": ROOT / "logs" / "postgres" / "pg_audit.log",
    "gitea-access": ROOT / "logs" / "gitea" / "gitea-access.jsonl",
    "nginx-access": ROOT / "logs" / "nginx" / "access.log",
    "app-audit": ROOT / "logs" / "app" / "audit.jsonl",
    "siem-audit": ROOT / "logs" / "siem" / "audit.jsonl",
    "hypervisor-audit": ROOT / "logs" / "hypervisor" / "audit.jsonl",
    "artifact-audit": ROOT / "logs" / "artifact" / "audit.jsonl",
}

RI2_FEATURES = frozenset(
    {f"F-{i:03d}" for i in range(16, 30)}
    | {f"F-{i:03d}" for i in range(45, 55)}
)

RI1_FEATURES = frozenset(
    {
        "F-001", "F-002", "F-003", "F-005", "F-006", "F-007", "F-008",
        "F-010", "F-011", "F-015", "F-037", "F-038", "F-039", "F-040", "F-041",
        "F-055", "F-057", "F-063", "F-079", "F-080", "F-081",
    }
)

INGEST_FEATURES = frozenset(
    {
        "F-001", "F-002", "F-006", "F-007", "F-010", "F-011",
        "F-037", "F-038", "F-079",
        "F-016", "F-023", "F-045", "F-048", "F-049",
    }
)

ALL_REAL_FEATURES = RI1_FEATURES | RI2_FEATURES
