"""Tests for CLI commands."""

from __future__ import annotations

from pathlib import Path

from typer.testing import CliRunner

from autoheal.cli.app import app

runner = CliRunner()


class TestCLI:
    """Test CLI commands."""

    def test_version(self):
        """Test version command."""
        result = runner.invoke(app, ["version"])
        assert result.exit_code == 0
        assert "0.1.0" in result.output

    def test_help(self):
        """Test help output."""
        result = runner.invoke(app, ["--help"])
        assert result.exit_code == 0
        assert "AutoHeal" in result.output

    def test_init(self, temp_project: Path, monkeypatch):
        """Test init command."""
        monkeypatch.chdir(str(temp_project))
        result = runner.invoke(app, ["init", str(temp_project)])
        assert result.exit_code == 0
        assert (temp_project / ".autoheal" / "config.toml").exists()
        assert (temp_project / ".autoheal" / "autoheal.db").exists()

    def test_config_list(self, temp_project: Path, monkeypatch):
        """Test config list command after init."""
        monkeypatch.chdir(str(temp_project))
        runner.invoke(app, ["init", str(temp_project)])
        result = runner.invoke(app, ["config", "list"])
        assert result.exit_code == 0
        assert "llm" in result.output.lower()

    def test_config_set_get(self, temp_project: Path, monkeypatch):
        """Test config set and get."""
        monkeypatch.chdir(str(temp_project))
        runner.invoke(app, ["init", str(temp_project)])

        result = runner.invoke(
            app, ["config", "set", "llm.provider", "anthropic"]
        )
        assert result.exit_code == 0

        result = runner.invoke(app, ["config", "get", "llm.provider"])
        assert result.exit_code == 0
        assert "anthropic" in result.output

    def test_status_no_init(self, tmp_path: Path, monkeypatch):
        """Test status without init."""
        monkeypatch.chdir(str(tmp_path))
        result = runner.invoke(app, ["status"])
        assert "not initialized" in result.output.lower() or result.exit_code != 0

    def test_history_empty(self, temp_project: Path, monkeypatch):
        """Test history with no errors."""
        monkeypatch.chdir(str(temp_project))
        runner.invoke(app, ["init", str(temp_project)])
        result = runner.invoke(app, ["history"])
        assert result.exit_code == 0
