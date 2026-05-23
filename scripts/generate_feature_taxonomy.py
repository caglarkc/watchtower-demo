#!/usr/bin/env python3
"""Generate watchtower/config/feature_taxonomy.yml from server-stack catalog."""

from __future__ import annotations

import sys
from pathlib import Path

import yaml

PROJECT_ROOT = Path(__file__).resolve().parents[1]
FEATURES_YML = (
    PROJECT_ROOT / "server-stack" / "simulation" / "feature_catalog" / "features.yml"
)
OUTPUT = PROJECT_ROOT / "watchtower" / "config" / "feature_taxonomy.yml"

# primary_class, severity_floor, secondary_classes (optional)
CLASSIFICATION: dict[str, tuple[str, str, list[str]]] = {
    "F-001": ("baseline-anomaly", "WARNING", []),
    "F-002": ("baseline-anomaly", "WARNING", []),
    "F-003": ("baseline-anomaly", "WARNING", []),
    "F-004": ("hard-rule", "ALERT", []),
    "F-005": ("hard-rule", "ALERT", []),
    "F-006": ("hard-rule", "ALERT", []),
    "F-007": ("hard-rule", "WARNING", []),
    "F-008": ("baseline-anomaly", "WARNING", []),
    "F-009": ("cross-signal", "ALERT", []),
    "F-010": ("policy-rule", "ALERT", []),
    "F-011": ("policy-rule", "CRITICAL", []),
    "F-012": ("baseline-anomaly", "WARNING", []),
    "F-013": ("baseline-anomaly", "WARNING", []),
    "F-014": ("baseline-anomaly", "WARNING", []),
    "F-015": ("hard-rule", "ALERT", []),
    "F-016": ("baseline-anomaly", "WARNING", []),
    "F-017": ("policy-rule", "ALERT", []),
    "F-018": ("policy-rule", "WARNING", []),
    "F-019": ("hard-rule", "WARNING", []),
    "F-020": ("baseline-anomaly", "WARNING", []),
    "F-021": ("policy-rule", "ALERT", []),
    "F-022": ("policy-rule", "ALERT", []),
    "F-023": ("policy-rule", "WARNING", []),
    "F-024": ("baseline-anomaly", "WARNING", []),
    "F-025": ("policy-rule", "ALERT", []),
    "F-026": ("baseline-anomaly", "LOG", []),
    "F-027": ("policy-rule", "WARNING", []),
    "F-028": ("policy-rule", "ALERT", []),
    "F-029": ("policy-rule", "WARNING", []),
    "F-030": ("policy-rule", "CRITICAL", []),
    "F-031": ("policy-rule", "CRITICAL", []),
    "F-032": ("policy-rule", "CRITICAL", []),
    "F-033": ("policy-rule", "ALERT", []),
    "F-034": ("baseline-anomaly", "WARNING", []),
    "F-035": ("policy-rule", "ALERT", []),
    "F-036": ("policy-rule", "ALERT", []),
    "F-037": ("policy-rule", "ALERT", []),
    "F-038": ("baseline-anomaly", "WARNING", []),
    "F-039": ("baseline-anomaly", "ALERT", ["hard-rule"]),
    "F-040": ("hard-rule", "ALERT", []),
    "F-041": ("hard-rule", "CRITICAL", []),
    "F-042": ("baseline-anomaly", "WARNING", []),
    "F-043": ("policy-rule", "CRITICAL", []),
    "F-044": ("baseline-anomaly", "WARNING", []),
    "F-045": ("baseline-anomaly", "WARNING", []),
    "F-046": ("baseline-anomaly", "WARNING", []),
    "F-047": ("baseline-anomaly", "WARNING", []),
    "F-048": ("baseline-anomaly", "WARNING", []),
    "F-049": ("baseline-anomaly", "WARNING", []),
    "F-050": ("hard-rule", "CRITICAL", []),
    "F-051": ("policy-rule", "ALERT", []),
    "F-052": ("hard-rule", "ALERT", []),
    "F-053": ("hard-rule", "CRITICAL", []),
    "F-054": ("hard-rule", "ALERT", []),
    "F-055": ("cross-signal", "ALERT", ["hard-rule"]),
    "F-056": ("cross-signal", "WARNING", []),
    "F-057": ("hard-rule", "ALERT", []),
    "F-058": ("hard-rule", "CRITICAL", []),
    "F-059": ("baseline-anomaly", "WARNING", []),
    "F-060": ("baseline-anomaly", "WARNING", []),
    "F-061": ("baseline-anomaly", "WARNING", []),
    "F-062": ("policy-rule", "WARNING", []),
    "F-063": ("hard-rule", "WARNING", []),
    "F-064": ("baseline-anomaly", "WARNING", []),
    "F-065": ("baseline-anomaly", "WARNING", []),
    "F-066": ("baseline-anomaly", "WARNING", []),
    "F-067": ("policy-rule", "ALERT", []),
    "F-068": ("baseline-anomaly", "ALERT", []),
    "F-069": ("hard-rule", "ALERT", []),
    "F-070": ("cross-signal", "ALERT", []),
    "F-071": ("cross-signal", "ALERT", []),
    "F-072": ("cross-signal", "CRITICAL", []),
    "F-073": ("cross-signal", "ALERT", []),
    "F-074": ("cross-signal", "ALERT", []),
    "F-075": ("cross-signal", "WARNING", []),
    "F-076": ("cross-signal", "ALERT", []),
    "F-077": ("cross-signal", "ALERT", []),
    "F-078": ("policy-rule", "ALERT", []),
    "F-079": ("baseline-anomaly", "WARNING", []),
    "F-080": ("cross-signal", "WARNING", []),
    "F-081": ("baseline-anomaly", "WARNING", []),
}

CONTEXT_BY_CLASS: dict[str, list[str]] = {
    "policy-rule": [
        "user",
        "role",
        "department",
        "asset",
        "action",
        "entitlement",
        "approval_ticket",
    ],
    "hard-rule": [
        "user",
        "role",
        "source_ip",
        "asset",
        "action",
        "technical_indicator",
    ],
    "baseline-anomaly": [
        "user",
        "role",
        "department",
        "asset",
        "time_window",
        "user_baseline",
        "department_baseline",
        "role_in_department_baseline",
    ],
    "cross-signal": [
        "user",
        "role",
        "department",
        "time_window",
        "correlated_signals",
        "signal_sources",
    ],
}


def _flags(primary: str) -> tuple[bool, bool, bool]:
    if primary == "policy-rule":
        return False, False, True
    if primary == "hard-rule":
        return False, False, False
    if primary == "baseline-anomaly":
        return True, True, False
    # cross-signal
    return False, False, True


def main() -> int:
    with FEATURES_YML.open(encoding="utf-8") as handle:
        catalog = yaml.safe_load(handle)

    features_out: list[dict] = []
    policy_rule_features: list[str] = []

    for item in catalog["features"]:
        fid = item["feature_id"]
        if fid not in CLASSIFICATION:
            print(f"Missing classification for {fid}", file=sys.stderr)
            return 1

        primary, severity, secondary = CLASSIFICATION[fid]
        requires_baseline, can_learn, needs_approval = _flags(primary)

        if primary == "policy-rule":
            policy_rule_features.append(fid)

        replay_refs = []
        if item.get("replay_positive"):
            replay_refs.append(item["replay_positive"])
        if item.get("replay_negative"):
            replay_refs.append(item["replay_negative"])

        features_out.append(
            {
                "feature_id": fid,
                "primary_detection_class": primary,
                "secondary_detection_classes": secondary,
                "default_severity_floor": severity,
                "requires_baseline": requires_baseline,
                "can_be_feedback_learned": can_learn,
                "requires_approval_for_suppression": needs_approval,
                "required_context": list(CONTEXT_BY_CLASS[primary]),
                "server_stack_replay_refs": replay_refs,
            }
        )

    document = {
        "version": "1.0",
        "total_features": 81,
        "policy_rule_features": sorted(policy_rule_features),
        "features": features_out,
    }

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    with OUTPUT.open("w", encoding="utf-8") as handle:
        yaml.dump(
            document,
            handle,
            allow_unicode=True,
            sort_keys=False,
            default_flow_style=False,
        )

    print(f"Wrote {len(features_out)} features to {OUTPUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
