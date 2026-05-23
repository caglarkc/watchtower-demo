#!/usr/bin/env python3
"""RI-5 real scenario coverage gate — 83/83 positive + negative."""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[2]
SCENARIOS_YML = ROOT / "simulation" / "feature_catalog" / "scenarios.yml"
REPORTS = ROOT / "reports" / "real" / "scenarios"
OUT = ROOT / "reports" / "real" / "coverage"


def load_scenarios() -> list[str]:
    doc = yaml.safe_load(SCENARIOS_YML.read_text(encoding="utf-8"))
    return [s["scenario_id"] for s in doc["scenarios"]]


def _evidence_pass(sid: str) -> tuple[bool, bool]:
    pos = REPORTS / f"{sid}-positive.json"
    neg = REPORTS / f"{sid}-negative.json"
    if not (pos.exists() and neg.exists()):
        return False, False
    try:
        pdata = json.loads(pos.read_text(encoding="utf-8"))
        ndata = json.loads(neg.read_text(encoding="utf-8"))
        return pdata.get("result") == "PASS", ndata.get("result") == "PASS"
    except json.JSONDecodeError:
        return False, False


def report() -> dict:
    ids = load_scenarios()
    rows = []
    pos_pass = neg_pass = 0
    for sid in ids:
        has_pos = (REPORTS / f"{sid}-positive.json").exists()
        has_neg = (REPORTS / f"{sid}-negative.json").exists()
        pos_ok, neg_ok = _evidence_pass(sid) if has_pos and has_neg else (False, False)
        if pos_ok:
            pos_pass += 1
        if neg_ok:
            neg_pass += 1
        status = "PASS" if pos_ok and neg_ok else "PENDING"
        rows.append(
            {
                "scenario_id": sid,
                "positive_evidence": has_pos,
                "negative_evidence": has_neg,
                "positive_pass": pos_ok,
                "negative_pass": neg_ok,
                "status": status,
            }
        )
    implemented = sum(1 for r in rows if r["status"] == "PASS")
    return {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "phase": "RI-5",
        "total_scenarios": len(rows),
        "implemented": implemented,
        "positive_replays_passed": pos_pass,
        "negative_replays_passed": neg_pass,
        "waivers": [],
        "scenarios": rows,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--all", action="store_true", default=True)
    parser.parse_args()

    OUT.mkdir(parents=True, exist_ok=True)
    data = report()
    out = OUT / "real_scenario_coverage.json"
    out.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(
        f"wrote {out} pos={data['positive_replays_passed']}/{data['total_scenarios']} "
        f"neg={data['negative_replays_passed']}/{data['total_scenarios']}"
    )
    gate = (
        data["total_scenarios"] == 83
        and data["positive_replays_passed"] == 83
        and data["negative_replays_passed"] == 83
    )
    return 0 if gate else 1


if __name__ == "__main__":
    raise SystemExit(main())
