"""Parse suppression durations like 7d, 24h, 30m."""

from __future__ import annotations

import re
from datetime import UTC, datetime, timedelta

_DURATION_RE = re.compile(
    r"^(?P<value>\d+)\s*(?P<unit>d|day|days|h|hr|hour|hours|m|min|mins|minute|minutes)$",
    re.IGNORECASE,
)


def parse_duration(duration: str, *, base: datetime | None = None) -> datetime:
    """Return expiry datetime for a duration string."""
    match = _DURATION_RE.match(duration.strip())
    if not match:
        msg = f"Invalid duration '{duration}'. Use forms like 7d, 24h, 30m"
        raise ValueError(msg)
    value = int(match.group("value"))
    unit = match.group("unit").lower()[0]
    start = base or datetime.now(UTC)
    if unit == "d":
        delta = timedelta(days=value)
    elif unit == "h":
        delta = timedelta(hours=value)
    else:
        delta = timedelta(minutes=value)
    return start + delta
