"""Unit tests for jps_pre_commit_utils.rules."""

import re

from jps_pre_commit_utils.rules import compile_patterns


def test_compile_patterns_returns_regex_objects():
    """Should compile each pattern into a regex object."""
    cfg = {"python": [r"sys\.exit", r"TODO"], "perl": [r"die"]}
    result = compile_patterns(cfg)
    assert isinstance(result, dict)
    assert isinstance(result["python"][0], re.Pattern)
    assert result["python"][0].pattern == r"sys\.exit"


def test_compile_patterns_empty_input():
    """Should handle empty config gracefully."""
    result = compile_patterns({})
    assert result == {}
