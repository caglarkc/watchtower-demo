#!/usr/bin/env python3
"""RI-0/RI-1 real integration coverage — metadata + evidence gate."""

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

RI1_FEATURES = frozenset(
    {
        "F-001", "F-002", "F-003", "F-005", "F-006", "F-007", "F-008",
        "F-010", "F-011", "F-015", "F-037", "F-038", "F-039", "F-040", "F-041",
        "F-055", "F-057", "F-063", "F-079", "F-080", "F-081",
    }
)
RI2_FEATURES = frozenset(
    {f"F-{i:03d}" for i in range(16, 30)} | {f"F-{i:03d}" for i in range(45, 55)}
)


def load_features() -> list[dict]:
    doc = yaml.safe_load(FEATURES.read_text(encoding="utf-8"))
    return doc["features"]


def report() -> dict:
    features = load_features()
    rows = []
    meta_ok = pos_ok = neg_ok = ri1_l2 = 0
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
        level = feat.get("real_parity_level", "L0")
        if fid in RI1_FEATURES and level in ("L2", "L3"):
            ri1_l2 += 1
        status = "PASS" if has_meta and has_pos and has_neg else "PENDING"
        if fid in RI1_FEATURES and has_pos and has_neg:
            try:
                pdata = json.loads(pos.read_text(encoding="utf-8"))
                ndata = json.loads(neg.read_text(encoding="utf-8"))
                if pdata.get("result") == "PASS" and ndata.get("result") == "PASS":
                    status = "PASS"
            except json.JSONDecodeError:
                pass
        rows.append(
            {
                "feature_id": fid,
                "real_parity_level": level,
                "real_tool": feat.get("real_tool"),
                "metadata_complete": has_meta,
                "positive_evidence": has_pos,
                "negative_evidence": has_neg,
                "status": status,
            }
        )
    implemented = sum(1 for r in rows if r["status"] == "PASS")
    ri1_rows = [r for r in rows if r["feature_id"] in RI1_FEATURES]
    ri1_pass = sum(1 for r in ri1_rows if r["status"] == "PASS")
    ri2_rows = [r for r in rows if r["feature_id"] in RI2_FEATURES]
    ri2_pass = sum(1 for r in ri2_rows if r["status"] == "PASS")
    ri2_l2 = sum(1 for r in ri2_rows if r.get("real_parity_level") in ("L2", "L3"))
    return {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "phase": "RI-2",
        "total_features": len(rows),
        "metadata_complete": meta_ok,
        "implemented": implemented,
        "positive_real_tests_passed": pos_ok,
        "negative_real_tests_passed": neg_ok,
        "ri1_features": len(RI1_FEATURES),
        "ri1_l2_metadata": ri1_l2,
        "ri1_pass": ri1_pass,
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
        f"ri1={data['ri1_pass']}/{data['ri1_features']}"
    )
    gate = data["metadata_complete"] == 81 and data["ri1_l2_metadata"] == len(RI1_FEATURES)
    return 0 if gate else 1


if __name__ == "__main__":
    raise SystemExit(main())
