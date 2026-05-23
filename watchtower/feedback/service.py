"""Manager/operator feedback — always produces pending_rule, never stable rule."""

from __future__ import annotations

from datetime import UTC, datetime, timedelta

from watchtower.domain.rules import (
    FeedbackActorRole,
    FeedbackEvent,
    FeedbackKind,
    PendingRule,
    RuleEffect,
    RuleScope,
)
from watchtower.storage.repositories.feedback_rules import FeedbackRulesRepository
from watchtower.taxonomy.loader import load_feature_taxonomy


_PENDING_KINDS: frozenset[FeedbackKind] = frozenset(
    {
        "expected_behavior",
        "false_positive",
        "temporary_exception",
        "project_context",
    }
)


class FeedbackService:
    """Record feedback and draft pending rules (approval required for stable rules)."""

    def __init__(self, repo: FeedbackRulesRepository) -> None:
        self._repo = repo
        self._taxonomy = load_feature_taxonomy()

    def submit_feedback(
        self,
        tenant_id: str,
        *,
        kind: FeedbackKind,
        actor_id: str,
        actor_role: FeedbackActorRole,
        feature_id: str | None = None,
        detection_class: str | None = None,
        candidate_id: str | None = None,
        scope: RuleScope | None = None,
        comment: str | None = None,
        expires_in_days: int | None = None,
    ) -> tuple[FeedbackEvent, PendingRule | None]:
        """Manager/operator feedback never creates a stable feedback_rule directly."""
        now = datetime.now(UTC)
        resolved_scope = scope or RuleScope()
        if feature_id and resolved_scope.feature_id is None:
            resolved_scope = resolved_scope.model_copy(update={"feature_id": feature_id})

        entry = self._taxonomy.by_id().get(feature_id) if feature_id else None
        if detection_class is None and entry is not None:
            detection_class = entry.primary_detection_class

        event = FeedbackEvent(
            id=self._repo.new_id(),
            tenant_id=tenant_id,
            kind=kind,
            actor_id=actor_id,
            actor_role=actor_role,
            feature_id=feature_id,
            detection_class=detection_class,
            candidate_id=candidate_id,
            scope=resolved_scope,
            comment=comment,
            created_at=now,
        )
        self._repo.insert_feedback_event(event)

        if kind not in _PENDING_KINDS:
            return event, None

        pending = self._build_pending_rule(
            tenant_id=tenant_id,
            event=event,
            actor_id=actor_id,
            actor_role=actor_role,
            now=now,
            expires_in_days=expires_in_days,
        )
        self._repo.insert_pending_rule(pending)
        return event, pending

    def _build_pending_rule(
        self,
        *,
        tenant_id: str,
        event: FeedbackEvent,
        actor_id: str,
        actor_role: FeedbackActorRole,
        now: datetime,
        expires_in_days: int | None,
    ) -> PendingRule:
        entry = self._taxonomy.by_id().get(event.feature_id) if event.feature_id else None
        requires_policy = bool(
            entry and entry.requires_approval_for_suppression
        )
        wants_suppress = event.kind in ("false_positive", "temporary_exception")
        suppress = wants_suppress and not requires_policy

        effect = RuleEffect(
            effect_type="suppress" if suppress else "downrank",
            severity_delta=-2 if event.kind != "true_positive" else 0,
            suppress_alert=suppress,
            suppression_requested=wants_suppress and requires_policy,
            policy_suppression_approved=False,
        )
        expires_at = None
        if expires_in_days is not None:
            expires_at = now + timedelta(days=expires_in_days)
        elif event.kind == "temporary_exception":
            expires_at = now + timedelta(days=7)

        return PendingRule(
            id=self._repo.new_id(),
            tenant_id=tenant_id,
            feedback_event_id=event.id,
            status="pending",
            scope=event.scope,
            effect=effect,
            proposed_by=actor_id,
            proposed_role=actor_role,
            requires_policy_suppression_approval=requires_policy,
            expires_at=expires_at,
            created_at=now,
        )
