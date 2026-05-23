"""CLI case commands smoke test."""

from __future__ import annotations

from pathlib import Path

from typer.testing import CliRunner

from watchtower.cli.main import app
from tests.alerts.helpers import produce_real_alert_via_graph


def test_cli_cases_timeline_and_export(db_path: Path, tenant_id, app):
    runner = CliRunner()
    boot = runner.invoke(
        app,
        ["--db", str(db_path), "bootstrap", "-u", "a", "-e", "a@b.c", "--password", "pw"],
    )
    assert boot.exit_code == 0

    alert_id, case_id, _ = produce_real_alert_via_graph(app, tenant_id)

    tl = runner.invoke(app, ["--db", str(db_path), "cases", "timeline", case_id])
    assert tl.exit_code == 0, tl.stdout
    assert "created" in tl.stdout

    exported = runner.invoke(
        app, ["--db", str(db_path), "cases", "export", case_id, "--format", "md"]
    )
    assert exported.exit_code == 0
    assert alert_id[:8] in exported.stdout or case_id[:8] in exported.stdout
