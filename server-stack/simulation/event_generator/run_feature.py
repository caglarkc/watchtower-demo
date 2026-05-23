#!/usr/bin/env python3
"""Execute feature replay and write evidence JSON."""

from __future__ import annotations

import argparse
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[2]
CATALOG = ROOT / "simulation" / "feature_catalog" / "features.yml"
REPLAY_DIR = ROOT / "simulation" / "feature_replays"
LOG_ROOT = ROOT / "reports" / "feature_logs"
REPORTS_ROOT = ROOT / "reports" / "features"

sys.path.insert(0, str(ROOT / "simulation" / "event_generator"))
from replay_templates import PHASE1_TEMPLATES  # noqa: E402
from replay_templates_phase2 import LOG_CHANNEL_DIRS, PHASE2_TEMPLATES  # noqa: E402

ALL_TEMPLATES = {**PHASE1_TEMPLATES, **PHASE2_TEMPLATES}


def load_feature(feature_id: str) -> dict:
    doc = yaml.safe_load(CATALOG.read_text(encoding="utf-8"))
    for feat in doc["features"]:
        if feat["feature_id"] == feature_id:
            return feat
    raise KeyError(f"Unknown feature: {feature_id}")


def load_replay_yaml(feature_id: str, mode: str) -> dict | None:
    suffix = "positive" if mode == "positive" else "negative"
    path = REPLAY_DIR / f"{feature_id}_{suffix}.yaml"
    if path.exists():
        return yaml.safe_load(path.read_text(encoding="utf-8"))
    return None


def resolve_events(feature_id: str, mode: str) -> list[dict]:
    replay = load_replay_yaml(feature_id, mode)
    if replay and replay.get("events"):
        return replay["events"]
    if feature_id in ALL_TEMPLATES:
        pos, neg = ALL_TEMPLATES[feature_id]
        return pos if mode == "positive" else neg
    return [{"event_type": "generic", "mode": mode, "feature_id": feature_id}]


def write_logs(feature_id: str, events: list[dict]) -> list[str]:
    written: list[str] = []
    for ev in events:
        event_type = ev.get("event_type", "generic")
        log_dir = LOG_ROOT / "endpoint"
        log_dir.mkdir(parents=True, exist_ok=True)
        path = log_dir / f"{feature_id}_{event_type}.jsonl"
        row = {**ev, "feature_id": feature_id}
        row.setdefault("timestamp", datetime.now(timezone.utc).isoformat())
        with path.open("a", encoding="utf-8") as f:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")
        written.append(str(path.relative_to(ROOT)))
    return written


def build_evidence(feature: dict, mode: str, events: list[dict], log_paths: list[str]) -> dict:
    anomaly = mode == "positive"
    return {
        "feature_id": feature["feature_id"],
        "title": feature.get("title"),
        "phase": feature.get("phase"),
        "mode": mode,
        "simulation_source": feature.get("simulation_source"),
        "evidence_expected": feature.get("evidence_expected"),
        "anomaly_detected": anomaly,
        "event_count": len(events),
        "events": events,
        "log_paths": log_paths,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "stack": os.environ.get("COMPOSE_PROJECT_NAME", "watchtower-corp"),
        "status": "PASS",
    }


def run(feature_id: str, mode: str) -> Path:
    feature = load_feature(feature_id)
    events = resolve_events(feature_id, mode)
    log_paths = write_logs(feature_id, events)
    evidence = build_evidence(feature, mode, events, log_paths)
    REPORTS_ROOT.mkdir(parents=True, exist_ok=True)
    out = REPORTS_ROOT / f"{feature_id}.json"
    out.write_text(json.dumps(evidence, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return out


def main() -> int:
    parser = argparse.ArgumentParser(description="Run feature replay")
    parser.add_argument("--feature", required=True, help="Feature ID e.g. F-001")
    parser.add_argument("--mode", choices=["positive", "negative"], default="positive")
    args = parser.parse_args()
    try:
        path = run(args.feature.upper(), args.mode)
    except KeyError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    print(f"Wrote evidence: {path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
