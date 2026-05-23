#!/usr/bin/env python3
"""RI real integration coverage — metadata + evidence gate."""

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
        "F-001", "F-002", "F-003", "F-004", "F-005", "F-006", "F-007", "F-008",
        "F-010", "F-011", "F-015", "F-037", "F-038", "F-039", "F-040", "F-041",
        "F-055", "F-057", "F-063", "F-079", "F-080", "F-081",
    }
)
RI2_FEATURES = frozenset(
    {f"F-{i:03d}" for i in range(16, 30)} | {f"F-{i:03d}" for i in range(45, 55)}
)
RI3_FEATURES = frozenset(
    {"F-012", "F-013"}
    | {f"F-{i:03d}" for i in range(30, 37)}
    | {"F-042", "F-043", "F-044"}
    | {f"F-{i:03d}" for i in range(58, 63)}
    | {f"F-{i:03d}" for i in range(64, 67)}
    | {f"F-{i:03d}" for i in range(67, 70)}
)
RI4_FEATURES = frozenset(
    {"F-009", "F-014", "F-056", "F-070", "F-071", "F-072", "F-073", "F-074", "F-075", "F-076", "F-077", "F-078"}
)
ALL_REAL = RI1_FEATURES | RI2_FEATURES | RI3_FEATURES | RI4_FEATURES


def load_features() -> list[dict]:
    doc = yaml.safe_load(FEATURES.read_text(encoding="utf-8"))
    return doc["features"]


def _evidence_pass(fid: str) -> bool:
    pos = REPORTS / f"{fid}-positive.json"
    neg = REPORTS / f"{fid}-negative.json"
    if not (pos.exists() and neg.exists()):
        return False
    try:
        pdata = json.loads(pos.read_text(encoding="utf-8"))
        ndata = json.loads(neg.read_text(encoding="utf-8"))
        return pdata.get("result") == "PASS" and ndata.get("result") == "PASS"
    except json.JSONDecodeError:
        return False


def report() -> dict:
    features = load_features()
    rows = []
    meta_ok = pos_ok = neg_ok = 0
    for feat in features:
        fid = feat["feature_id"]
        has_meta = all(feat.get(f) for f in REQUIRED_META)
        if has_meta:
            meta_ok += 1
        has_pos = (REPORTS / f"{fid}-positive.json").exists()
        has_neg = (REPORTS / f"{fid}-negative.json").exists()
        if has_pos:
            pos_ok += 1
        if has_neg:
            neg_ok += 1
        evidence_level = feat.get("real_parity_level", "L0")
        if has_pos:
            try:
                pdata = json.loads((REPORTS / f"{fid}-positive.json").read_text(encoding="utf-8"))
                evidence_level = pdata.get("parity_level", evidence_level)
            except json.JSONDecodeError:
                pass
        status = "PASS" if has_meta and _evidence_pass(fid) else ("PENDING" if fid in ALL_REAL else "N/A")
        rows.append(
            {
                "feature_id": fid,
                "real_parity_level": evidence_level,
                "catalog_parity_level": feat.get("real_parity_level", "L0"),
                "metadata_complete": has_meta,
                "positive_evidence": has_pos,
                "negative_evidence": has_neg,
                "status": status,
            }
        )

    def _phase_stats(ids: frozenset) -> dict:
        subset = [r for r in rows if r["feature_id"] in ids]
        return {
            "count": len(ids),
            "l2_metadata": sum(1 for r in subset if r["real_parity_level"] in ("L2", "L3")),
            "pass": sum(1 for r in subset if r["status"] == "PASS"),
        }

    ri1 = _phase_stats(RI1_FEATURES)
    ri2 = _phase_stats(RI2_FEATURES)
    ri3 = _phase_stats(RI3_FEATURES)
    ri4 = _phase_stats(RI4_FEATURES)
    return {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "phase": "RI-6",
        "total_features": len(rows),
        "metadata_complete": meta_ok,
        "implemented": sum(1 for r in rows if r["status"] == "PASS"),
        "positive_real_tests_passed": pos_ok,
        "negative_real_tests_passed": neg_ok,
        "ri1_features": ri1["count"],
        "ri1_l2_metadata": ri1["l2_metadata"],
        "ri1_pass": ri1["pass"],
        "ri2_features": ri2["count"],
        "ri2_l2_metadata": ri2["l2_metadata"],
        "ri2_pass": ri2["pass"],
        "ri3_features": ri3["count"],
        "ri3_l2_metadata": ri3["l2_metadata"],
        "ri3_pass": ri3["pass"],
        "ri4_features": ri4["count"],
        "ri4_l2_metadata": ri4["l2_metadata"],
        "ri4_pass": ri4["pass"],
        "l2_or_higher": sum(1 for r in rows if r.get("real_parity_level") in ("L2", "L3")),
        "l3_count": sum(1 for r in rows if r.get("real_parity_level") == "L3"),
        "l3_minimum": 40,
        "waivers": [],
        "features": rows,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--all", action="store_true", default=True)
    parser.parse_args()

    OUT.mkdir(parents=True, exist_ok=True)
    data = report()
    out = OUT / "real_feature_coverage.json"
    out.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(
        f"wrote {out} metadata={data['metadata_complete']}/{data['total_features']} "
        f"ri1={data['ri1_pass']}/{data['ri1_features']} "
        f"ri2={data['ri2_pass']}/{data['ri2_features']} "
        f"ri3={data['ri3_pass']}/{data['ri3_features']} "
        f"ri4={data['ri4_pass']}/{data['ri4_features']}"
    )
    gate = (
        data["metadata_complete"] == 81
        and data["ri1_l2_metadata"] == data["ri1_features"]
        and data["ri2_l2_metadata"] == data["ri2_features"]
        and data["ri3_l2_metadata"] == data["ri3_features"]
        and data["ri4_l2_metadata"] == data["ri4_features"]
        and data["l2_or_higher"] == 81
        and data["l3_count"] >= 40
        and data["implemented"] == 81
    )
    return 0 if gate else 1


if __name__ == "__main__":
    raise SystemExit(main())
