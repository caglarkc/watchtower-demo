#!/usr/bin/env python3
"""Generate S-001..S-083 deterministic replay YAML files."""

from __future__ import annotations

from pathlib import Path

import yaml

from scenario_lib import SCENARIOS, events_for_scenario, feature_ids_for, services_for_events

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "simulation" / "scenarios"


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    for meta in SCENARIOS:
        sid = meta["id"]
        for mode in ("positive", "negative"):
            events = events_for_scenario(sid, mode)
            doc = {
                "scenario_id": sid,
                "title": meta["title"],
                "mode": mode,
                "category": meta["category"],
                "user_role": meta["user_role"],
                "deterministic_seed": meta["seed"],
                "expected_severity": meta["severity"],
                "feature_ids": feature_ids_for(sid),
                "services": services_for_events(events),
                "events": events,
                "negative_control": {
                    "type": "baseline_replay",
                    "description": "Same scenario with sub-threshold feature signals",
                }
                if mode == "negative"
                else None,
                "expected_evidence": f"Multi-signal workflow for {meta['title']}",
            }
            if doc["negative_control"] is None:
                del doc["negative_control"]
            path = OUT / f"{sid}_{mode}.yaml"
            path.write_text(yaml.dump(doc, allow_unicode=True, sort_keys=False), encoding="utf-8")
        print(f"wrote {sid}_positive.yaml / {sid}_negative.yaml")
    print(f"total scenarios: {len(SCENARIOS)}")


if __name__ == "__main__":
    main()
