"""RI-4 real actions for P3 physical, HR, collaboration, print, CRM."""

from __future__ import annotations

import time
from typing import Any

from config import (
    AI_GATEWAY_URL,
    BADGE_URL,
    CUPS_URL,
    HRIS_URL,
    MATTERMOST_URL,
    PROXY_URL,
    SAMBA_AD_URL,
    SUITECRM_URL,
    VAULT_URL,
    WIKI_URL,
)
from http_client import post_json


def run_action(feature_id: str, mode: str) -> dict[str, Any]:
    positive = mode == "positive"
    started = time.time()
    actions: list[dict] = []

    if feature_id == "F-009":
        actions.append(
            {
                "service": "badge",
                "response": post_json(
                    f"{BADGE_URL}/action/concurrent-session",
                    {
                        "locations": ["floor-3", "floor-b1"] if positive else ["floor-3"],
                        "minutes_apart": 12 if positive else 0,
                        "anomaly": positive,
                    },
                ),
            }
        )
        actions.append(
            {
                "service": "samba-ad",
                "response": post_json(
                    f"{SAMBA_AD_URL}/action/auth-success",
                    {"user": "alice", "anomaly": positive},
                ),
            }
        )

    elif feature_id == "F-014":
        actions.append(
            {
                "service": "hris",
                "response": post_json(
                    f"{HRIS_URL}/action/credential-reset-burst",
                    {"resets": 12 if positive else 1, "unlocks": 8 if positive else 0, "anomaly": positive},
                ),
            }
        )
        actions.append(
            {
                "service": "samba-ad",
                "response": post_json(
                    f"{SAMBA_AD_URL}/action/credential-reset-burst",
                    {"count": 12 if positive else 1, "anomaly": positive},
                ),
            }
        )

    elif feature_id == "F-056":
        actions.append(
            {
                "service": "cups",
                "response": post_json(
                    f"{CUPS_URL}/action/print-job",
                    {
                        "pages": 180 if positive else 4,
                        "sensitive_labels": 45 if positive else 0,
                        "document": "seeds/real/print/confidential-report.pdf",
                        "anomaly": positive,
                    },
                ),
            }
        )

    elif feature_id == "F-070":
        actions.append(
            {
                "service": "badge",
                "response": post_json(
                    f"{BADGE_URL}/action/badge-login-mismatch",
                    {"badge_present": not positive, "login_success": True, "anomaly": positive},
                ),
            }
        )
        actions.append(
            {
                "service": "samba-ad",
                "response": post_json(
                    f"{SAMBA_AD_URL}/action/auth-success",
                    {"user": "ghost-login", "anomaly": positive},
                ),
            }
        )

    elif feature_id == "F-071":
        actions.append(
            {
                "service": "mattermost",
                "response": post_json(
                    f"{MATTERMOST_URL}/action/composite-bundle",
                    {"signals": ["ai_leak", "exfil", "secret_burst"] if positive else ["baseline"], "anomaly": positive},
                ),
            }
        )
        if positive:
            actions.append({"service": "ai-gateway", "response": post_json(f"{AI_GATEWAY_URL}/v1/prompt", {"prompt": "leak", "anomaly": True})})
            actions.append({"service": "proxy", "response": post_json(f"{PROXY_URL}/action/cloud-upload", {"bytes": 50_000_000, "anomaly": True})})
            actions.append({"service": "vault", "response": post_json(f"{VAULT_URL}/action/secret-read-burst", {"count": 10, "anomaly": True})})

    elif feature_id == "F-072":
        actions.append(
            {
                "service": "hris",
                "response": post_json(
                    f"{HRIS_URL}/action/offboarding-activity",
                    {"status": "terminated" if positive else "active", "logins_after": 6 if positive else 0, "anomaly": positive},
                ),
            }
        )
        if positive:
            actions.append(
                {
                    "service": "samba-ad",
                    "response": post_json(f"{SAMBA_AD_URL}/action/auth-success", {"user": "leaver", "anomaly": True}),
                }
            )

    elif feature_id == "F-073":
        actions.append(
            {
                "service": "suitecrm",
                "response": post_json(
                    f"{SUITECRM_URL}/action/record-chain",
                    {"record_id": "contract-991", "users": 3 if positive else 1, "anomaly": positive},
                ),
            }
        )
        actions.append(
            {
                "service": "wiki",
                "response": post_json(
                    f"{WIKI_URL}/action/wiki-bulk-download",
                    {"pages": 3 if positive else 1, "anomaly": positive},
                ),
            }
        )

    elif feature_id == "F-074":
        actions.append(
            {
                "service": "badge",
                "response": post_json(
                    f"{BADGE_URL}/action/off-shift-access",
                    {"shift": "off" if positive else "day", "login_hour": 2 if positive else 10, "anomaly": positive},
                ),
            }
        )

    elif feature_id == "F-075":
        actions.append(
            {
                "service": "hris",
                "response": post_json(
                    f"{HRIS_URL}/action/new-hire-access",
                    {"day": 1, "systems_accessed": 28 if positive else 6, "anomaly": positive},
                ),
            }
        )

    elif feature_id == "F-076":
        actions.append(
            {
                "service": "hris",
                "response": post_json(
                    f"{HRIS_URL}/action/role-change-entitlement",
                    {"role_changed": True, "old_group_used": positive, "anomaly": positive},
                ),
            }
        )

    elif feature_id == "F-077":
        actions.append(
            {
                "service": "hris",
                "response": post_json(
                    f"{HRIS_URL}/action/leave-activity",
                    {"on_leave": True, "keyboard_events": 900 if positive else 0, "anomaly": positive},
                ),
            }
        )

    elif feature_id == "F-078":
        actions.append(
            {
                "service": "hris",
                "response": post_json(
                    f"{HRIS_URL}/action/contractor-scope",
                    {
                        "systems": ["payroll-db", "dc-admin"] if positive else ["dev-git"],
                        "anomaly": positive,
                    },
                ),
            }
        )

    else:
        raise KeyError(f"No RI-4 action for {feature_id}")

    return {"feature_id": feature_id, "mode": mode, "started_at": started, "actions_executed": actions}
