#!/usr/bin/env python3
"""Generate feature/scenario coverage reports."""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[2]
FEATURES = ROOT / "simulation" / "feature_catalog" / "features.yml"
REPORTS = ROOT / "reports" / "features"
OUT_DIR = ROOT / "reports" / "coverage"


def load_features() -> list[dict]:
    doc = yaml.safe_load(FEATURES.read_text(encoding="utf-8"))
    return doc["features"]


def report_phase(phase: int | None) -> dict:
    features = load_features()
    if phase is not None:
        features = [f for f in features if f.get("phase") == phase]

    rows = []
    pos_pass = neg_pass = 0
    for feat in features:
        fid = feat["feature_id"]
        pos_file = REPORTS / f"{fid}-positive.json"
        neg_file = REPORTS / f"{fid}-negative.json"
        has_pos = pos_file.exists()
        has_neg = neg_file.exists()
        if has_pos:
            pos_pass += 1
        if has_neg:
            neg_pass += 1
        rows.append(
            {
                "feature_id": fid,
                "phase": feat.get("phase"),
                "positive_evidence": has_pos,
                "negative_evidence": has_neg,
                "status": "PASS" if has_pos and has_neg else "PENDING",
            }
        )

    implemented = sum(1 for r in rows if r["status"] == "PASS")
    return {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "phase_filter": phase,
        "total_features": len(rows),
        "implemented": implemented,
        "positive_tests_passed": pos_pass,
        "negative_tests_passed": neg_pass,
        "waivers": [],
        "features": rows,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--phase", type=int, default=None)
    parser.add_argument("--all", action="store_true")
    args = parser.parse_args()

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    if args.all:
        report = report_phase(None)
        out = OUT_DIR / "feature_coverage.json"
    else:
        report = report_phase(args.phase)
        out = OUT_DIR / f"feature_coverage_phase{args.phase or 'all'}.json"

    out.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(
        f"wrote {out} ({report['implemented']}/{report['total_features']} PASS, "
        f"pos={report['positive_tests_passed']} neg={report['negative_tests_passed']})"
    )
    gate_ok = (
        report["total_features"] == 81
        and report["positive_tests_passed"] == 81
        and report["negative_tests_passed"] == 81
        and report["implemented"] == 81
    )
    return 0 if (args.all and gate_ok) or not args.all else 1


if __name__ == "__main__":
    raise SystemExit(main())
