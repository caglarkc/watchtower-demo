"""Server-stack lab preflight (read-only)."""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path

from watchtower.config.paths import PROJECT_ROOT

SERVER_STACK_ROOT = PROJECT_ROOT / "server-stack"
FEATURE_REPLAYS = SERVER_STACK_ROOT / "simulation" / "feature_replays"
SCENARIO_REPLAYS = SERVER_STACK_ROOT / "simulation" / "scenarios"
LOGS_ROOT = SERVER_STACK_ROOT / "logs"
REAL_FINAL_GATE = SERVER_STACK_ROOT / "reports" / "real" / "coverage" / "real_final_gate.json"


@dataclass
class PreflightResult:
    ok: bool
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    feature_replay_count: int = 0
    scenario_replay_count: int = 0
    log_file_count: int = 0
    real_gate_pass: bool | None = None

    def raise_if_failed(self) -> None:
        if not self.ok:
            msg = "Server-stack preflight failed:\n" + "\n".join(self.errors)
            raise RuntimeError(msg)


def run_preflight(*, require_logs: bool = False) -> PreflightResult:
    """Verify server-stack test lab artifacts exist (no product code in server-stack)."""
    result = PreflightResult(ok=True)

    if not SERVER_STACK_ROOT.is_dir():
        result.ok = False
        result.errors.append(f"server-stack root missing: {SERVER_STACK_ROOT}")
        return result

    if not FEATURE_REPLAYS.is_dir():
        result.ok = False
        result.errors.append(f"feature replays missing: {FEATURE_REPLAYS}")
    else:
        result.feature_replay_count = len(list(FEATURE_REPLAYS.glob("F-*_positive.yaml")))

    if not SCENARIO_REPLAYS.is_dir():
        result.ok = False
        result.errors.append(f"scenario replays missing: {SCENARIO_REPLAYS}")
    else:
        result.scenario_replay_count = len(list(SCENARIO_REPLAYS.glob("S-*_positive.yaml")))

    if result.feature_replay_count != 81:
        result.ok = False
        result.errors.append(
            f"expected 81 feature replays, found {result.feature_replay_count}"
        )

    if result.scenario_replay_count != 83:
        result.ok = False
        result.errors.append(
            f"expected 83 scenario replays, found {result.scenario_replay_count}"
        )

    if LOGS_ROOT.is_dir():
        result.log_file_count = len(
            list(LOGS_ROOT.glob("**/*.jsonl")) + list(LOGS_ROOT.glob("**/*.log"))
        )
    elif require_logs:
        result.warnings.append(f"logs root missing: {LOGS_ROOT}")

    if REAL_FINAL_GATE.is_file():
        try:
            gate = json.loads(REAL_FINAL_GATE.read_text(encoding="utf-8"))
            result.real_gate_pass = gate.get("result") == "PASS"
            if not result.real_gate_pass:
                result.warnings.append(
                    f"real_final_gate.json result={gate.get('result')} (replays still usable)"
                )
        except json.JSONDecodeError:
            result.warnings.append("real_final_gate.json unreadable")
    else:
        result.warnings.append("real_final_gate.json not found")

    return result
