#!/usr/bin/env python3
"""Seed real file share data for RI-1."""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
FILES = ROOT / "seeds" / "real" / "files"

SHARES = ("finance", "hr", "legal", "dev", "public")
SAMPLES = {
    "finance": ["budget_2026.xlsx", "forecast_q1.csv"],
    "hr": ["payroll_jan.csv", "reviews_2025.docx"],
    "legal": ["contract_acme.pdf", "confidential_memo.txt"],
    "dev": ["source_module.py", "build_notes.md"],
    "public": ["announcement.txt"],
}


def main() -> int:
    for share in SHARES:
        d = FILES / share
        d.mkdir(parents=True, exist_ok=True)
        for name in SAMPLES.get(share, ["readme.txt"]):
            p = d / name
            if not p.exists():
                p.write_text(f"synthetic seed content for {share}/{name}\n", encoding="utf-8")
    classification = FILES / "classification.yml"
    if not classification.exists():
        classification.write_text(
            "version: '1.0'\nlabels:\n  - name: confidential\n    paths: [legal, hr/payroll]\n",
            encoding="utf-8",
        )
    baseline = ROOT / "seeds" / "real" / "baseline"
    baseline.mkdir(parents=True, exist_ok=True)
    for name, content in {
        "normal_day.yml": "work_hours: {start: 8, end: 18}\n",
        "peer_groups.yml": "groups:\n  - finance\n  - hr\n",
        "work_windows.yml": "roles:\n  CFO: {start: 7, end: 20}\n",
    }.items():
        p = baseline / name
        if not p.exists():
            p.write_text(content, encoding="utf-8")
    print(f"seed-real-files: wrote under {FILES}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
