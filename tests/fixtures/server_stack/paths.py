"""Server-stack lab paths for Watchtower E2E (read-only)."""

from watchtower.config.paths import PROJECT_ROOT

SERVER_STACK_ROOT = PROJECT_ROOT / "server-stack"
FEATURE_REPLAYS = SERVER_STACK_ROOT / "simulation" / "feature_replays"
SCENARIO_REPLAYS = SERVER_STACK_ROOT / "simulation" / "scenarios"
LOGS_ROOT = SERVER_STACK_ROOT / "logs"
REAL_FINAL_GATE = (
    SERVER_STACK_ROOT / "reports" / "real" / "coverage" / "real_final_gate.json"
)
