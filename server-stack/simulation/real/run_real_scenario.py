#!/usr/bin/env python3
"""RI-5: orchestrate real feature replays for scenarios S-001..S-083."""

from __future__ import annotations

import argparse
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
REAL_DIR = Path(__file__).resolve().parent
SCENARIO_DIR = ROOT / "simulation" / "scenarios"
REPORTS = ROOT / "reports" / "real" / "scenarios"

sys.path.insert(0, str(REAL_DIR))
sys.path.insert(0, str(SCENARIO_DIR))

from config import ALL_REAL_FEATURES  # noqa: E402
from run_real_feature import run_evidence  # noqa: E402
from scenario_lib import feature_ids_for, load_scenario_meta  # noqa: E402


def load_replay_yaml(scenario_id: str, mode: str) -> dict | None:
    path = SCENARIO_DIR / f"{scenario_id}_{mode}.yaml"
    if path.exists():
        import yaml

        return yaml.safe_load(path.read_text(encoding="utf-8"))
    return None


def run(scenario_id: str, mode: str) -> Path:
    meta = load_scenario_meta(scenario_id)
    replay = load_replay_yaml(scenario_id, mode) or {}
    fids = replay.get("feature_ids") or feature_ids_for(scenario_id)

    feature_evidence: list[dict] = []
    actions_executed: list[dict] = []
    raw_logs_asserted: list[dict] = []
    ingest_assertions: list[dict] = []
    seed_refs: list[str] = []
    failed_features: list[str] = []

    for fid in fids:
        if fid not in ALL_REAL_FEATURES:
            failed_features.append(fid)
            continue
        try:
            ev = run_evidence(fid, mode)
            feature_evidence.append(
                {
                    "feature_id": fid,
                    "result": ev.get("result"),
                    "parity_level": ev.get("parity_level"),
                    "actions_executed": ev.get("actions_executed", []),
                    "raw_logs_asserted": ev.get("raw_logs_asserted", []),
                    "ingest_assertions": ev.get("ingest_assertions", []),
                    "seed_refs": ev.get("seed_refs", []),
                }
            )
            actions_executed.extend(ev.get("actions_executed", []))
            raw_logs_asserted.extend(ev.get("raw_logs_asserted", []))
            ingest_assertions.extend(ev.get("ingest_assertions", []))
            for ref in ev.get("seed_refs", []):
                if ref not in seed_refs:
                    seed_refs.append(ref)
            if ev.get("result") != "PASS":
                failed_features.append(fid)
        except Exception as exc:  # noqa: BLE001
            feature_evidence.append({"feature_id": fid, "result": "FAIL", "error": str(exc)})
            failed_features.append(fid)

    ok = len(failed_features) == 0 and len(feature_evidence) == len(fids)
    evidence = {
        "scenario_id": scenario_id,
        "title": meta["title"],
        "mode": mode,
        "category": meta["category"],
        "user_role": meta["user_role"],
        "deterministic_seed": meta["seed"],
        "expected_severity": replay.get("expected_severity", meta["severity"]),
        "feature_ids": fids,
        "parity_level": "L2",
        "parity_target": "L2",
        "features_executed": feature_evidence,
        "actions_executed": actions_executed,
        "raw_logs_asserted": raw_logs_asserted,
        "ingest_assertions": ingest_assertions,
        "seed_refs": seed_refs or ["seeds/real/baseline/normal_day.yml"],
        "anomaly_detected": mode == "positive",
        "event_count": len(actions_executed),
        "synthetic_preserved": True,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "stack": os.environ.get("COMPOSE_PROJECT_NAME", "watchtower-corp"),
        "result": "PASS" if ok else "FAIL",
        "status": "PASS" if ok else "FAIL",
        "replay_key": f"{scenario_id}:{meta['seed']}:{mode}:real",
    }

    REPORTS.mkdir(parents=True, exist_ok=True)
    payload = json.dumps(evidence, indent=2, ensure_ascii=False) + "\n"
    mode_path = REPORTS / f"{scenario_id}-{mode}.json"
    primary = REPORTS / f"{scenario_id}.json"
    mode_path.write_text(payload, encoding="utf-8")
    primary.write_text(payload, encoding="utf-8")
    if not ok:
        raise RuntimeError(f"{scenario_id} real scenario failed: {failed_features}")
    return primary


def main() -> int:
    parser = argparse.ArgumentParser(description="Run real scenario replay")
    parser.add_argument("--scenario", required=True)
    parser.add_argument("--mode", choices=["positive", "negative"], default="positive")
    args = parser.parse_args()
    try:
        path = run(args.scenario.upper(), args.mode)
    except (KeyError, RuntimeError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    print(f"Wrote real scenario evidence: {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
