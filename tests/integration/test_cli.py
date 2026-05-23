"""CLI integration smoke tests."""

from __future__ import annotations

from pathlib import Path

from typer.testing import CliRunner

from watchtower.cli.main import app


def _invoke(db_path: Path, *args: str):
    runner = CliRunner()
    return runner.invoke(app, ["--db", str(db_path), *args])


def test_cli_status_before_bootstrap(db_path: Path):
    result = _invoke(db_path, "status")
    assert result.exit_code == 0
    assert "bootstrapped: False" in result.stdout
    assert "unavailable until bootstrap" in result.stdout


def test_cli_bootstrap_and_modes_get(db_path: Path):
    boot = _invoke(
        db_path,
        "bootstrap",
        "--username",
        "admin",
        "--email",
        "admin@corp.local",
        "--password",
        "test-pass-123",
    )
    assert boot.exit_code == 0, boot.stdout

    status = _invoke(db_path, "status")
    assert status.exit_code == 0
    assert "bootstrapped: True" in status.stdout
    assert "mode: learn" in status.stdout

    modes = _invoke(db_path, "modes", "get")
    assert modes.exit_code == 0
    assert modes.stdout.strip() == "learn"


def test_cli_modes_get_blocked_without_bootstrap(db_path: Path):
    result = _invoke(db_path, "modes", "get")
    assert result.exit_code == 1
    assert "bootstrap" in result.stdout.lower() or "bootstrap" in (result.stderr or "").lower()


def test_cli_mode_switch_learn_run_hybrid(db_path: Path):
    _invoke(
        db_path,
        "bootstrap",
        "-u",
        "admin",
        "-e",
        "a@b.c",
        "--password",
        "pw",
    )

    for mode in ("run", "hybrid"):
        set_result = _invoke(db_path, "modes", "set", mode)
        assert set_result.exit_code == 0, set_result.stdout

        get_result = _invoke(db_path, "modes", "get")
        assert get_result.exit_code == 0
        assert get_result.stdout.strip() == mode
