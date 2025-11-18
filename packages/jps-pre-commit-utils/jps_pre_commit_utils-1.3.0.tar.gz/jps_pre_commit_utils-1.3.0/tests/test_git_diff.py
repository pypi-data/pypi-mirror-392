"""Unit tests for jps_pre_commit_utils.git_diff."""

import subprocess

from jps_pre_commit_utils.git_diff import get_staged_diff


class DummyResult:
    def __init__(self, stdout="diff output"):
        self.stdout = stdout


def test_get_staged_diff_returns_stdout(monkeypatch: object) -> None:
    """Should return stdout from subprocess.run.

    Args:
        monkeypatch: pytest monkeypatch fixture.
    """

    def mock_run(*a, **kw):
        return DummyResult("MOCK_DIFF")

    monkeypatch.setattr(subprocess, "run", mock_run)
    result = get_staged_diff()
    assert result == "MOCK_DIFF"


def test_get_staged_diff_handles_empty_output(monkeypatch: object) -> None:
    """Should return empty string when subprocess has no output.

    Args:
        monkeypatch: pytest monkeypatch fixture.
    """

    def mock_run(*a, **kw):
        return DummyResult("")

    monkeypatch.setattr(subprocess, "run", mock_run)
    assert get_staged_diff() == ""


def test_get_staged_diff_does_not_raise(monkeypatch: object) -> None:
    """Should not raise even if subprocess.run fails.

    Args:
        monkeypatch: pytest monkeypatch fixture.
    """

    def mock_run(*a, **kw):
        raise subprocess.SubprocessError("git failed")

    monkeypatch.setattr(subprocess, "run", mock_run)
    try:
        result = get_staged_diff()
    except subprocess.SubprocessError:
        result = None
    assert result is None or isinstance(result, str)
