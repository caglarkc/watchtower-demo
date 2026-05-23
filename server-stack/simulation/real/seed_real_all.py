#!/usr/bin/env python3
"""Idempotent RI-0 real seed directory bootstrap."""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SEEDS = ROOT / "seeds" / "real"

DIRS = [
    "identity",
    "files/finance",
    "files/hr",
    "files/legal",
    "files/dev",
    "files/public",
    "mail/attachments",
    "postgres",
    "git/repo_templates",
    "web",
    "vault",
    "hris",
    "badge",
    "ai/uploads",
    "baseline",
]

PLACEHOLDER_FILES = {
    "identity/users.csv": "user_id,display_name,department,role\n",
    "identity/groups.csv": "group_id,group_name\n",
    "files/classification.yml": "version: '1.0'\nlabels: []\n",
    "baseline/normal_day.yml": "version: '1.0'\n",
    "baseline/peer_groups.yml": "version: '1.0'\n",
    "baseline/work_windows.yml": "version: '1.0'\n",
}


def main() -> int:
    import subprocess
    import sys

    here = Path(__file__).resolve().parent
    for script in (
        "seed_real_identity.py",
        "seed_real_files.py",
        "seed_real_mail.py",
        "seed_real_apps.py",
        "seed_real_security.py",
        "seed_real_endpoint.py",
        "seed_real_physical_hr.py",
    ):
        subprocess.run([sys.executable, str(here / script)], check=True)

    for d in DIRS:
        (SEEDS / d).mkdir(parents=True, exist_ok=True)
    for rel, content in PLACEHOLDER_FILES.items():
        path = SEEDS / rel
        if not path.exists():
            path.write_text(content, encoding="utf-8")
    readme = SEEDS / "README.md"
    if not readme.exists():
        readme.write_text(
            "# Real integration seeds (RI-0)\n\n"
            "Synthetic PII-free corporate fixtures. Expanded in RI-1+.\n",
            encoding="utf-8",
        )
    print(f"seed-real-all: ready under {SEEDS}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
