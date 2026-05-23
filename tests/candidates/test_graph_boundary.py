"""Raw events must not enter the decision graph directly."""

from __future__ import annotations

import inspect

from watchtower.candidates.extractor import CandidateExtractor
from watchtower.domain.normalized_event import CandidateEvent, NormalizedEvent
from watchtower.domain.events import RawEventRecord


def test_extractor_only_accepts_normalized_event():
    sig = inspect.signature(CandidateExtractor.extract)
    assert "normalized" in sig.parameters
    ann = sig.parameters["normalized"].annotation
    assert ann is NormalizedEvent or getattr(ann, "__name__", "") == "NormalizedEvent"


def test_candidate_requires_normalized_event_id():
    fields = CandidateEvent.model_fields
    assert "normalized_event_id" in fields
    assert fields["normalized_event_id"].is_required()


def test_raw_record_not_assignable_to_candidate():
    raw = RawEventRecord(dedupe_key="k", payload={"x": 1})
    assert not hasattr(raw, "feature_hint")
    extractor = CandidateExtractor()
    assert extractor.extract(raw) is None  # type: ignore[arg-type]
