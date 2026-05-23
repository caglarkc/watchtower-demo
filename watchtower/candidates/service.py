"""Pipeline: raw → normalized → candidate (graph boundary)."""

from __future__ import annotations

from dataclasses import dataclass

from watchtower.candidates.extractor import CandidateExtractor
from watchtower.domain.normalized_event import NormalizationOutcome
from watchtower.normalization.service import NormalizationService
from watchtower.storage.repositories.candidate_event import CandidateEventRepository
from watchtower.storage.repositories.normalized_event import NormalizedEventRepository
from watchtower.storage.repositories.raw_event import RawEventRepository
from watchtower.storage.repositories.unknown_schema import UnknownSchemaRepository
from watchtower.taxonomy.loader import load_feature_taxonomy


@dataclass
class PipelineResult:
    processed: int = 0
    normalized: int = 0
    candidates: int = 0
    unknown: int = 0
    skipped: int = 0


class CandidatePipelineService:
    """Ensures raw events never flow directly into the decision graph."""

    def __init__(
        self,
        raw_events: RawEventRepository,
        normalized_events: NormalizedEventRepository,
        unknown_schema: UnknownSchemaRepository,
        candidates: CandidateEventRepository,
        normalizer: NormalizationService | None = None,
        extractor: CandidateExtractor | None = None,
    ) -> None:
        self._raw = raw_events
        self._normalized = normalized_events
        self._unknown = unknown_schema
        self._candidates = candidates
        self._normalizer = normalizer or NormalizationService()
        self._extractor = extractor or CandidateExtractor()
        self._taxonomy = load_feature_taxonomy()

    def process_outcome(
        self,
        outcome: NormalizationOutcome,
        *,
        tenant_id: str,
    ) -> PipelineResult:
        result = PipelineResult(processed=1)
        if outcome.unknown is not None:
            entry = outcome.unknown.model_copy(update={"tenant_id": tenant_id})
            self._unknown.enqueue(entry)
            result.unknown = 1
            return result

        if outcome.normalized is None:
            result.skipped = 1
            return result

        normalized = self._normalized.insert(
            outcome.normalized.model_copy(update={"tenant_id": tenant_id})
        )
        result.normalized = 1

        if normalized.feature_hint and not self._taxonomy_feature_valid(
            normalized.feature_hint
        ):
            normalized = normalized.model_copy(update={"feature_hint": None})

        candidate = self._extractor.extract(normalized)
        if candidate is None:
            return result

        candidate = candidate.model_copy(
            update={
                "normalized_event_id": normalized.id or "",
                "tenant_id": tenant_id,
            }
        )
        self._candidates.insert(candidate)
        result.candidates = 1
        return result

    def process_raw_batch(self, tenant_id: str, *, limit: int = 500) -> PipelineResult:
        totals = PipelineResult()
        rows = self._raw.list_unprocessed(tenant_id, limit=limit)
        for row in rows:
            outcome = self._normalizer.normalize_payload(
                row["payload"],
                tenant_id=tenant_id,
                connector_type=row["connector_type"],
                raw_event_id=row["id"],
                source_id=row["source_id"],
                source_path=row["source_path"],
            )
            partial = self.process_outcome(outcome, tenant_id=tenant_id)
            totals.processed += partial.processed
            totals.normalized += partial.normalized
            totals.candidates += partial.candidates
            totals.unknown += partial.unknown
            totals.skipped += partial.skipped
        return totals

    def _taxonomy_feature_valid(self, feature_hint: str) -> bool:
        return feature_hint in self._taxonomy.feature_ids
