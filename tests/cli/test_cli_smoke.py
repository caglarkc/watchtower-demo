"""CLI smoke tests (no Telegram)."""

from __future__ import annotations

from typer.testing import CliRunner

from watchtower.cli.main import app
from watchtower.services.app import create_app
from watchtower.config.settings import WatchtowerSettings


def test_cli_smoke_commands(tmp_path):
    db = tmp_path / "cli.db"
    settings = WatchtowerSettings(database_path=db)
    wt_app = create_app(settings=settings)
    runner = CliRunner()

    result = runner.invoke(
        app,
        ["--db", str(db), "bootstrap", "--username", "admin", "--password", "secret123"],
        obj=wt_app,
    )
    assert result.exit_code == 0, result.output

    for args in [
        ["--db", str(db), "status"],
        ["--db", str(db), "modes", "get"],
        ["--db", str(db), "modes", "set", "learn"],
        ["--db", str(db), "sources", "list"],
    ]:
        r = runner.invoke(app, args, obj=wt_app)
        assert r.exit_code == 0, r.output

    assert "telegram" not in result.output.lower()


def test_cli_alerts_and_query(tmp_path):
    db = tmp_path / "cli2.db"
    settings = WatchtowerSettings(database_path=db)
    wt_app = create_app(settings=settings)
    runner = CliRunner()
    runner.invoke(
        app,
        ["--db", str(db), "bootstrap", "--username", "admin", "--password", "secret123"],
        obj=wt_app,
    )
    with wt_app.session() as session:
        tenant_id = session.bootstrap_service.get_default_tenant().id
        alert, _ = session.alerts.create_alert(
            tenant_id,
            feature_id="F-010",
            severity="CRITICAL",
            title="test",
            department_id="backend",
        )

    show = runner.invoke(
        app, ["--db", str(db), "alerts", "show", alert.id], obj=wt_app
    )
    assert show.exit_code == 0
    assert "CRITICAL" in show.output

    q = runner.invoke(
        app,
        ["--db", str(db), "query", "son 24 saatte kritik backend anomalileri"],
        obj=wt_app,
    )
    assert q.exit_code == 0
    assert "auditable query_id=" in q.output
    assert "Alerts matched" in q.output
