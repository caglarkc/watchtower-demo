#!/usr/bin/env python3
"""Seed HRIS, badge, print docs, CRM records for RI-4."""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def main() -> int:
    hris = ROOT / "seeds" / "real" / "hris"
    write(
        hris / "employees.yml",
        "employees:\n"
        "  - id: E001\n    name: Alice CFO\n    status: active\n    role: finance\n"
        "  - id: E003\n    name: Carol Leaver\n    status: terminated\n"
        "  - id: E004\n    name: Dan Contractor\n    identity: contractor\n"
        "  - id: E005\n    name: Eve Newhire\n    hire_day: 1\n",
    )
    write(
        hris / "lifecycle.yml",
        "events:\n  - offboarding\n  - leave\n  - role_change\n  - new_hire\n  - contractor_scope\n",
    )

    badge = ROOT / "seeds" / "real" / "badge"
    write(
        badge / "locations.yml",
        "locations:\n  - floor-3\n  - floor-b1\n  - lobby\n  - datacenter\n",
    )
    write(
        badge / "shifts.yml",
        "shifts:\n  day: [08:00, 18:00]\n  off: []\n",
    )

    print_dir = ROOT / "seeds" / "real" / "print"
    print_dir.mkdir(parents=True, exist_ok=True)
    doc = print_dir / "confidential-report.pdf"
    if not doc.exists():
        doc.write_bytes(b"%PDF-1.4\n% SYNTHETIC CONFIDENTIAL PRINT DOC\n" * 50)

    crm = ROOT / "seeds" / "real" / "crm"
    write(
        crm / "records.yml",
        "records:\n  - id: contract-991\n    type: opportunity\n    classification: confidential\n"
        "  - id: account-220\n    type: account\n",
    )
    write(
        crm / "access_policy.yml",
        "policy:\n  max_users_per_record: 2\n  audit_channel: suitecrm\n",
    )

    print(f"seed-real-physical-hr: hris + badge + print + crm under {ROOT / 'seeds' / 'real'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
