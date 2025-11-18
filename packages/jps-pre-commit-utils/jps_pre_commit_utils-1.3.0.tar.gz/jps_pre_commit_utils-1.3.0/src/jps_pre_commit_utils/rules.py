"""Compile user-configured patterns into regex objects."""

from __future__ import annotations

import re
from typing import Dict, List


def _as_list(value: object) -> List[str]:
    """Normalize a string or list-of-strings to a list of strings.

    Args:
        value: Input value of various possible types.

    Returns:
        List[str]: Normalized list of strings.
    """
    if value is None:
        return []
    if isinstance(value, str):
        return [value]
    if isinstance(value, (list, tuple)):
        return [str(v) for v in value]
    return []


def compile_patterns(pattern_cfg: object) -> Dict[str, List[re.Pattern]]:
    """Compile configured patterns.

    Args:
        pattern_cfg: Expected `Dict[str, Iterable[str]]`, but tolerant.

    Returns:
        Dict[str, List[re.Pattern]]: Group -> compiled regex list.
    """
    if not isinstance(pattern_cfg, dict):
        return {}

    compiled: Dict[str, List[re.Pattern]] = {}

    for group, raw in pattern_cfg.items():
        patterns = _as_list(raw)
        if not patterns:
            continue
        try:
            compiled[group] = [re.compile(p) for p in patterns]
        except re.error:
            # If a pattern fails to compile, skip that group entirely.
            continue

    return compiled
