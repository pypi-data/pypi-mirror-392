"""Regression test to ensure local config overrides home config."""

from pathlib import Path

import yaml

import jps_pre_commit_utils.config as config


def test_load_config_prefers_local_over_home(tmp_path: object, monkeypatch: object) -> None:
    """Verify that a local `.my-pre-commit-checks.yaml` takes precedence.

    The local config should override `~/.config/my-pre-commit-checks.yaml` if both exist.

    Args:
        tmp_path: pytest temporary directory fixture.
        monkeypatch: pytest monkeypatch fixture.
    """
    # Prepare fake home directory with config
    home_cfg = tmp_path / ".config" / "my-pre-commit-checks.yaml"
    home_cfg.parent.mkdir(parents=True)
    home_data = {"paths": ["/home-shared"], "patterns": {"perl": [r"bar"]}}
    home_cfg.write_text(yaml.safe_dump(home_data))

    # Prepare local config (should override)
    local_cfg = tmp_path / ".my-pre-commit-checks.yaml"
    local_data = {"paths": ["/local-data"], "patterns": {"python": [r"foo"]}}
    local_cfg.write_text(yaml.safe_dump(local_data))

    # Patch environment to use fake home and cwd
    monkeypatch.setattr(Path, "home", lambda: tmp_path)
    monkeypatch.chdir(tmp_path)

    # Execute
    result = config.load_config()

    # Local config should take priority
    assert result["paths"] == ["/local-data"]
    assert "python" in result["patterns"]
    assert "perl" not in result["patterns"]
    # The merged config should include both pattern groups
    assert set(result["patterns"].keys()) == {"python"}


def test_load_config_handles_invalid_home_yaml(tmp_path: object, monkeypatch: object) -> None:
    """Verify that invalid YAML in the home config does NOT crash.

    This verifies that the loader gracefully falls back to defaults.

    Args:
        tmp_path: pytest temporary directory fixture.
        monkeypatch: pytest monkeypatch fixture.
    """
    # Create malformed YAML in fake home config
    home_cfg = tmp_path / ".config" / "my-pre-commit-checks.yaml"
    home_cfg.parent.mkdir(parents=True)
    home_cfg.write_text("paths: [unclosed_list")  # malformed YAML

    # Patch environment to use fake home directory
    monkeypatch.setattr(Path, "home", lambda: tmp_path)
    monkeypatch.chdir(tmp_path)

    # Execute loader
    result = config.load_config()

    # Validate that defaults were returned (not an exception)
    assert "patterns" in result
    assert "paths" in result
    assert isinstance(result["patterns"], dict)
    assert isinstance(result["paths"], list)

    # Confirm it didn’t silently load invalid content
    assert "/mnt/pure3" in result["paths"]
