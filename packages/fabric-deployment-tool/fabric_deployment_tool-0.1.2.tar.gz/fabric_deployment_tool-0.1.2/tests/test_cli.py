from __future__ import annotations

from pathlib import Path

from typer.testing import CliRunner

from fabric_deployment_tool import _fab_cli


runner = CliRunner()


def test_cli_version() -> None:
    result = runner.invoke(_fab_cli.app, ["--version"])
    assert result.exit_code == 0
    assert result.stdout.strip()


def test_cli_run(tmp_path: Path) -> None:
    (tmp_path / "proj").mkdir()
    (tmp_path / "proj" / "artifact.yaml").write_text("{}", encoding="utf-8")
    result = runner.invoke(_fab_cli.app, ["run", str(tmp_path / "proj")])
    assert result.exit_code == 0
    assert "artifact.yaml" in result.stdout
