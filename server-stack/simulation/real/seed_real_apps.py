#!/usr/bin/env python3
"""Seed postgres, git, web fixtures for RI-2."""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def main() -> int:
    pg = ROOT / "seeds" / "real" / "postgres"
    pg.mkdir(parents=True, exist_ok=True)
    (pg / "schema.sql").write_text(
        (ROOT / "configs" / "postgres" / "init.sql").read_text(encoding="utf-8"),
        encoding="utf-8",
    )
    (pg / "pii_customers.csv").write_text("id,name,email\n1,Acme,a@acme.corp\n", encoding="utf-8")
    (pg / "payroll.csv").write_text("employee,salary\nalice,50000\n", encoding="utf-8")

    git = ROOT / "seeds" / "real" / "git"
    git.mkdir(parents=True, exist_ok=True)
    (git / "repos.yml").write_text("repos:\n  - name: corp/demo\n    visibility: internal\n", encoding="utf-8")
    (git / "repo_templates").mkdir(exist_ok=True)

    web = ROOT / "seeds" / "real" / "web"
    web.mkdir(parents=True, exist_ok=True)
    (web / "api_users.yml").write_text("users:\n  - id: api1\n    role: analyst\n", encoding="utf-8")
    (web / "endpoints.yml").write_text(
        "endpoints:\n  - path: /api/reports\n  - path: /api/admin\n",
        encoding="utf-8",
    )
    (web / "access_patterns.yml").write_text("baseline_rps: 2\n", encoding="utf-8")

    print("seed-real-apps: postgres, git, web seeds ready")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
