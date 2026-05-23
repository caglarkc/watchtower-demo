"""Soak helpers: server-stack F-001 replay JSONL and pipeline evidence counts."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import yaml

from watchtower.candidates.extractor import CandidateExtractor
from watchtower.config.paths import PROJECT_ROOT
from watchtower.e2e.preflight import FEATURE_REPLAYS
from watchtower.e2e.replay import first_candidate_from_feature
from watchtower.normalization.service import NormalizationService
from watchtower.services.app import AppContext


def replay_events_to_jsonl(
    feature_id: str,
    path: Path,
    *,
    positive: bool = True,
) -> Path:
    suffix = "positive" if positive else "negative"
    replay_path = FEATURE_REPLAYS / f"{feature_id}_{suffix}.yaml"
    data = yaml.safe_load(replay_path.read_text(encoding="utf-8"))
    events: list[dict[str, Any]] = data.get("events", [])
    path.write_text(
        "\n".join(json.dumps(ev, ensure_ascii=False) for ev in events) + "\n",
        encoding="utf-8",
    )
    return path


def db_pipeline_counts(app: AppContext, tenant_id: str) -> dict[str, int]:
    with app.session() as session:
        conn = session.conn
        raw = conn.execute(
            "SELECT COUNT(*) FROM raw_events WHERE tenant_id = ?",
            (tenant_id,),
        ).fetchone()[0]
        normalized = conn.execute(
            "SELECT COUNT(*) FROM normalized_events WHERE tenant_id = ?",
            (tenant_id,),
        ).fetchone()[0]
        candidates = conn.execute(
            "SELECT COUNT(*) FROM candidate_events WHERE tenant_id = ?",
            (tenant_id,),
        ).fetchone()[0]
        graph_runs = conn.execute(
            "SELECT COUNT(*) FROM graph_runs WHERE tenant_id = ?",
            (tenant_id,),
        ).fetchone()[0]
        alerts = conn.execute(
            "SELECT COUNT(*) FROM alert_cases WHERE tenant_id = ?",
            (tenant_id,),
        ).fetchone()[0]
        silent = conn.execute(
            "SELECT COUNT(*) FROM silent_candidate_findings WHERE tenant_id = ?",
            (tenant_id,),
        ).fetchone()[0]
        learning = conn.execute(
            "SELECT COUNT(*) FROM controlled_learning_events WHERE tenant_id = ?",
            (tenant_id,),
        ).fetchone()[0]
    return {
        "raw_events": int(raw),
        "normalized_events": int(normalized),
        "candidate_events": int(candidates),
        "graph_runs": int(graph_runs),
        "alerts": int(alerts),
        "silent_findings": int(silent),
        "learning_events": int(learning),
    }


def register_f001_jsonl_source(
    app: AppContext,
    tenant_id: str,
    jsonl_path: Path,
    *,
    source_id: str = "src-f001-jsonl",
) -> str:
    with app.session() as session:
        source = session.sources.create(
            tenant_id,
            "file_jsonl",
            "f001-replay",
            {"file_path": str(jsonl_path)},
            source_id=source_id,
        )
        session.conn.commit()
        return source.id


def seed_f001_baseline(app: AppContext, tenant_id: str) -> None:
    normalizer = NormalizationService()
    extractor = CandidateExtractor()
    candidate = first_candidate_from_feature(
        normalizer, extractor, tenant_id=tenant_id, feature_id="F-001"
    )
    if candidate is None:
        msg = "F-001 candidate required for baseline seed"
        raise RuntimeError(msg)
    from tests.e2e.conftest import seed_baseline_for_candidate

    seed_baseline_for_candidate(app, tenant_id, candidate)


def server_stack_log_available() -> bool:
    logs = PROJECT_ROOT / "server-stack" / "logs"
    return logs.is_dir() and any(logs.glob("**/*.jsonl"))


def set_tenant_mode(app: AppContext, tenant_id: str, mode: str) -> None:
    with app.session() as session:
        session.mode_controller.set_mode(tenant_id, mode)  # type: ignore[arg-type]
        session.conn.commit()
