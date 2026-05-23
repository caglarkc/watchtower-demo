"""Scenario replay helpers — deterministic events from feature templates."""

from __future__ import annotations

import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[2]
SCENARIOS_YML = ROOT / "simulation" / "feature_catalog" / "scenarios.yml"
CATALOG_DATA = ROOT / "simulation" / "feature_catalog" / "catalog_data.py"

sys.path.insert(0, str(ROOT / "simulation" / "event_generator"))
sys.path.insert(0, str(ROOT / "simulation" / "feature_catalog"))

from catalog_data import SCENARIO_FEATURE_MAP, SCENARIOS  # noqa: E402
from replay_templates import PHASE1_TEMPLATES  # noqa: E402
from replay_templates_phase2 import PHASE2_TEMPLATES  # noqa: E402
from replay_templates_phase3 import PHASE3_TEMPLATES  # noqa: E402

ALL_TEMPLATES = {**PHASE1_TEMPLATES, **PHASE2_TEMPLATES, **PHASE3_TEMPLATES}

LOG_CHANNEL_TO_SERVICE: dict[str, str] = {
    "endpoint": "endpoint-synthetic",
    "postfix": "postfix",
    "dovecot": "dovecot",
    "roundcube": "roundcube",
    "postgres": "postgres",
    "gitea": "gitea",
    "nginx": "nginx",
    "app": "internal-app",
    "artifact": "artifact-registry",
    "siem": "siem-admin",
    "hypervisor": "hypervisor-console",
    "ai_gateway": "ai-gateway-mock",
    "proxy": "proxy-sink",
    "cloud": "cloud-storage-mock",
    "vault": "vault-mock",
    "mattermost": "mattermost",
    "cups": "cups",
    "badge": "badge-api",
    "hris": "hris-mock",
    "wiki": "wiki-mock",
    "suitecrm": "suitecrm-mock",
    "dlp": "dlp-mock",
    "activity": "activity-generator",
    "samba": "samba-files",
    "bind": "bind-dns",
    "dhcp": "dhcp-server",
    "zeek": "zeek-synthetic",
}


def load_scenario_meta(scenario_id: str) -> dict:
    for s in SCENARIOS:
        if s["id"] == scenario_id:
            return s
    doc = yaml.safe_load(SCENARIOS_YML.read_text(encoding="utf-8"))
    for s in doc["scenarios"]:
        if s["scenario_id"] == scenario_id:
            return {
                "id": s["scenario_id"],
                "title": s["title"],
                "category": s["category"],
                "user_role": s["user_role"],
                "severity": s["expected_severity"],
                "seed": s["deterministic_seed"],
            }
    raise KeyError(f"Unknown scenario: {scenario_id}")


def feature_ids_for(scenario_id: str) -> list[str]:
    return SCENARIO_FEATURE_MAP[scenario_id]


def events_for_scenario(scenario_id: str, mode: str) -> list[dict]:
    meta = load_scenario_meta(scenario_id)
    fids = feature_ids_for(scenario_id)
    events: list[dict] = []
    anchor = {
        "event_type": "scenario_anchor",
        "log_channel": "endpoint",
        "scenario_id": scenario_id,
        "user_role": meta["user_role"],
        "category": meta["category"],
        "seed": meta["seed"],
        "anomaly": mode == "positive",
    }
    events.append(anchor)
    for fid in fids:
        if fid not in ALL_TEMPLATES:
            continue
        pos, neg = ALL_TEMPLATES[fid]
        picked = pos if mode == "positive" else neg
        for ev in picked:
            events.append({**ev, "source_feature": fid, "scenario_id": scenario_id})
    return events


def services_for_events(events: list[dict]) -> list[str]:
    services: list[str] = []
    for ev in events:
        ch = ev.get("log_channel", "endpoint")
        svc = LOG_CHANNEL_TO_SERVICE.get(ch, "endpoint-synthetic")
        if svc not in services:
            services.append(svc)
    return sorted(services)
