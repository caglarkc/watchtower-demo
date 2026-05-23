"""CLI case commands smoke test."""

from __future__ import annotations

from pathlib import Path

from typer.testing import CliRunner

from watchtower.cli.main import app as cli_app
from tests.alerts.helpers import produce_real_alert_via_graph


def test_cli_cases_timeline_and_export(tenant_id, app):
    alert_id, case_id, _ = produce_real_alert_via_graph(app, tenant_id)
    db = str(app.settings.database_path)
    runner = CliRunner()

    tl = runner.invoke(cli_app, ["--db", db, "cases", "timeline", case_id])
    assert tl.exit_code == 0, tl.stdout
    assert "created" in tl.stdout

    exported = runner.invoke(
        cli_app, ["--db", db, "cases", "export", case_id, "--format", "md"]
    )
    assert exported.exit_code == 0
    assert alert_id[:8] in exported.stdout or case_id[:8] in exported.stdout
