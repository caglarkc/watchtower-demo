"""CLI daemon run smoke tests."""

from __future__ import annotations

from pathlib import Path

from typer.testing import CliRunner

from watchtower.cli.main import app
from tests.daemon.helpers import replay_events_to_jsonl


def _invoke(db_path: Path, *args: str):
    runner = CliRunner()
    return runner.invoke(app, ["--db", str(db_path), *args])


def test_cli_daemon_run_once(db_path: Path, tmp_path: Path):
    jsonl = replay_events_to_jsonl("F-001", tmp_path / "f001.jsonl")

    boot = _invoke(
        db_path,
        "bootstrap",
        "-u",
        "admin",
        "-e",
        "admin@test.local",
        "--password",
        "test-pass-123",
    )
    assert boot.exit_code == 0, boot.stdout

    with open(db_path, "rb"):
        pass

    from watchtower.services.app import create_app
    from watchtower.config.settings import WatchtowerSettings
    from tests.daemon.helpers import register_f001_jsonl_source
    from tests.e2e.conftest import seed_baseline_for_candidate
    from tests.graph.conftest import set_tenant_mode
    from watchtower.candidates.extractor import CandidateExtractor
    from watchtower.e2e.replay import first_candidate_from_feature
    from watchtower.normalization.service import NormalizationService

    wt_app = create_app(settings=WatchtowerSettings(database_path=db_path))
    with wt_app.session() as session:
        tenant = session.bootstrap_service.get_default_tenant()
        assert tenant is not None
        tenant_id = tenant.id
    register_f001_jsonl_source(wt_app, tenant_id, jsonl)
    normalizer = NormalizationService()
    extractor = CandidateExtractor()
    candidate = first_candidate_from_feature(
        normalizer, extractor, tenant_id=tenant_id, feature_id="F-001"
    )
    assert candidate is not None
    seed_baseline_for_candidate(wt_app, tenant_id, candidate)
    set_tenant_mode(wt_app, tenant_id, "learn")

    result = _invoke(db_path, "daemon", "run", "--once")
    assert result.exit_code == 0, result.stdout + (result.stderr or "")
    assert "loop=1" in result.stdout
    assert "graph_runs=" in result.stdout
