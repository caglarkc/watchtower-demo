"""On-demand LLM explanations for alerts (does not change deterministic severity)."""

from __future__ import annotations

from typing import Any

from watchtower.domain.alerts import Alert, AlertDetailView
from watchtower.llm.gateway import LLMGateway, LLMGatewayResult


def build_explanation_prompt(detail: AlertDetailView) -> str:
    alert = detail.alert
    assessment = detail.assessment or {}
    breakdown = detail.score_breakdown or {}
    lines = [
        f"Feature {alert.feature_id} alert for operator review.",
        f"Deterministic severity: {alert.severity} (do not change).",
        f"Detection class: {assessment.get('detection_class', 'unknown')}.",
        f"User: {alert.user_id}, department: {alert.department_id}, resource: {alert.resource}.",
        "Explain risk factors and recommended investigation steps using the score breakdown.",
    ]
    if breakdown.get("components"):
        lines.append("Score components:")
        for comp in breakdown["components"][:12]:
            lines.append(f"  - {comp.get('source')}: {comp.get('points')} pts — {comp.get('reason')}")
    return "\n".join(lines)


def explain_alert(
    gateway: LLMGateway,
    detail: AlertDetailView,
    *,
    tenant_id: str,
) -> tuple[dict[str, Any], LLMGatewayResult]:
    """Generate explanation; severity remains from deterministic assessment."""
    prompt = build_explanation_prompt(detail)
    context = {
        "alert_id": detail.alert.id,
        "severity_locked": detail.alert.severity,
        "assessment": detail.assessment,
        "score_breakdown": detail.score_breakdown,
        "source_evidence": detail.source_evidence,
    }
    result = gateway.invoke(
        "alert_explanation",
        prompt,
        tenant_id=tenant_id,
        context=context,
    )
    if result.success and result.data is not None:
        payload = {
            "skipped": False,
            "provider": result.provider,
            "model": result.model,
            "data": result.data.model_dump(),
            "severity_unchanged": detail.alert.severity,
        }
    else:
        payload = {
            "skipped": False,
            "fail_open": True,
            "note": result.note,
            "severity_unchanged": detail.alert.severity,
        }
    return payload, result
