"""Case export to JSON and Markdown."""

from __future__ import annotations

import json
from typing import Any

from watchtower.domain.alerts import AlertDetailView


def export_case_json(detail: AlertDetailView) -> str:
    payload = {
        "alert": detail.alert.model_dump(mode="json"),
        "case": detail.case.model_dump(mode="json") if detail.case else None,
        "score_breakdown": detail.score_breakdown,
        "assessment": detail.assessment,
        "source_evidence": detail.source_evidence,
        "llm_explanation": detail.llm_explanation,
        "timeline": [e.model_dump(mode="json") for e in detail.timeline],
    }
    return json.dumps(payload, indent=2, ensure_ascii=False, default=str)


def export_case_markdown(detail: AlertDetailView) -> str:
    alert = detail.alert
    lines = [
        f"# Case Report — {alert.id}",
        "",
        f"- **Feature:** {alert.feature_id}",
        f"- **Severity:** {alert.severity}",
        f"- **Status:** {alert.status}",
        f"- **Title:** {alert.title}",
        "",
        "## Score breakdown",
    ]
    breakdown = detail.score_breakdown or {}
    for comp in breakdown.get("components", []):
        lines.append(
            f"- `{comp.get('source')}`: **{comp.get('points')}** — {comp.get('reason')}"
        )
    if not breakdown.get("components"):
        lines.append("- (no breakdown stored)")
    lines.extend(["", "## Timeline"])
    for entry in detail.timeline:
        meta = entry.metadata
        extra = f" {meta}" if meta else ""
        lines.append(
            f"- `{entry.created_at.isoformat()}` **{entry.event_type}** "
            f"by {entry.actor or 'system'}{extra}"
        )
        if entry.comment:
            lines.append(f"  - {entry.comment}")
    if detail.llm_explanation:
        lines.extend(["", "## LLM explanation", "```json"])
        lines.append(json.dumps(detail.llm_explanation, indent=2, default=str))
        lines.append("```")
    return "\n".join(lines) + "\n"
