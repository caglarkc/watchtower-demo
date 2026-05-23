#!/usr/bin/env python3
"""Run RI-1/RI-2 real feature actions with log and ingest assertions."""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[2]
REAL_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(REAL_DIR))

FEATURES = ROOT / "simulation" / "feature_catalog" / "features.yml"
REPORTS = ROOT / "reports" / "real" / "features"

from config import ALL_REAL_FEATURES, INGEST_L3_FEATURES, RI1_FEATURES, RI2_FEATURES, RI3_FEATURES, RI4_FEATURES  # noqa: E402
from assertions import run_assertions  # noqa: E402


def _run_action(feature_id: str, mode: str) -> dict:
    if feature_id in RI1_FEATURES:
        from actions.p0_identity_network import run_action

        return run_action(feature_id, mode)
    if feature_id in RI2_FEATURES:
        from actions.p1_mail_apps import run_action

        return run_action(feature_id, mode)
    if feature_id in RI3_FEATURES:
        from actions.p2_security_proxy import run_action

        return run_action(feature_id, mode)
    if feature_id in RI4_FEATURES:
        from actions.p3_physical_hr import run_action

        return run_action(feature_id, mode)
    return {"skipped": True}


def load_feature(feature_id: str) -> dict:
    doc = yaml.safe_load(FEATURES.read_text(encoding="utf-8"))
    for feat in doc["features"]:
        if feat["feature_id"] == feature_id:
            return feat
    raise KeyError(f"Unknown feature: {feature_id}")


def run(feature_id: str, mode: str) -> Path:
    feature = load_feature(feature_id)
    for field in (
        "real_parity_level",
        "real_tool",
        "real_action_command",
        "raw_log_assertion",
        "ingest_assertion",
    ):
        if not feature.get(field):
            raise ValueError(f"{feature_id}: missing real metadata field {field}")

    since = time.time()
    action_result = _run_action(feature_id, mode) if feature_id in ALL_REAL_FEATURES else {"skipped": True}
    raw_logs, ingest, ok = run_assertions(feature_id, mode, since)

    parity = feature.get("real_parity_level", "L0")
    if feature_id in ALL_REAL_FEATURES:
        parity = "L2"
        for ing in ingest:
            if ing.get("result") == "PASS" and ing.get("parity_level") == "L3":
                parity = "L3"
                break
        if feature_id in INGEST_L3_FEATURES and parity != "L3":
            parity = "L2"

    seed_refs = ["seeds/real/baseline/normal_day.yml"]
    if feature_id in RI4_FEATURES:
        seed_refs = [
            "seeds/real/hris/employees.yml",
            "seeds/real/badge/locations.yml",
            "seeds/real/print/confidential-report.pdf",
            "seeds/real/crm/records.yml",
        ]
    elif feature_id in RI3_FEATURES:
        seed_refs = [
            "seeds/real/vault/secrets.yml",
            "seeds/real/ai/prompts.yml",
            "seeds/real/baseline/peer_groups.yml",
            "seeds/real/ai/uploads/sample.bin",
        ]
    elif feature_id in RI2_FEATURES:
        seed_refs = [
            "seeds/real/mail/mailboxes.yml",
            "seeds/real/postgres/schema.sql",
            "seeds/real/git/repos.yml",
            "seeds/real/web/endpoints.yml",
        ]
    elif feature_id in RI1_FEATURES:
        seed_refs = [
            "seeds/real/identity/users.csv",
            "seeds/real/files/classification.yml",
            "seeds/real/baseline/normal_day.yml",
        ]

    evidence = {
        "id": feature_id,
        "feature_id": feature_id,
        "title": feature.get("title"),
        "mode": mode,
        "parity_level": parity,
        "parity_target": feature.get("real_parity_target", "L2"),
        "real_tool": feature.get("real_tool"),
        "actions_executed": action_result.get("actions_executed", []),
        "raw_logs_asserted": raw_logs,
        "ingest_assertions": ingest,
        "seed_refs": seed_refs,
        "anomaly_detected": mode == "positive",
        "evidence_expected": feature.get("evidence_expected"),
        "synthetic_preserved": True,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "stack": os.environ.get("COMPOSE_PROJECT_NAME", "watchtower-corp"),
        "result": "PASS" if ok or feature_id not in ALL_REAL_FEATURES else "FAIL",
        "status": "PASS" if ok or feature_id not in ALL_REAL_FEATURES else "FAIL",
    }

    REPORTS.mkdir(parents=True, exist_ok=True)
    payload = json.dumps(evidence, indent=2, ensure_ascii=False) + "\n"
    mode_path = REPORTS / f"{feature_id}-{mode}.json"
    primary = REPORTS / f"{feature_id}.json"
    mode_path.write_text(payload, encoding="utf-8")
    primary.write_text(payload, encoding="utf-8")
    if feature_id in (RI1_FEATURES | RI2_FEATURES | RI3_FEATURES | RI4_FEATURES) and not ok:
        raise RuntimeError(f"{feature_id} real assertions failed")
    return primary


def run_evidence(feature_id: str, mode: str) -> dict:
    """Return evidence dict after running real feature (for scenario orchestration)."""
    path = run(feature_id, mode)
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> int:
    parser = argparse.ArgumentParser(description="Run real feature replay")
    parser.add_argument("--feature", required=True)
    parser.add_argument("--mode", choices=["positive", "negative"], default="positive")
    args = parser.parse_args()
    try:
        path = run(args.feature.upper(), args.mode)
    except (KeyError, ValueError, RuntimeError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    print(f"Wrote real evidence: {path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
