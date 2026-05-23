"""Dependencies injected into graph nodes (engines, not math)."""

from __future__ import annotations

from dataclasses import dataclass

from watchtower.baseline.engine import BaselineEngine
from watchtower.decision.service import DecisionService
from watchtower.feedback.service import FeedbackService
from watchtower.rules.engine import RuleEngine
from watchtower.services.mode_controller import ModeController
from watchtower.storage.repositories.graph import GraphRepository


@dataclass
class GraphDeps:
    """Session-scoped services for graph node orchestration."""

    mode_controller: ModeController
    decision: DecisionService
    baseline: BaselineEngine
    feedback: FeedbackService
    rules: RuleEngine
    graph_repo: GraphRepository
