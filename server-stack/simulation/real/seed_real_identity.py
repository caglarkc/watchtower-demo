#!/usr/bin/env python3
"""Seed real identity data for RI-1."""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
IDENTITY = ROOT / "seeds" / "real" / "identity"

USERS = """user_id,display_name,department,role,enabled
u001,CFO User,Finance,CFO,1
u002,Finance Analyst,Finance,Analyst,1
u003,HR Manager,HR,Manager,1
u004,Legal Counsel,Legal,Counsel,1
u005,Dev Lead,Engineering,Lead,1
u006,Service SQL,IT,ServiceAccount,1
u007,Contractor One,External,Contractor,1
"""

GROUPS = """group_id,group_name,members
g001,Domain Admins,u001
g002,Finance-RO,u002
g003,HR-Full,u003
g004,Legal-Confidential,u004
g005,Dev-Write,u005
g006,Service-Accounts,u006
"""

SERVICE_ACCOUNTS = """account,samAccountName,interactive_allowed
svc_sql,svc_sql,0
svc_backup,svc_backup,0
svc_monitor,svc_monitor,0
"""

CONTRACTORS = """contractor_id,display_name,valid_until
c001,Contractor One,2026-12-31
c002,Contractor Two,2026-06-30
"""


def write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def main() -> int:
    write(IDENTITY / "users.csv", USERS)
    write(IDENTITY / "groups.csv", GROUPS)
    write(IDENTITY / "service_accounts.csv", SERVICE_ACCOUNTS)
    write(IDENTITY / "contractors.csv", CONTRACTORS)
    write(
        IDENTITY / "org_units.ldif",
        "dn: OU=Finance,DC=corp,DC=local\nou: Finance\n\n"
        "dn: OU=HR,DC=corp,DC=local\nou: HR\n",
    )
    print(f"seed-real-identity: wrote {IDENTITY}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
