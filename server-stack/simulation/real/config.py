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

LOG_PATHS = {
    "samba-ad": ROOT / "logs" / "identity" / "ad_events.jsonl",
    "samba-audit": ROOT / "logs" / "samba" / "audit.log",
    "zeek-conn": ROOT / "logs" / "zeek" / "conn.log",
    "bind-query": ROOT / "logs" / "dns" / "query.log",
    "dhcp": ROOT / "logs" / "dhcp" / "dhcpd.log",
    "endpoint": ROOT / "logs" / "endpoint",
}

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
    }
)
