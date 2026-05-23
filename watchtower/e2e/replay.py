"""Load server-stack replay YAML into Watchtower pipeline (read-only source)."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml

from watchtower.candidates.extractor import CandidateExtractor
from watchtower.config.paths import PROJECT_ROOT
from watchtower.domain.normalized_event import CandidateEvent, NormalizedEvent
from watchtower.e2e.preflight import FEATURE_REPLAYS, SCENARIO_REPLAYS
from watchtower.normalization.service import NormalizationService

FEATURE_IDS = [f"F-{i:03d}" for i in range(1, 82)]
SCENARIO_IDS = [f"S-{i:03d}" for i in range(1, 84)]


@dataclass
class ReplayIngestResult:
    replay_id: str
    events_total: int
    normalized_count: int
    candidate_count: int
    feature_ids: set[str]


def load_feature_replay(feature_id: str, *, positive: bool = True) -> dict[str, Any]:
    suffix = "positive" if positive else "negative"
    path = FEATURE_REPLAYS / f"{feature_id}_{suffix}.yaml"
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def load_scenario_replay(scenario_id: str, *, positive: bool = True) -> dict[str, Any]:
    suffix = "positive" if positive else "negative"
    path = SCENARIO_REPLAYS / f"{scenario_id}_{suffix}.yaml"
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def ingest_replay_events(
    normalizer: NormalizationService,
    extractor: CandidateExtractor,
    *,
    tenant_id: str,
    replay_id: str,
    events: list[dict[str, Any]],
    context_feature_id: str | None = None,
) -> ReplayIngestResult:
    normalized_count = 0
    candidate_count = 0
    features: set[str] = set()

    for payload in events:
        outcome = normalizer.normalize_payload(
            payload,
            tenant_id=tenant_id,
            connector_type="simulation_fixture",
            context_feature_id=context_feature_id or payload.get("source_feature"),
        )
        if outcome.normalized is None:
            continue
        normalized_count += 1
        if outcome.normalized.feature_hint:
            features.add(outcome.normalized.feature_hint)
        if extractor.extract(outcome.normalized) is not None:
            candidate_count += 1

    return ReplayIngestResult(
        replay_id=replay_id,
        events_total=len(events),
        normalized_count=normalized_count,
        candidate_count=candidate_count,
        feature_ids=features,
    )


def ingest_feature_replay(
    normalizer: NormalizationService,
    extractor: CandidateExtractor,
    *,
    tenant_id: str,
    feature_id: str,
) -> ReplayIngestResult:
    data = load_feature_replay(feature_id)
    return ingest_replay_events(
        normalizer,
        extractor,
        tenant_id=tenant_id,
        replay_id=feature_id,
        events=data.get("events", []),
        context_feature_id=feature_id,
    )


def ingest_scenario_replay(
    normalizer: NormalizationService,
    extractor: CandidateExtractor,
    *,
    tenant_id: str,
    scenario_id: str,
) -> ReplayIngestResult:
    data = load_scenario_replay(scenario_id)
    return ingest_replay_events(
        normalizer,
        extractor,
        tenant_id=tenant_id,
        replay_id=scenario_id,
        events=data.get("events", []),
    )


def first_candidate_from_feature(
    normalizer: NormalizationService,
    extractor: CandidateExtractor,
    *,
    tenant_id: str,
    feature_id: str,
    prefer_anomaly: bool = True,
) -> CandidateEvent | None:
    data = load_feature_replay(feature_id)
    chosen: CandidateEvent | None = None
    for payload in data.get("events", []):
        if prefer_anomaly and not payload.get("anomaly"):
            continue
        outcome = normalizer.normalize_payload(
            payload,
            tenant_id=tenant_id,
            connector_type="simulation_fixture",
            context_feature_id=feature_id,
        )
        if outcome.normalized is None:
            continue
        cand = extractor.extract(outcome.normalized)
        if cand:
            _enrich_candidate_from_payload(cand, payload)
            return cand
    for payload in data.get("events", []):
        outcome = normalizer.normalize_payload(
            payload,
            tenant_id=tenant_id,
            connector_type="simulation_fixture",
            context_feature_id=feature_id,
        )
        if outcome.normalized is None:
            continue
        cand = extractor.extract(outcome.normalized)
        if cand:
            _enrich_candidate_from_payload(cand, payload)
            return cand
    return chosen


def _enrich_candidate_from_payload(candidate: CandidateEvent, payload: dict[str, Any]) -> None:
    attrs = dict(candidate.attributes)
    attrs.setdefault("user_id", payload.get("user") or payload.get("account"))
    attrs.setdefault("department_id", payload.get("department"))
    attrs.setdefault("role_id", payload.get("role"))
    attrs.setdefault("volume", float(payload.get("bytes_read") or payload.get("volume") or 0))
    attrs.setdefault("metric_name", payload.get("metric_name", "event_volume"))
    if payload.get("anomaly"):
        candidate.anomaly_flag = True
    candidate.attributes = attrs


def server_stack_connector_health(logs_root: Path | None = None) -> str:
    from watchtower.connectors.server_stack import ServerStackConnector

    root = logs_root or (PROJECT_ROOT / "server-stack" / "logs")
    connector = ServerStackConnector("e2e-server-stack", root, max_files=5)
    return connector.health().status
