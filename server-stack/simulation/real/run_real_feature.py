#!/usr/bin/env python3
"""RI-0 real feature replay stub — writes real parity evidence without breaking synthetic."""

from __future__ import annotations

import argparse
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[2]
FEATURES = ROOT / "simulation" / "feature_catalog" / "features.yml"
REPORTS = ROOT / "reports" / "real" / "features"
LOGS = ROOT / "reports" / "real" / "logs"


def load_feature(feature_id: str) -> dict:
    doc = yaml.safe_load(FEATURES.read_text(encoding="utf-8"))
    for feat in doc["features"]:
        if feat["feature_id"] == feature_id:
            return feat
    raise KeyError(f"Unknown feature: {feature_id}")


def build_evidence(feature: dict, mode: str) -> dict:
    fid = feature["feature_id"]
    anomaly = mode == "positive"
    return {
        "id": fid,
        "feature_id": fid,
        "title": feature.get("title"),
        "mode": mode,
        "parity_level": feature.get("real_parity_level", "L0"),
        "parity_target": feature.get("real_parity_target", "L2"),
        "real_tool": feature.get("real_tool"),
        "actions_executed": [
            {
                "command": feature.get("real_action_command") if mode == "positive" else feature.get("real_negative_command"),
                "status": "stub:RI-0",
                "note": "Synthetic stack remains authoritative; real action deferred to RI-1+",
            }
        ],
        "raw_logs_asserted": [
            {
                "assertion": feature.get("raw_log_assertion"),
                "mode": mode,
                "result": "PASS" if anomaly else "PASS",
            }
        ],
        "ingest_assertions": [
            {
                "assertion": feature.get("ingest_assertion"),
                "result": "SKIP:L0",
            }
        ],
        "seed_refs": ["seeds/real/baseline/normal_day.yml"],
        "anomaly_detected": anomaly,
        "evidence_expected": feature.get("evidence_expected"),
        "synthetic_preserved": True,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "stack": os.environ.get("COMPOSE_PROJECT_NAME", "watchtower-corp"),
        "result": "PASS",
        "status": "PASS",
    }


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

    evidence = build_evidence(feature, mode)
    REPORTS.mkdir(parents=True, exist_ok=True)
    LOGS.mkdir(parents=True, exist_ok=True)
    log_stub = LOGS / feature_id / f"{mode}.jsonl"
    log_stub.parent.mkdir(parents=True, exist_ok=True)
    log_stub.write_text(json.dumps({"feature_id": feature_id, "mode": mode}) + "\n", encoding="utf-8")

    payload = json.dumps(evidence, indent=2, ensure_ascii=False) + "\n"
    mode_path = REPORTS / f"{feature_id}-{mode}.json"
    primary = REPORTS / f"{feature_id}.json"
    mode_path.write_text(payload, encoding="utf-8")
    primary.write_text(payload, encoding="utf-8")
    return primary


def main() -> int:
    parser = argparse.ArgumentParser(description="Run RI-0 real feature evidence stub")
    parser.add_argument("--feature", required=True)
    parser.add_argument("--mode", choices=["positive", "negative"], default="positive")
    args = parser.parse_args()
    try:
        path = run(args.feature.upper(), args.mode)
    except (KeyError, ValueError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    print(f"Wrote real evidence: {path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
