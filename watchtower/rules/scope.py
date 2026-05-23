"""Scope matching for feedback rules."""

from __future__ import annotations

from datetime import datetime

from watchtower.domain.rules import DecisionContext, RuleScope


def _time_in_window(occurred_at: datetime, start: str | None, end: str | None) -> bool:
    if start is None and end is None:
        return True
    t = occurred_at.time()
    if start is not None:
        sh, sm = (int(x) for x in start.split(":", 1))
        if t < occurred_at.replace(hour=sh, minute=sm, second=0, microsecond=0).time():
            return False
    if end is not None:
        eh, em = (int(x) for x in end.split(":", 1))
        if t > occurred_at.replace(hour=eh, minute=em, second=0, microsecond=0).time():
            return False
    return True


def scope_matches(scope: RuleScope, ctx: DecisionContext) -> bool:
    """Return True when all non-null scope dimensions match the decision context."""
    if scope.feature_id is not None and scope.feature_id != ctx.feature_id:
        return False
    if scope.user_id is not None and scope.user_id != ctx.user_id:
        return False
    if scope.role_id is not None and scope.role_id != ctx.role_id:
        return False
    if scope.department_id is not None and scope.department_id != ctx.department_id:
        return False
    if scope.resource is not None and scope.resource != ctx.resource:
        return False
    if scope.action is not None and scope.action != ctx.action:
        return False
    if scope.pattern_key is not None and scope.pattern_key != ctx.pattern_key:
        return False
    if ctx.volume is not None:
        if scope.volume_min is not None and ctx.volume < scope.volume_min:
            return False
        if scope.volume_max is not None and ctx.volume > scope.volume_max:
            return False
    elif scope.volume_min is not None or scope.volume_max is not None:
        return False
    if not _time_in_window(ctx.occurred_at, scope.time_start, scope.time_end):
        return False
    return True
