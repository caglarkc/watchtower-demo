"""Operating mode definitions."""

from __future__ import annotations

from typing import Literal

WatchtowerMode = Literal["learn", "run", "hybrid"]

VALID_MODES: frozenset[str] = frozenset({"learn", "run", "hybrid"})
DEFAULT_MODE: WatchtowerMode = "learn"
