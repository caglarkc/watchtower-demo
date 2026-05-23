"""LLM call audit persistence."""

from __future__ import annotations

from watchtower.llm.providers.mock import mock_openai
from tests.llm.conftest import valid_alert_explanation_json


def test_llm_call_writes_audit(gateway_with_db_audit, app, tenant_id):
    gw = gateway_with_db_audit([mock_openai([valid_alert_explanation_json()])])
    result = gw.invoke("alert_explanation", "audit me", tenant_id=tenant_id)
    assert result.success
    with app.session() as session:
        count = session.conn.execute(
            "SELECT COUNT(*) FROM llm_call_audit WHERE tenant_id = ?",
            (tenant_id,),
        ).fetchone()[0]
    assert count >= 1
