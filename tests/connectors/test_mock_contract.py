"""Mock connector protocol contract tests."""

from __future__ import annotations

from watchtower.connectors.mock import MockConnector
from watchtower.domain.events import ConnectorCursor, RawEventRecord


def test_mock_connector_contract_roundtrip():
    events = [
        RawEventRecord(dedupe_key=f"k{i}", payload={"n": i}) for i in range(5)
    ]
    connector = MockConnector("mock-1", events=events)
    health = connector.health()
    assert health.status == "healthy"

    hint = connector.schema_hint()
    assert hint.format == "mock"

    cursor = ConnectorCursor()
    batch = connector.poll(cursor, limit=2)
    assert len(batch.events) == 2
    assert batch.has_more is True

    connector.ack(batch.next_cursor)
    assert connector.acked_cursor is not None
    assert connector.acked_cursor.data["index"] == 2

    batch2 = connector.poll(batch.next_cursor, limit=10)
    assert len(batch2.events) == 3
    assert batch2.has_more is False


def test_mock_connector_health_failure():
    connector = MockConnector("mock-2", fail_health=True)
    try:
        connector.health()
    except Exception:
        pass
    else:
        raise AssertionError("expected health failure")
