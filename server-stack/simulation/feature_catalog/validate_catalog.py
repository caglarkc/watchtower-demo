#!/usr/bin/env python3
"""Validate Phase 0 feature/scenario coverage manifests."""

from __future__ import annotations

import json
import sys
from pathlib import Path

import yaml

CATALOG_DIR = Path(__file__).resolve().parent
REQUIRED_FEATURE_COUNT = 81
REQUIRED_SCENARIO_COUNT = 83


def _load_yaml(name: str) -> dict:
    path = CATALOG_DIR / name
    if not path.exists():
        raise FileNotFoundError(f"Missing manifest: {path}")
    with path.open(encoding="utf-8") as f:
        return yaml.safe_load(f)


def validate() -> list[str]:
    errors: list[str] = []

    features_doc = _load_yaml("features.yml")
    scenarios_doc = _load_yaml("scenarios.yml")
    matrix_doc = _load_yaml("coverage_matrix.yml")

    features = features_doc.get("features", [])
    scenarios = scenarios_doc.get("scenarios", [])

    if len(features) != REQUIRED_FEATURE_COUNT:
        errors.append(f"Expected {REQUIRED_FEATURE_COUNT} features, got {len(features)}")
    if len(scenarios) != REQUIRED_SCENARIO_COUNT:
        errors.append(f"Expected {REQUIRED_SCENARIO_COUNT} scenarios, got {len(scenarios)}")

    feature_ids = [f["feature_id"] for f in features]
    scenario_ids = [s["scenario_id"] for s in scenarios]

    if len(feature_ids) != len(set(feature_ids)):
        errors.append("Duplicate feature_id entries in features.yml")
    if len(scenario_ids) != len(set(scenario_ids)):
        errors.append("Duplicate scenario_id entries in scenarios.yml")

    required_feature_fields = (
        "phase",
        "simulation_source",
        "positive_command",
        "negative_command",
        "evidence_path",
    )
    for feat in features:
        fid = feat.get("feature_id", "<unknown>")
        for field in required_feature_fields:
            if not feat.get(field):
                errors.append(f"{fid}: missing required field '{field}'")

    for scen in scenarios:
        sid = scen.get("scenario_id", "<unknown>")
        if not scen.get("feature_ids"):
            errors.append(f"{sid}: must map to at least one feature")
        if not scen.get("replay_command"):
            errors.append(f"{sid}: missing replay_command")

    feature_set = set(feature_ids)
    for mapping in matrix_doc.get("scenario_to_features", []):
        sid = mapping.get("scenario_id")
        for fid in mapping.get("feature_ids", []):
            if fid not in feature_set:
                errors.append(f"{sid}: references unknown feature {fid}")

    unmapped = matrix_doc.get("summary", {}).get("features_without_scenario", [])
    if unmapped:
        errors.append(f"Features without scenario mapping: {', '.join(unmapped)}")

    return errors


def main() -> int:
    try:
        errors = validate()
    except Exception as exc:  # noqa: BLE001
        print(f"VALIDATE FAIL: {exc}", file=sys.stderr)
        return 1

    if errors:
        print("VALIDATE FAIL:")
        for err in errors:
            print(f"  - {err}")
        return 1

    print("VALIDATE PASS: 81 features, 83 scenarios, coverage matrix OK")
    report_path = CATALOG_DIR.parents[1] / "reports" / "coverage" / "phase0_validate.json"
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(
        json.dumps({"status": "PASS", "features": 81, "scenarios": 83}, indent=2) + "\n",
        encoding="utf-8",
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
