"""Approval workflow and scoped feedback-rule application."""

from __future__ import annotations

from datetime import UTC, datetime

from watchtower.domain.rules import (
    ApproverRole,
    DecisionContext,
    FeedbackRule,
    PendingRule,
    RuleApplicationResult,
    RuleApproval,
    RuleEffect,
)
from watchtower.rules.scope import scope_matches
from watchtower.storage.repositories.feedback_rules import FeedbackRulesRepository
from watchtower.taxonomy.loader import load_feature_taxonomy

_APPROVER_ROLES: frozenset[str] = frozenset({"security_operator", "system_admin"})


class RuleEngine:
    """pending -> approved/rejected -> stable feedback_rule with audit trail."""

    def __init__(self, repo: FeedbackRulesRepository) -> None:
        self._repo = repo
        self._taxonomy = load_feature_taxonomy()

    def approve_pending_rule(
        self,
        tenant_id: str,
        pending_rule_id: str,
        *,
        approver_id: str,
        approver_role: ApproverRole,
        comment: str | None = None,
        allow_policy_suppression: bool = False,
    ) -> FeedbackRule:
        if approver_role not in _APPROVER_ROLES:
            msg = f"Role {approver_role} cannot approve rules"
            raise PermissionError(msg)

        pending = self._require_pending(tenant_id, pending_rule_id)
        now = datetime.now(UTC)

        effect = pending.effect.model_copy()
        if pending.requires_policy_suppression_approval:
            effect.suppress_alert = allow_policy_suppression
            effect.policy_suppression_approved = allow_policy_suppression
            if allow_policy_suppression:
                effect.effect_type = "suppress"
        elif effect.suppress_alert:
            effect.policy_suppression_approved = True

        pending.status = "approved"
        pending.reviewed_at = now
        pending.reviewed_by = approver_id
        pending.review_comment = comment
        self._repo.update_pending_rule(pending)

        approval = RuleApproval(
            id=self._repo.new_id(),
            tenant_id=tenant_id,
            pending_rule_id=pending.id,
            decision="approved",
            approver_id=approver_id,
            approver_role=approver_role,
            allow_policy_suppression=allow_policy_suppression,
            comment=comment,
            created_at=now,
        )
        self._repo.insert_rule_approval(approval)

        stable = FeedbackRule(
            id=self._repo.new_id(),
            tenant_id=tenant_id,
            pending_rule_id=pending.id,
            feedback_event_id=pending.feedback_event_id,
            scope=pending.scope,
            effect=effect,
            approved_by=approver_id,
            approved_at=now,
            expires_at=pending.expires_at,
            active=True,
        )
        self._repo.insert_feedback_rule(stable)
        return stable

    def reject_pending_rule(
        self,
        tenant_id: str,
        pending_rule_id: str,
        *,
        approver_id: str,
        approver_role: ApproverRole,
        comment: str | None = None,
    ) -> PendingRule:
        if approver_role not in _APPROVER_ROLES:
            msg = f"Role {approver_role} cannot reject rules"
            raise PermissionError(msg)

        pending = self._require_pending(tenant_id, pending_rule_id)
        now = datetime.now(UTC)
        pending.status = "rejected"
        pending.reviewed_at = now
        pending.reviewed_by = approver_id
        pending.review_comment = comment
        self._repo.update_pending_rule(pending)

        approval = RuleApproval(
            id=self._repo.new_id(),
            tenant_id=tenant_id,
            pending_rule_id=pending.id,
            decision="rejected",
            approver_id=approver_id,
            approver_role=approver_role,
            comment=comment,
            created_at=now,
        )
        self._repo.insert_rule_approval(approval)
        return pending

    def apply_feedback_rules(
        self,
        ctx: DecisionContext,
        *,
        as_of: datetime | None = None,
    ) -> RuleApplicationResult:
        """Apply only approved, active, non-expired feedback rules."""
        now = as_of or datetime.now(UTC)
        entry = self._taxonomy.by_id().get(ctx.feature_id)

        for pending in self._repo.list_pending_rules(ctx.tenant_id, status="pending"):
            if scope_matches(pending.scope, ctx):
                return RuleApplicationResult(
                    matched=True,
                    reason="pending_rule_not_approved",
                    pending_rule_id=pending.id,
                )

        best: FeedbackRule | None = None
        for rule in self._repo.list_active_feedback_rules(ctx.tenant_id):
            if rule.expires_at is not None and rule.expires_at < now:
                continue
            if scope_matches(rule.scope, ctx):
                best = rule
                break

        if best is None:
            return RuleApplicationResult(matched=False)

        return self._apply_stable_rule(best, ctx, entry)

    def _apply_stable_rule(
        self,
        rule: FeedbackRule,
        ctx: DecisionContext,
        entry: object | None,
    ) -> RuleApplicationResult:
        effect = rule.effect
        suppress = effect.suppress_alert
        policy_blocked = False

        detection = ctx.detection_class or (
            getattr(entry, "primary_detection_class", None) if entry else None
        )
        needs_policy_approval = bool(
            entry and getattr(entry, "requires_approval_for_suppression", False)
        ) or detection == "policy-rule"

        if suppress and needs_policy_approval and not effect.policy_suppression_approved:
            suppress = False
            policy_blocked = True

        return RuleApplicationResult(
            matched=True,
            downrank=effect.effect_type == "downrank" or effect.severity_delta < 0,
            suppress_alert=suppress,
            severity_delta=effect.severity_delta,
            applied_rule_id=rule.id,
            reason="feedback_rule_applied",
            policy_suppression_blocked=policy_blocked,
        )

    def evaluate_pending_only(
        self,
        tenant_id: str,
        ctx: DecisionContext,
    ) -> RuleApplicationResult:
        """Check pending rules without applying stable rules (pre-approval)."""
        for pending in self._repo.list_pending_rules(tenant_id, status="pending"):
            if scope_matches(pending.scope, ctx):
                return RuleApplicationResult(
                    matched=True,
                    reason="pending_rule_not_approved",
                    pending_rule_id=pending.id,
                )
        return RuleApplicationResult(matched=False)

    def _require_pending(self, tenant_id: str, rule_id: str) -> PendingRule:
        pending = self._repo.get_pending_rule(tenant_id, rule_id)
        if pending is None:
            msg = f"Pending rule not found: {rule_id}"
            raise ValueError(msg)
        if pending.status != "pending":
            msg = f"Pending rule not in pending state: {pending.status}"
            raise ValueError(msg)
        return pending
