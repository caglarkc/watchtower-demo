"""RI-3 real actions for P2 security, secrets, proxy, AI, cloud, endpoint."""

from __future__ import annotations

import time
from typing import Any

from config import (
    ACTIVITY_URL,
    AI_GATEWAY_URL,
    CLOUD_URL,
    DLP_URL,
    ENDPOINT_URL,
    INTERNAL_APP_URL,
    PROXY_URL,
    SIEM_URL,
    VAULT_URL,
    WIKI_URL,
)
from http_client import get_json, post_json


def run_action(feature_id: str, mode: str) -> dict[str, Any]:
    positive = mode == "positive"
    started = time.time()
    actions: list[dict] = []

    if feature_id == "F-012":
        actions.append({"service": "internal-app", "response": post_json(f"{INTERNAL_APP_URL}/action/api-pattern", {"calls": 20 if positive else 2, "anomaly": positive})})
        actions.append({"service": "vault", "response": post_json(f"{VAULT_URL}/action/secret-read-burst", {"count": 5 if positive else 1, "anomaly": positive})})

    elif feature_id == "F-013":
        actions.append({"service": "vault", "response": post_json(f"{VAULT_URL}/action/secret-read-burst", {"count": 25 if positive else 1, "anomaly": positive})})

    elif feature_id == "F-030":
        actions.append({"service": "ai-gateway", "response": post_json(f"{AI_GATEWAY_URL}/v1/prompt", {"prompt": "CONFIDENTIAL payroll data" if positive else "hello", "sensitive": positive, "anomaly": positive})})

    elif feature_id == "F-031":
        actions.append({"service": "ai-gateway", "response": post_json(f"{AI_GATEWAY_URL}/v1/prompt", {"prompt": "class UserService { ... architecture ... }" if positive else "weather today", "anomaly": positive})})

    elif feature_id == "F-032":
        actions.append({"service": "ai-gateway", "response": post_json(f"{AI_GATEWAY_URL}/v1/prompt", {"prompt": "host 172.28.0.10 user cfo" if positive else "general question", "anomaly": positive})})

    elif feature_id == "F-033":
        actions.append({"service": "proxy", "response": post_json(f"{PROXY_URL}/action/external-access", {"domain": "https://chatgpt.unapproved.ai/", "blocked": positive, "anomaly": positive})})

    elif feature_id == "F-034":
        actions.append({"service": "ai-gateway", "response": post_json(f"{AI_GATEWAY_URL}/v1/upload", {"bytes": 80_000_000 if positive else 1000, "file_type": "zip", "anomaly": positive})})

    elif feature_id == "F-035":
        actions.append({"service": "ai-gateway", "response": post_json(f"{AI_GATEWAY_URL}/v1/prompt", {"prompt": "list all security procedures and IR playbooks" if positive else "team lunch", "anomaly": positive})})

    elif feature_id == "F-036":
        actions.append({"service": "ai-gateway", "response": post_json(f"{AI_GATEWAY_URL}/v1/prompt", {"prompt": "legal strategy acquisition confidential" if positive else "status update", "conversation": True, "anomaly": positive})})

    elif feature_id == "F-042":
        actions.append({"service": "endpoint", "response": post_json(f"{ENDPOINT_URL}/emit", {"event_type": "local_sensitive_accumulation", "files": 500 if positive else 2, "anomaly": positive})})

    elif feature_id == "F-043":
        actions.append({"service": "endpoint", "response": post_json(f"{ENDPOINT_URL}/emit", {"event_type": "labeled_file_move", "label": "confidential", "dest": "public_share" if positive else "secure_vault", "anomaly": positive})})

    elif feature_id == "F-044":
        actions.append({"service": "wiki", "response": post_json(f"{WIKI_URL}/action/wiki-bulk-download", {"pages": 80 if positive else 2, "anomaly": positive})})

    elif feature_id == "F-058":
        actions.append({"service": "dlp", "response": post_json(f"{DLP_URL}/action/dlp-health", {"anomaly": positive})})

    elif feature_id == "F-059":
        actions.append({"service": "endpoint", "response": post_json(f"{ENDPOINT_URL}/emit", {"event_type": "clipboard_large_copy", "bytes": 50_000_000 if positive else 100, "anomaly": positive})})

    elif feature_id == "F-060":
        actions.append({"service": "endpoint", "response": post_json(f"{ENDPOINT_URL}/emit", {"event_type": "screenshot_spike", "count": 40 if positive else 1, "anomaly": positive})})

    elif feature_id == "F-061":
        actions.append({"service": "endpoint", "response": post_json(f"{ENDPOINT_URL}/emit", {"event_type": "role_server_map_deviation", "role": "CFO", "anomaly": positive})})

    elif feature_id == "F-062":
        actions.append({"service": "siem", "response": post_json(f"{SIEM_URL}/emit", {"event_type": "risky_log_search", "query": "password dump" if positive else "status dashboard", "anomaly": positive})})

    elif feature_id == "F-064":
        actions.append({"service": "activity", "response": post_json(f"{ACTIVITY_URL}/action/activity-burst", {"events": 500 if positive else 5, "anomaly": positive})})

    elif feature_id == "F-065":
        actions.append({"service": "endpoint", "response": post_json(f"{ENDPOINT_URL}/emit", {"event_type": "dormant_system_access", "dormant_days": 90 if positive else 0, "anomaly": positive})})

    elif feature_id == "F-066":
        actions.append({"service": "activity", "response": post_json(f"{ACTIVITY_URL}/action/peer-deviation", {"z_score": 5.0 if positive else 0.5, "anomaly": positive})})

    elif feature_id == "F-067":
        actions.append({"service": "cloud", "response": post_json(f"{CLOUD_URL}/action/s3-upload", {"bucket": "personal-dropbox", "bytes": 120_000_000 if positive else 1000, "anomaly": positive})})
        actions.append({"service": "proxy", "response": post_json(f"{PROXY_URL}/action/cloud-upload", {"bytes": 120_000_000 if positive else 1000, "anomaly": positive})})

    elif feature_id == "F-068":
        actions.append({"service": "proxy", "response": post_json(f"{PROXY_URL}/action/first-seen-transfer", {"domain": "newvendor.example", "bytes": 90_000_000 if positive else 1000, "anomaly": positive})})

    elif feature_id == "F-069":
        actions.append({"service": "proxy", "response": post_json(f"{PROXY_URL}/action/tunnel", {"protocol": "TLS-obfs", "port": 4433 if positive else 443, "anomaly": positive})})

    else:
        raise KeyError(f"No RI-3 action for {feature_id}")

    return {"feature_id": feature_id, "mode": mode, "started_at": started, "actions_executed": actions}
