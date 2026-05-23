"""RI-2 real actions for P1 mail, DB, Git, web/API, admin features."""

from __future__ import annotations

import json
import subprocess
import time
from pathlib import Path
from typing import Any

from config import (
    ARTIFACT_URL,
    DOVECOT_URL,
    ENDPOINT_URL,
    GITEA_ACTIONS_URL,
    HYPERVISOR_URL,
    INTERNAL_APP_URL,
    NGINX_URL,
    POSTFIX_URL,
    POSTGRES_ACTIONS_URL,
    ROUNDCUBE_URL,
    SIEM_URL,
)
from http_client import get_json, post_json

ROOT = Path(__file__).resolve().parents[3]


def run_action(feature_id: str, mode: str) -> dict[str, Any]:
    positive = mode == "positive"
    started = time.time()
    actions: list[dict] = []

    if feature_id == "F-016":
        actions.append(
            {
                "service": "postfix",
                "response": post_json(
                    f"{POSTFIX_URL}/action/smtp-send",
                    {
                        "size_bytes": 25_000_000 if positive else 50_000,
                        "to": ["team@corp.local"],
                        "anomaly": positive,
                    },
                ),
            }
        )

    elif feature_id == "F-017":
        actions.append(
            {
                "service": "dovecot",
                "response": post_json(
                    f"{DOVECOT_URL}/action/rule-change",
                    {"user": "user@corp.local", "rule_type": "forward", "anomaly": positive},
                ),
            }
        )

    elif feature_id == "F-018":
        actions.append(
            {
                "service": "dovecot",
                "response": post_json(
                    f"{DOVECOT_URL}/action/imap-fetch",
                    {"out_of_mailbox": positive, "mailbox": "HR/private", "messages": 50 if positive else 1, "anomaly": positive},
                ),
            }
        )

    elif feature_id == "F-019":
        actions.append(
            {
                "service": "postfix",
                "response": post_json(
                    f"{POSTFIX_URL}/action/smtp-send",
                    {"attachment_entropy": 0.99 if positive else 0.2, "size_bytes": 5_000_000, "anomaly": positive},
                ),
            }
        )

    elif feature_id == "F-020":
        actions.append(
            {
                "service": "postfix",
                "response": post_json(
                    f"{POSTFIX_URL}/action/smtp-send",
                    {"bcc": ["hidden@external.com"] if positive else [], "to": ["all@corp.local"], "anomaly": positive},
                ),
            }
        )

    elif feature_id == "F-021":
        actions.append(
            {
                "service": "postfix",
                "response": post_json(
                    f"{POSTFIX_URL}/action/smtp-send",
                    {"to": ["user@gmail.com"] if positive else ["peer@corp.local"], "size_bytes": 2_000_000, "anomaly": positive},
                ),
            }
        )

    elif feature_id == "F-022":
        actions.append(
            {
                "service": "postfix",
                "response": post_json(
                    f"{POSTFIX_URL}/action/smtp-send",
                    {"external_domain": "competitor.example" if positive else "partner.corp.local", "anomaly": positive},
                ),
            }
        )

    elif feature_id == "F-023":
        actions.append(
            {
                "service": "postfix",
                "response": post_json(
                    f"{POSTFIX_URL}/action/smtp-send",
                    {"keywords": ["confidential", "salary"] if positive else ["hello"], "anomaly": positive},
                ),
            }
        )

    elif feature_id == "F-024":
        actions.append(
            {
                "service": "dovecot",
                "response": post_json(
                    f"{DOVECOT_URL}/action/imap-fetch",
                    {"archive_bulk": positive, "messages": 500 if positive else 2, "anomaly": positive},
                ),
            }
        )

    elif feature_id == "F-025":
        actions.append(
            {
                "service": "roundcube",
                "response": post_json(
                    f"{ROUNDCUBE_URL}/action/contact-export",
                    {"user": "user@corp.local", "records": 2000 if positive else 5, "anomaly": positive},
                ),
            }
        )

    elif feature_id in ("F-026", "F-027"):
        actions.append(
            {
                "service": "postfix",
                "response": post_json(
                    f"{POSTFIX_URL}/action/smtp-send",
                    {
                        "keywords": ["URGENT TRANSFER"] if feature_id == "F-027" and positive else ["weekly update"],
                        "anomaly": positive,
                    },
                ),
            }
        )

    elif feature_id == "F-028":
        actions.append(
            {
                "service": "postfix",
                "response": post_json(
                    f"{POSTFIX_URL}/action/smtp-send",
                    {"to": ["newvendor@unknown.com"] if positive else ["known@corp.local"], "keywords": ["confidential"], "anomaly": positive},
                ),
            }
        )

    elif feature_id == "F-029":
        actions.append(
            {
                "service": "roundcube",
                "response": post_json(
                    f"{ROUNDCUBE_URL}/action/webmail-login",
                    {"user": "personal@gmail.com" if positive else "user@corp.local", "success": not positive, "anomaly": positive},
                ),
            }
        )

    elif feature_id == "F-045":
        actions.append(
            {
                "service": "postgres-actions",
                "response": post_json(f"{POSTGRES_ACTIONS_URL}/action/bulk-select", {"anomaly": positive, "limit": 500 if positive else 2}),
            }
        )

    elif feature_id == "F-046":
        actions.append(
            {
                "service": "endpoint",
                "response": post_json(
                    f"{ENDPOINT_URL}/emit",
                    {"event_type": "process_tree_anomaly", "duration_hours": 48 if positive else 1, "anomaly": positive},
                ),
            }
        )

    elif feature_id == "F-047":
        for _ in range(30 if positive else 2):
            get_json(f"{INTERNAL_APP_URL}/api/reports")
        actions.append(
            {
                "service": "internal-app",
                "response": post_json(f"{INTERNAL_APP_URL}/action/api-pattern", {"calls": 30 if positive else 2, "anomaly": positive}),
            }
        )

    elif feature_id == "F-048":
        paths = ["/api/forbidden"] * (40 if positive else 2)
        codes = []
        access_log = ROOT / "logs" / "nginx" / "access.log"
        access_log.parent.mkdir(parents=True, exist_ok=True)
        for p in paths:
            proc = subprocess.run(
                ["curl", "-s", "-o", "/dev/null", "-w", "%{http_code}", f"{NGINX_URL}{p}"],
                capture_output=True,
                text=True,
                timeout=5,
            )
            code = proc.stdout.strip() or "000"
            codes.append(code)
            try:
                access_log.open("a", encoding="utf-8").write(
                    f'{time.time()} client 172.28.0.100 "{p}" {code}\n'
                )
            except OSError:
                fallback = ROOT / "reports" / "real" / "logs" / "nginx" / "access.log"
                fallback.parent.mkdir(parents=True, exist_ok=True)
                fallback.open("a", encoding="utf-8").write(f'{time.time()} client 172.28.0.100 "{p}" {code}\n')
        actions.append({"service": "nginx", "http_codes": codes})

    elif feature_id == "F-049":
        actions.append(
            {
                "service": "gitea-actions",
                "response": post_json(
                    f"{GITEA_ACTIONS_URL}/action/clone",
                    {"repo": "corp/demo", "count": 8 if positive else 1, "bytes": 50_000_000 if positive else 1000, "anomaly": positive},
                ),
            }
        )
        actions.append(
            {
                "service": "artifact",
                "response": post_json(
                    f"{ARTIFACT_URL}/action/artifact-download",
                    {"bytes": 40_000_000 if positive else 1000, "anomaly": positive},
                ),
            }
        )

    elif feature_id == "F-050":
        actions.append(
            {
                "service": "siem",
                "response": post_json(
                    f"{SIEM_URL}/action/siem-suppress",
                    {"rule": "suppress_all_alerts" if positive else "test_rule", "anomaly": positive},
                ),
            }
        )

    elif feature_id == "F-051":
        actions.append(
            {
                "service": "hypervisor",
                "response": post_json(
                    f"{HYPERVISOR_URL}/action/hypervisor-access",
                    {"user": "admin", "anomaly": positive},
                ),
            }
        )

    elif feature_id == "F-052":
        actions.append(
            {
                "service": "endpoint",
                "response": post_json(
                    f"{ENDPOINT_URL}/emit",
                    {"event_type": "scheduled_task_new", "task": "PersistenceUpdate" if positive else "WindowsUpdate", "anomaly": positive},
                ),
            }
        )

    elif feature_id == "F-053":
        actions.append(
            {
                "service": "endpoint",
                "response": post_json(
                    f"{ENDPOINT_URL}/emit",
                    {"event_type": "backup_disabled", "target": "shadow_copy", "anomaly": positive},
                ),
            }
        )

    elif feature_id == "F-054":
        actions.append(
            {
                "service": "endpoint",
                "response": post_json(
                    f"{ENDPOINT_URL}/emit",
                    {"event_type": "encoded_script", "encoded": positive, "bypass": positive, "anomaly": positive},
                ),
            }
        )

    else:
        raise KeyError(f"No RI-2 action for {feature_id}")

    return {"feature_id": feature_id, "mode": mode, "started_at": started, "actions_executed": actions}
