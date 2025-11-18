from __future__ import annotations

from pathlib import Path

import pytest

from fabric_deployment_tool import _git


def test_discover_artifacts(tmp_path: Path) -> None:
    (tmp_path / "proj").mkdir()
    files = ["a.yaml", "b.yml", "c.json", "notes.txt"]
    for name in files:
        target = tmp_path / "proj" / name
        target.write_text("{}", encoding="utf-8")
    artifacts = _git.discover_artifacts(tmp_path / "proj")
    assert artifacts == ["a.yaml", "b.yml", "c.json"]


def test_deploy_missing_root(tmp_path: Path) -> None:
    with pytest.raises(FileNotFoundError):
        _git.deploy(tmp_path / "missing")


def test_deploy_with_artifacts(tmp_path: Path) -> None:
    (tmp_path / "proj").mkdir()
    result = _git.deploy(tmp_path / "proj", artifacts=["abc.yaml"])
    assert result.deployed_items == ["abc.yaml"]
    assert "abc.yaml" in result.summary()
