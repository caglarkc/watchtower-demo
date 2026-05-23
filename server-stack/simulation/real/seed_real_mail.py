#!/usr/bin/env python3
"""Seed real mail fixtures for RI-2."""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
MAIL = ROOT / "seeds" / "real" / "mail"


def write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def main() -> int:
    write(
        MAIL / "mailboxes.yml",
        "mailboxes:\n  - user: cfo@corp.local\n    quota_mb: 5120\n  - user: finance@corp.local\n",
    )
    write(
        MAIL / "distribution_lists.yml",
        "lists:\n  - name: all-staff@corp.local\n    members: 120\n",
    )
    write(
        MAIL / "forwarding_rules.yml",
        "rules: []\n",
    )
    (MAIL / "attachments").mkdir(parents=True, exist_ok=True)
    att = MAIL / "attachments" / "sample.pdf"
    if not att.exists():
        att.write_bytes(b"%PDF-1.4 synthetic attachment\n")
    print(f"seed-real-mail: wrote {MAIL}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
