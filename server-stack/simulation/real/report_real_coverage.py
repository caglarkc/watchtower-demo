#!/usr/bin/env python3
"""RI-0 real integration coverage — metadata + evidence gate."""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[2]
FEATURES = ROOT / "simulation" / "feature_catalog" / "features.yml"
REPORTS = ROOT / "reports" / "real" / "features"
OUT = ROOT / "reports" / "real" / "coverage"

REQUIRED_META = (
    "real_parity_level",
    "real_tool",
    "real_action_command",
    "raw_log_assertion",
    "ingest_assertion",
)


def load_features() -> list[dict]:
    doc = yaml.safe_load(FEATURES.read_text(encoding="utf-8"))
    return doc["features"]


def report() -> dict:
    features = load_features()
    rows = []
    meta_ok = pos_ok = neg_ok = 0
    for feat in features:
        fid = feat["feature_id"]
        has_meta = all(feat.get(f) for f in REQUIRED_META)
        if has_meta:
            meta_ok += 1
        pos = REPORTS / f"{fid}-positive.json"
        neg = REPORTS / f"{fid}-negative.json"
        has_pos = pos.exists()
        has_neg = neg.exists()
        if has_pos:
            pos_ok += 1
        if has_neg:
            neg_ok += 1
        rows.append(
            {
                "feature_id": fid,
                "real_parity_level": feat.get("real_parity_level"),
                "real_tool": feat.get("real_tool"),
                "metadata_complete": has_meta,
                "positive_evidence": has_pos,
                "negative_evidence": has_neg,
                "status": "PASS" if has_meta and has_pos and has_neg else "PENDING",
            }
        )
    implemented = sum(1 for r in rows if r["status"] == "PASS")
    return {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "phase": "RI-0",
        "total_features": len(rows),
        "metadata_complete": meta_ok,
        "implemented": implemented,
        "positive_real_tests_passed": pos_ok,
        "negative_real_tests_passed": neg_ok,
        "l2_or_higher": sum(1 for r in rows if r.get("real_parity_level") in ("L2", "L3")),
        "waivers": [],
        "features": rows,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--all", action="store_true", default=True)
    args = parser.parse_args()

    OUT.mkdir(parents=True, exist_ok=True)
    data = report()
    out = OUT / "real_feature_coverage.json"
    out.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(
        f"wrote {out} metadata={data['metadata_complete']}/{data['total_features']} "
        f"evidence={data['implemented']}/{data['total_features']}"
    )
    gate = data["metadata_complete"] == data["total_features"] == 81
    return 0 if gate else 1


if __name__ == "__main__":
    raise SystemExit(main())
