# tests/test_scanner.py
import re

from jps_pre_commit_utils import scanner


def test_scan_diff_detects_patterns(monkeypatch: object) -> None:
    """Ensure scan_diff flags lines containing forbidden patterns.

    Args:
        monkeypatch: pytest monkeypatch fixture.
    """
    # Mock compile_patterns to return regex objects
    monkeypatch.setattr(
        "jps_pre_commit_utils.scanner.compile_patterns",
        lambda cfg: {
            "python": [re.compile(r"TODO"), re.compile(r"print")],
        },
    )

    added_lines = [
        "print('debug')",  # should match
        "def func(): pass",  # should NOT match
        "# TODO: implement later",  # should match
    ]

    # Run scanner
    config = {"patterns": {"python": ["TODO", "print"]}}
    results = scanner.scan_diff(added_lines, config)

    assert isinstance(results, list)
    assert len(results) == 2, f"Expected 2 matches, got {len(results)}"
    assert any("print" in r["line"] for r in results)
    assert any("TODO" in r["line"] for r in results)


def test_scan_diff_no_matches(monkeypatch: object) -> None:
    """Ensure scan_diff returns an empty list when no matches found.

    Args:
        monkeypatch: pytest monkeypatch fixture.
    """
    monkeypatch.setattr(
        "jps_pre_commit_utils.scanner.compile_patterns",
        lambda cfg: {"python": [re.compile(r"forbidden")]},
    )

    added_lines = ["safe_line", "another_safe_line"]
    config = {"patterns": {"python": ["forbidden"]}}
    results = scanner.scan_diff(added_lines, config)
    assert results == []


def test_scan_diff_handles_empty_input(monkeypatch: object) -> None:
    """Handles empty added lines gracefully.

    Args:
        monkeypatch: pytest monkeypatch fixture.
    """
    monkeypatch.setattr(
        "jps_pre_commit_utils.scanner.compile_patterns", lambda cfg: {"python": [re.compile(r".*")]}
    )
    config = {"patterns": {"python": [".*"]}}
    results = scanner.scan_diff([], config)
    assert results == []
