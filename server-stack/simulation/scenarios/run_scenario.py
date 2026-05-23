#!/usr/bin/env python3
"""Execute scenario replay and write evidence JSON."""

from __future__ import annotations

import argparse
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[2]
SCENARIO_DIR = ROOT / "simulation" / "scenarios"
LOG_ROOT = ROOT / "reports" / "scenario_logs"
REPORTS_ROOT = ROOT / "reports" / "scenarios"

sys.path.insert(0, str(ROOT / "simulation" / "scenarios"))
sys.path.insert(0, str(ROOT / "simulation" / "event_generator"))

from scenario_lib import (  # noqa: E402
    events_for_scenario,
    feature_ids_for,
    load_scenario_meta,
    services_for_events,
)
from run_feature import _log_subdir, LOG_CHANNEL_DIRS  # noqa: E402


def load_replay_yaml(scenario_id: str, mode: str) -> dict | None:
    path = SCENARIO_DIR / f"{scenario_id}_{mode}.yaml"
    if path.exists():
        return yaml.safe_load(path.read_text(encoding="utf-8"))
    return None


def resolve_events(scenario_id: str, mode: str) -> list[dict]:
    replay = load_replay_yaml(scenario_id, mode)
    if replay and replay.get("events"):
        return replay["events"]
    return events_for_scenario(scenario_id, mode)


def write_logs(scenario_id: str, events: list[dict]) -> list[str]:
    written: list[str] = []
    for ev in events:
        event_type = ev.get("event_type", "generic")
        subdir = _log_subdir(ev) if ev.get("log_channel") in LOG_CHANNEL_DIRS else "scenarios"
        log_dir = LOG_ROOT / scenario_id / subdir
        log_dir.mkdir(parents=True, exist_ok=True)
        path = log_dir / f"{event_type}.jsonl"
        row = {**ev, "scenario_id": scenario_id}
        row.setdefault("timestamp", datetime.now(timezone.utc).isoformat())
        with path.open("a", encoding="utf-8") as f:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")
        written.append(str(path.relative_to(ROOT)))
    return written


def build_evidence(scenario_id: str, mode: str, events: list[dict], log_paths: list[str]) -> dict:
    meta = load_scenario_meta(scenario_id)
    replay = load_replay_yaml(scenario_id, mode) or {}
    return {
        "scenario_id": scenario_id,
        "title": meta["title"],
        "mode": mode,
        "category": meta["category"],
        "user_role": meta["user_role"],
        "deterministic_seed": meta["seed"],
        "expected_severity": replay.get("expected_severity", meta["severity"]),
        "feature_ids": replay.get("feature_ids", feature_ids_for(scenario_id)),
        "services": replay.get("services", services_for_events(events)),
        "expected_evidence": replay.get("expected_evidence", meta["title"]),
        "anomaly_detected": mode == "positive",
        "event_count": len(events),
        "events": events,
        "log_paths": log_paths,
        "negative_control": replay.get("negative_control") if mode == "negative" else None,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "stack": os.environ.get("COMPOSE_PROJECT_NAME", "watchtower-corp"),
        "status": "PASS",
        "replay_key": f"{scenario_id}:{meta['seed']}:{mode}",
    }


def run(scenario_id: str, mode: str) -> Path:
    events = resolve_events(scenario_id, mode)
    log_paths = write_logs(scenario_id, events)
    evidence = build_evidence(scenario_id, mode, events, log_paths)
    REPORTS_ROOT.mkdir(parents=True, exist_ok=True)
    mode_path = REPORTS_ROOT / f"{scenario_id}-{mode}.json"
    primary = REPORTS_ROOT / f"{scenario_id}.json"
    payload = json.dumps(evidence, indent=2, ensure_ascii=False) + "\n"
    mode_path.write_text(payload, encoding="utf-8")
    primary.write_text(payload, encoding="utf-8")
    return primary


def main() -> int:
    parser = argparse.ArgumentParser(description="Run scenario replay")
    parser.add_argument("--scenario", required=True, help="Scenario ID e.g. S-001")
    parser.add_argument("--mode", choices=["positive", "negative"], default="positive")
    args = parser.parse_args()
    try:
        path = run(args.scenario.upper(), args.mode)
    except KeyError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    print(f"Wrote evidence: {path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
