"""RI-1 real actions for P0 identity, file, DNS, DHCP, network features."""

from __future__ import annotations

import random
import subprocess
import time
from typing import Any

from config import (
    BIND_DNS_IP,
    DHCP_LOGGER_URL,
    ENDPOINT_URL,
    FILES_ACTIONS_URL,
    SAMBA_AD_URL,
    ZEEK_URL,
)
from http_client import post_json


def _ts() -> float:
    return time.time()


def _zeek_records_positive(feature: str) -> list[dict]:
    if feature == "F-002":
        hosts = [f"172.28.0.{h}" for h in range(110, 130)]
        return [
            {
                "id.orig_h": "172.28.0.100",
                "id.resp_h": h,
                "id.resp_p": 445,
                "proto": "tcp",
                "service": "smb",
                "orig_bytes": 5000,
                "resp_bytes": 5000,
            }
            for h in hosts
        ]
    if feature == "F-007":
        return [
            {
                "id.orig_h": "172.28.0.100",
                "id.resp_h": "172.28.0.11",
                "id.resp_p": p,
                "proto": "tcp",
                "orig_bytes": 40,
                "resp_bytes": 0,
            }
            for p in range(20, 120)
        ]
    if feature == "F-015":
        return [
            {"id.orig_h": "172.28.0.100", "id.resp_h": "172.28.0.50", "id.resp_p": 3389, "service": "rdp"},
            {"id.orig_h": "172.28.0.50", "id.resp_h": "172.28.0.51", "id.resp_p": 3389, "service": "rdp"},
        ]
    return [
        {
            "id.orig_h": "172.28.0.100",
            "id.resp_h": "172.28.0.11",
            "id.resp_p": 445,
            "proto": "tcp",
            "service": "smb",
            "orig_bytes": 14_000_000,
            "resp_bytes": 14_000_000,
        }
    ]


def _zeek_records_negative() -> list[dict]:
    return [
        {
            "id.orig_h": "172.28.0.100",
            "id.resp_h": "172.28.0.11",
            "id.resp_p": 445,
            "proto": "tcp",
            "service": "smb",
            "orig_bytes": 1024,
            "resp_bytes": 2048,
        }
    ]


def _dig_queries(positive: bool) -> list[str]:
    if positive:
        return [f"entropy-{random.randint(10000, 99999)}.corp.local" for _ in range(8)]
    return ["www.corp.local", "dc1.corp.local"]


def run_action(feature_id: str, mode: str) -> dict[str, Any]:
    positive = mode == "positive"
    started = _ts()
    actions: list[dict] = []

    if feature_id == "F-001":
        body = {"user": "cfo", "bytes_read": 14_000_000_000 if positive else 1_000_000, "count": 5 if positive else 1}
        actions.append({"service": "samba-files-actions", "response": post_json(f"{FILES_ACTIONS_URL}/action/read-volume", body)})
        actions.append({"service": "zeek", "response": post_json(f"{ZEEK_URL}/emit", {"records": _zeek_records_positive("F-001") if positive else _zeek_records_negative()})})

    elif feature_id == "F-002":
        actions.append({"service": "zeek", "response": post_json(f"{ZEEK_URL}/emit", {"records": _zeek_records_positive("F-002") if positive else _zeek_records_negative()})})

    elif feature_id == "F-003":
        queries = _dig_queries(positive)
        results = []
        for q in queries:
            qtype = "TXT" if positive else "A"
            cmd = ["dig", f"@{BIND_DNS_IP}", q, qtype, "+time=2", "+tries=1"]
            proc = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
            results.append({"query": q, "returncode": proc.returncode})
        actions.append({"service": "bind-dns", "dig": results})

    elif feature_id == "F-005":
        body = {"count": 4 if positive else 0}
        if positive:
            actions.append({"service": "dhcp-logger", "response": post_json(f"{DHCP_LOGGER_URL}/action/rogue-dhcp", body)})
        else:
            actions.append({"service": "dhcp-logger", "note": "negative: no rogue event emitted"})

    elif feature_id == "F-006":
        if positive:
            actions.append({"service": "samba-ad", "response": post_json(f"{SAMBA_AD_URL}/action/auth-fail-burst", {"user": "brute1", "count": 10})})
        else:
            actions.append({"service": "samba-ad", "response": post_json(f"{SAMBA_AD_URL}/action/auth-success", {"user": "normal_user"})})

    elif feature_id == "F-007":
        actions.append({"service": "zeek", "response": post_json(f"{ZEEK_URL}/emit", {"records": _zeek_records_positive("F-007") if positive else _zeek_records_negative()})})

    elif feature_id == "F-008":
        targets = ["dc1", "files1", "sql1", "app1", "vault1"] if positive else ["dc1"]
        actions.append({"service": "samba-ad", "response": post_json(f"{SAMBA_AD_URL}/action/kerberos-diversity", {"targets": targets})})

    elif feature_id == "F-010":
        actions.append({"service": "samba-ad", "response": post_json(f"{SAMBA_AD_URL}/action/service-account-interactive", {"user": "svc_sql" if positive else "svc_sql", "interactive": positive})})

    elif feature_id == "F-011":
        actions.append(
            {
                "service": "samba-ad",
                "response": post_json(
                    f"{SAMBA_AD_URL}/action/group-change",
                    {"group": "Domain Admins", "member": "attacker1", "action": "add" if positive else "remove"},
                ),
            }
        )

    elif feature_id == "F-015":
        actions.append({"service": "zeek", "response": post_json(f"{ZEEK_URL}/emit", {"records": _zeek_records_positive("F-015") if positive else _zeek_records_negative()})})
        actions.append(
            {
                "service": "endpoint",
                "response": post_json(
                    f"{ENDPOINT_URL}/emit",
                    {"event_type": "rdp_hop", "hops": 3 if positive else 1, "anomaly": positive},
                ),
            }
        )

    elif feature_id == "F-037":
        actions.append(
            {
                "service": "samba-files-actions",
                "response": post_json(
                    f"{FILES_ACTIONS_URL}/action/cross-dept-access",
                    {"user": "finance1", "department": "hr" if positive else "finance"},
                ),
            }
        )

    elif feature_id == "F-038":
        actions.append(
            {
                "service": "samba-files-actions",
                "response": post_json(
                    f"{FILES_ACTIONS_URL}/action/bulk-io",
                    {"read_bytes": 18_400_000_000 if positive else 100_000, "write_bytes": 0},
                ),
            }
        )

    elif feature_id == "F-039":
        actions.append(
            {
                "service": "samba-files-actions",
                "response": post_json(f"{FILES_ACTIONS_URL}/action/rename-storm", {"count": 15 if positive else 1}),
            }
        )

    elif feature_id == "F-040":
        paths = ["/share/legal/confidential", "/share/hr/payroll"] if positive else ["/share/legal/public"]
        actions.append({"service": "samba-files-actions", "response": post_json(f"{FILES_ACTIONS_URL}/action/dir-traversal", {"paths": paths})})

    elif feature_id == "F-041":
        actions.append(
            {
                "service": "samba-files-actions",
                "response": post_json(f"{FILES_ACTIONS_URL}/action/acl-change", {"path": "/share/public", "acl": "Everyone:FULL" if positive else "Domain Users:READ"}),
            }
        )

    elif feature_id == "F-055":
        actions.append(
            {
                "service": "endpoint",
                "response": post_json(
                    f"{ENDPOINT_URL}/emit",
                    {"event_type": "usb_write", "device": "USB3", "bytes": 2_000_000_000 if positive else 1000, "anomaly": positive},
                ),
            }
        )

    elif feature_id == "F-057":
        actions.append(
            {
                "service": "endpoint",
                "response": post_json(
                    f"{ENDPOINT_URL}/emit",
                    {"event_type": "nic_promiscuous", "enabled": positive, "anomaly": positive},
                ),
            }
        )

    elif feature_id == "F-063":
        actions.append(
            {
                "service": "endpoint",
                "response": post_json(
                    f"{ENDPOINT_URL}/emit",
                    {"event_type": "unknown_hardware", "device_id": "UNKNOWN-PC-99" if positive else "CORP-LAPTOP-01", "anomaly": positive},
                ),
            }
        )

    elif feature_id == "F-079":
        actions.append(
            {
                "service": "endpoint",
                "response": post_json(
                    f"{ENDPOINT_URL}/emit",
                    {"event_type": "after_hours_session", "hour": 2 if positive else 14, "anomaly": positive},
                ),
            }
        )
        actions.append({"service": "samba-ad", "response": post_json(f"{SAMBA_AD_URL}/action/auth-success", {"user": "cfo", "logon_type": 2})})

    elif feature_id == "F-080":
        actions.append(
            {
                "service": "endpoint",
                "response": post_json(
                    f"{ENDPOINT_URL}/emit",
                    {"event_type": "idle_session_abuse", "idle_minutes": 120 if positive else 5, "keyboard_events": 0 if positive else 50, "anomaly": positive},
                ),
            }
        )

    elif feature_id == "F-081":
        actions.append(
            {
                "service": "endpoint",
                "response": post_json(
                    f"{ENDPOINT_URL}/emit",
                    {"event_type": "role_work_window", "role": "CFO", "violation": positive, "anomaly": positive},
                ),
            }
        )

    else:
        raise KeyError(f"No RI-1 action for {feature_id}")

    return {"feature_id": feature_id, "mode": mode, "started_at": started, "actions_executed": actions}
