#!/usr/bin/env python3
"""Generate Phase 0 coverage manifests from catalog_data."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

import yaml

from catalog_data import (
    FEATURE_CATEGORIES,
    FEATURE_MATRIX,
    FEATURE_TITLES,
    SCENARIO_FEATURE_MAP,
    SCENARIOS,
)

CATALOG_DIR = Path(__file__).resolve().parent
REPORTS_DIR = CATALOG_DIR.parents[1] / "reports" / "coverage"


def _services_for_source(source: str) -> list[str]:
    mapping = {
        "Samba": "samba",
        "Zeek": "zeek",
        "BIND": "bind",
        "DHCP": "dhcp",
        "Postfix": "postfix",
        "Dovecot": "dovecot",
        "Roundcube": "roundcube",
        "PostgreSQL": "postgres",
        "Gitea": "gitea",
        "Nginx": "nginx",
        "Vault": "vault",
        "Badge": "badge_api",
        "HRIS": "hris_mock",
        "AI gateway": "ai_gateway_mock",
        "proxy": "proxy_sink",
        "CUPS": "cups",
        "wiki": "wiki_mock",
        "SIEM": "siem_admin_mock",
        "hypervisor": "hypervisor_mock",
        "DLP": "dlp_mock",
        "endpoint": "endpoint_synthetic",
        "Wazuh": "wazuh",
    }
    found: list[str] = []
    for key, svc in mapping.items():
        if key.lower() in source.lower() and svc not in found:
            found.append(svc)
    if not found:
        found.append("endpoint_synthetic")
    return found


def build_features() -> dict:
    features = []
    for row in FEATURE_MATRIX:
        fid = row["id"]
        features.append(
            {
                "feature_id": fid,
                "title": FEATURE_TITLES[fid],
                "category": FEATURE_CATEGORIES[fid],
                "phase": row["phase"],
                "simulation_source": row["simulation_source"],
                "simulation_type": "synthetic_replay",
                "services": _services_for_source(row["simulation_source"]),
                "evidence_expected": row["evidence_expected"],
                "positive_command": f"make feature FEATURE={fid}",
                "negative_command": f"make feature-negative FEATURE={fid}",
                "evidence_path": f"reports/features/{fid}.json",
                "replay_positive": f"simulation/feature_replays/{fid}_positive.yaml",
                "replay_negative": f"simulation/feature_replays/{fid}_negative.yaml",
                "status": "manifest",
            }
        )
    return {
        "version": "1.0",
        "phase": 0,
        "total_features": len(features),
        "features": features,
    }


def build_scenarios() -> dict:
    scenarios = []
    for s in SCENARIOS:
        sid = s["id"]
        scenarios.append(
            {
                "scenario_id": sid,
                "title": s["title"],
                "category": s["category"],
                "user_role": s["user_role"],
                "expected_severity": s["severity"],
                "deterministic_seed": s["seed"],
                "feature_ids": SCENARIO_FEATURE_MAP[sid],
                "replay_command": f"make scenario SCENARIO={sid}",
                "negative_command": f"make scenario-negative SCENARIO={sid}",
                "evidence_path": f"reports/scenarios/{sid}.json",
                "replay_script": f"simulation/scenarios/{sid}_replay.yaml",
                "status": "manifest",
            }
        )
    return {
        "version": "1.0",
        "phase": 0,
        "total_scenarios": len(scenarios),
        "scenarios": scenarios,
    }


def build_coverage_matrix() -> dict:
    mappings = []
    feature_to_scenarios: dict[str, list[str]] = {row["id"]: [] for row in FEATURE_MATRIX}

    for sid, fids in SCENARIO_FEATURE_MAP.items():
        mappings.append({"scenario_id": sid, "feature_ids": fids})
        for fid in fids:
            if sid not in feature_to_scenarios[fid]:
                feature_to_scenarios[fid].append(sid)

    feature_coverage = [
        {
            "feature_id": fid,
            "scenario_ids": sorted(sids),
            "scenario_count": len(sids),
        }
        for fid, sids in sorted(feature_to_scenarios.items())
    ]

    unmapped_features = [f["feature_id"] for f in feature_coverage if f["scenario_count"] == 0]

    return {
        "version": "1.0",
        "phase": 0,
        "scenario_to_features": mappings,
        "feature_to_scenarios": feature_coverage,
        "summary": {
            "total_features": len(FEATURE_MATRIX),
            "total_scenarios": len(SCENARIOS),
            "features_with_scenario": len(FEATURE_MATRIX) - len(unmapped_features),
            "features_without_scenario": unmapped_features,
        },
    }


def write_phase0_report(features: dict, scenarios: dict, matrix: dict) -> None:
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    report = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "phase": 0,
        "feature_coverage": {
            "total_features": features["total_features"],
            "manifest_complete": features["total_features"] == 81,
        },
        "scenario_coverage": {
            "total_scenarios": scenarios["total_scenarios"],
            "manifest_complete": scenarios["total_scenarios"] == 83,
        },
        "matrix_summary": matrix["summary"],
    }
    (REPORTS_DIR / "phase0_catalog.json").write_text(
        json.dumps(report, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )


def main() -> None:
    features = build_features()
    scenarios = build_scenarios()
    matrix = build_coverage_matrix()

    for name, data in [
        ("features.yml", features),
        ("scenarios.yml", scenarios),
        ("coverage_matrix.yml", matrix),
    ]:
        path = CATALOG_DIR / name
        path.write_text(
            yaml.dump(data, allow_unicode=True, sort_keys=False, default_flow_style=False),
            encoding="utf-8",
        )
        print(f"wrote {path}")

    write_phase0_report(features, scenarios, matrix)
    print(f"wrote {REPORTS_DIR / 'phase0_catalog.json'}")


if __name__ == "__main__":
    main()
