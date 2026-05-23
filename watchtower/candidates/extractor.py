"""Extract decision-graph candidates from normalized events only."""

from __future__ import annotations

import uuid

from watchtower.domain.normalized_event import CandidateEvent, NormalizedEvent
from watchtower.normalization.registry import NON_CANDIDATE_EVENT_TYPES


class CandidateExtractor:
    """Raw logs never enter the graph — only normalized → candidate."""

    def extract(self, normalized: NormalizedEvent) -> CandidateEvent | None:
        if normalized.event_type in NON_CANDIDATE_EVENT_TYPES:
            return None

        feature_hint = normalized.feature_hint
        if not feature_hint:
            return None

        actor = normalized.actor or "unknown"
        action = normalized.action or normalized.event_type
        resource = normalized.resource or normalized.event_type

        return CandidateEvent(
            id=str(uuid.uuid4()),
            tenant_id=normalized.tenant_id,
            normalized_event_id=normalized.id or "",
            feature_hint=feature_hint,
            actor=actor,
            action=action,
            resource=resource,
            occurred_at=normalized.occurred_at,
            scenario_id=normalized.scenario_id,
            anomaly_flag=normalized.anomaly_flag,
            attributes=dict(normalized.attributes),
        )
