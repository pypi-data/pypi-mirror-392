"""Minimal wrapper around `git diff` for staged changes."""

from __future__ import annotations

import subprocess


def get_staged_diff() -> str:
    """Return the staged diff (unified=0) as a string.

    Returns:
        str: Raw unified diff text.
    """
    result = subprocess.run(
        ["git", "diff", "--cached", "--unified=0"],
        capture_output=True,
        text=True,
        check=False,
    )
    return result.stdout or ""
