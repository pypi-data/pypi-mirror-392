"""Core scanning logic for added lines against compiled patterns."""

from __future__ import annotations

from typing import Dict, Iterable, List, Mapping, Union

from .rules import compile_patterns

Added = Union[str, Iterable[str]]


def scan_diff(diff_text: Added, config: Mapping[str, object]) -> List[Dict[str, str]]:
    """Scan added lines and return list of findings.

    Accepts either a single string (with newlines) or an iterable of lines.

    Args:
        diff_text: Added lines to scan.
        config: Loaded configuration; reads the "patterns" key.

    Returns:
        List[Dict[str, str]]: Each finding has:
            - "pattern": matched pattern string
            - "line": offending line (raw)
            - "group": (optional) group name from pattern bundle
    """
    raw_patterns = config.get("patterns", {})
    compiled = compile_patterns(raw_patterns)

    # Normalize lines
    if isinstance(diff_text, str):
        lines = diff_text.splitlines()
    else:
        lines = list(diff_text)

    findings: List[Dict[str, str]] = []

    if not compiled or not lines:
        return findings

    for line in lines:
        for group, patterns in compiled.items():
            for pat in patterns:
                if pat.search(line):
                    findings.append({"pattern": pat.pattern, "line": line, "group": group})
    return findings
