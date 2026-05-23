#!/usr/bin/env python3
"""Generate Phase 3 feature replay YAML files."""

from __future__ import annotations

from pathlib import Path

import yaml

from replay_templates_phase3 import PHASE3_TEMPLATES

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "simulation" / "feature_replays"


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    for fid, (pos, neg) in PHASE3_TEMPLATES.items():
        for mode, events in ("positive", pos), ("negative", neg):
            doc = {"feature_id": fid, "mode": mode, "phase": 3, "events": events}
            path = OUT / f"{fid}_{mode}.yaml"
            path.write_text(yaml.dump(doc, allow_unicode=True, sort_keys=False), encoding="utf-8")
            print(f"wrote {path}")
    print(f"total features: {len(PHASE3_TEMPLATES)}")


if __name__ == "__main__":
    main()
