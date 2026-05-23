#!/usr/bin/env python3
"""Seed endpoint behavior baselines for RI-3."""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
BASELINE = ROOT / "seeds" / "real" / "baseline"


def main() -> int:
    BASELINE.mkdir(parents=True, exist_ok=True)
    (BASELINE / "endpoint_roles.yml").write_text(
        "roles:\n  CFO:\n    servers: [files1, db1, app1]\n  dev:\n    servers: [git1]\n",
        encoding="utf-8",
    )
    (BASELINE / "dormant_systems.yml").write_text(
        "systems:\n  - id: legacy-etl\n    last_seen_days: 120\n",
        encoding="utf-8",
    )
    (BASELINE / "clipboard_thresholds.yml").write_text("max_bytes: 1000000\n", encoding="utf-8")
    print(f"seed-real-endpoint: wrote {BASELINE}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
