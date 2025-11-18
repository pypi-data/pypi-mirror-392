"""Command-line orchestration for inserted-line checks."""

from __future__ import annotations

from typing import List

from .config import load_config
from .git_diff import get_staged_diff
from .report import print_report
from .scanner import scan_diff


def main() -> int:
    """Run the end-to-end scan for staged inserted lines.

    Workflow:
      1) Load configuration (local > home > defaults).
      2) Collect staged diff (unified=0).
      3) Extract added lines and scan them.
      4) Print a report; return 1 if findings were detected.

    Returns:
        int: 0 if no findings, 1 if findings were detected.
    """
    cfg = load_config()

    raw_diff = get_staged_diff()
    added_lines = _extract_added_lines(raw_diff)

    findings = scan_diff(added_lines, cfg)
    print_report(findings)

    return 1 if findings else 0


def _extract_added_lines(diff_text: str) -> List[str]:
    """Parse added lines from a unified diff string.

    Only lines beginning with '+' (and not '+++') are considered.

    Args:
        diff_text: Output of `git diff --cached --unified=0`.

    Returns:
        List[str]: Added lines without the leading '+'.
    """
    added: List[str] = []
    for line in diff_text.splitlines():
        if not line.startswith("+"):
            continue
        # ignore diff metadata lines like '+++ b/file.py'
        if line.startswith("+++"):
            continue
        added.append(line[1:])
    return added
