#!/usr/bin/env python3
"""Prepare F-001 replay JSONL source + baseline for soak scripts."""

from __future__ import annotations

import argparse
from pathlib import Path

from tests.daemon.helpers import register_f001_jsonl_source, replay_events_to_jsonl
from tests.daemon.test_loop import _seed_f001_baseline
from tests.graph.conftest import set_tenant_mode
from watchtower.config.settings import WatchtowerSettings
from watchtower.services.app import create_app
from watchtower.services.bootstrap import BootstrapRequiredError


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--db", type=Path, required=True)
    parser.add_argument("--jsonl", type=Path, default=None)
    parser.add_argument("--mode", default="learn", choices=("learn", "run", "hybrid"))
    args = parser.parse_args()

    jsonl = args.jsonl or args.db.parent / "soak_f001.jsonl"
    replay_events_to_jsonl("F-001", jsonl)

    settings = WatchtowerSettings(database_path=args.db)
    app = create_app(settings=settings, run_migrations=True)

    with app.session() as session:
        try:
            tenant = session.bootstrap_service.get_default_tenant()
            if tenant is None:
                tenant, _ = session.bootstrap_service.bootstrap(
                    "soak-admin",
                    "soak@localhost",
                    "soak-change-me",
                )
            tenant_id = tenant.id
        except BootstrapRequiredError:
            tenant, _ = session.bootstrap_service.bootstrap(
                "soak-admin",
                "soak@localhost",
                "soak-change-me",
            )
            tenant_id = tenant.id
        session.conn.commit()

    register_f001_jsonl_source(app, tenant_id, jsonl, source_id="src-soak-f001")
    _seed_f001_baseline(app, tenant_id)
    set_tenant_mode(app, tenant_id, args.mode)
    print(f"soak prepared tenant={tenant_id} jsonl={jsonl} mode={args.mode}")


if __name__ == "__main__":
    main()
