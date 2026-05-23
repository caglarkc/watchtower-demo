#!/usr/bin/env python3
"""Write resumable soak summary JSON from database pipeline evidence."""

from __future__ import annotations

import argparse
import json
from datetime import UTC, datetime
from pathlib import Path

from watchtower.config.settings import WatchtowerSettings
from watchtower.observability.metrics import (
    METRIC_EVENTS_POLLED,
    METRIC_GRAPH_RUNS,
    METRIC_RAW_STORED,
)
from watchtower.services.app import create_app
from tests.daemon.helpers import db_pipeline_counts


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--db", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--label", default="short_soak")
    args = parser.parse_args()

    settings = WatchtowerSettings(database_path=args.db)
    app = create_app(settings=settings, run_migrations=True)
    with app.session() as session:
        tenant = session.bootstrap_service.get_default_tenant()
        if tenant is None:
            raise SystemExit("not bootstrapped")
        tenant_id = tenant.id
        counts = db_pipeline_counts(app, tenant_id)
        metrics = session.metrics.snapshot(tenant_id).to_dict()

    payload = {
        "label": args.label,
        "finished_at": datetime.now(UTC).isoformat(),
        "pipeline_counts": counts,
        "metrics": metrics,
        "passed": counts["raw_events"] >= 1
        and counts["normalized_events"] >= 1
        and counts["graph_runs"] >= 1
        and metrics.get("counters", {}).get(METRIC_RAW_STORED, 0) >= 1
        and metrics.get("counters", {}).get(METRIC_EVENTS_POLLED, 0) >= 1
        and metrics.get("counters", {}).get(METRIC_GRAPH_RUNS, 0) >= 1,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(json.dumps(payload, indent=2))
    if not payload["passed"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
