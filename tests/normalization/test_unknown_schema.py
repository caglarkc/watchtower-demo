"""Unknown schema queue tests."""

from __future__ import annotations

from watchtower.domain.normalized_event import NormalizedEvent
from watchtower.normalization.service import NormalizationService


def test_unknown_schema_goes_to_queue(app, tenant_id):
    normalizer = NormalizationService()
    garbage = {"foo": "bar", "baz": 123}

    with app.session() as session:
        outcome = normalizer.normalize_payload(
            garbage,
            tenant_id=tenant_id,
            connector_type="server_stack",
        )
        assert outcome.normalized is None
        assert outcome.unknown is not None
        partial = session.pipeline.process_outcome(outcome, tenant_id=tenant_id)
        pending = session.unknown_schema.count_pending(tenant_id)

    assert partial.unknown == 1
    assert pending >= 1


def test_empty_payload_is_unknown(normalizer):
    outcome = normalizer.normalize_payload(
        {},
        tenant_id="t1",
        connector_type="file_jsonl",
    )
    assert outcome.unknown is not None
    assert outcome.normalized is None
