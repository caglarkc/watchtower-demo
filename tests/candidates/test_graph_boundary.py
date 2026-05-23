"""Raw events must not enter the decision graph directly."""

from __future__ import annotations

import inspect
import typing

from watchtower.candidates.extractor import CandidateExtractor
from watchtower.domain.normalized_event import CandidateEvent, NormalizedEvent
from watchtower.domain.events import RawEventRecord


def test_extractor_only_accepts_normalized_event():
    sig = inspect.signature(CandidateExtractor.extract)
    assert "normalized" in sig.parameters
    ann = sig.parameters["normalized"].annotation
  if isinstance(ann, str):
        assert ann == "NormalizedEvent"
    else:
        assert ann is NormalizedEvent


def test_candidate_requires_normalized_event_id():
    fields = CandidateEvent.model_fields
    assert "normalized_event_id" in fields
    assert fields["normalized_event_id"].is_required()


def test_raw_record_is_not_normalized_type():
    raw = RawEventRecord(dedupe_key="k", payload={"x": 1})
    assert not isinstance(raw, NormalizedEvent)
    extractor = CandidateExtractor()
    # API contract: only NormalizedEvent is a valid input type
    hints = typing.get_type_hints(CandidateExtractor.extract)
    assert hints.get("normalized") is NormalizedEvent
