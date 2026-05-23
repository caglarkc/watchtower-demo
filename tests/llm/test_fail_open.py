"""LLM unavailable fail-open."""

from __future__ import annotations

from watchtower.llm.gateway import FAIL_OPEN_NOTE
from watchtower.llm.providers.mock import mock_openai


def test_llm_unavailable_fail_open(gateway_with_audit):
    gw = gateway_with_audit(
        [mock_openai([], unavailable=True)]
    )
    result = gw.invoke("alert_explanation", "no providers")
    assert result.success is False
    assert result.fail_open is True
    assert result.note == FAIL_OPEN_NOTE
    assert result.data is None


def test_all_providers_fail_fail_open(gateway_with_audit):
    p1 = mock_openai(["{bad"], unavailable=False)
    gw = gateway_with_audit([p1])
    result = gw.invoke("alert_explanation", "bad forever")
    assert result.fail_open is True
    assert result.attempts >= 1
