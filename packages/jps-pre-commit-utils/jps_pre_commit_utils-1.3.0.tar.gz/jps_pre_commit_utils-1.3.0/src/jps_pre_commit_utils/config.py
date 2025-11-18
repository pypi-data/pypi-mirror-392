"""Config loading and defaults for the pre-commit checks."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, Mapping, MutableMapping

import yaml

# Defaults keep your existing expectations and tests green.
_DEFAULTS: Dict[str, Any] = {
    "paths": ["/mnt/pure3", "/Users", r"C:\\Users"],
    "ignore_patterns": ["/mnt/pure3/bioinfo/shared/"],
    "extra_regexes": [r"jira/[A-Z]+-[0-9]+"],
    "patterns": {
        "python": [
            r"sys\.exit",
            r"logger\.debug",
            r"logging\.debug",
            r"\bprint\(",
            r"\btest\b",
            r"TODO",
        ],
        "perl": [
            r"use\s+Data::Dumper",
            r"warn\s+",
            r"print\s+",
            r"\btest\b",
            r"TODO",
        ],
        "yaml": [
            r"\btest\b",
            r"TODO",
        ],
    },
}


def _read_yaml(path: Path) -> Dict[str, Any]:
    """Read a YAML file returning a dict; empty dict if not found/invalid.

    Args:
        path: File path.

    Returns:
        Dict[str, Any]: Parsed YAML or {} on error.
    """
    try:
        if not path.exists():
            return {}
        return yaml.safe_load(path.read_text()) or {}
    except Exception:
        # Invalid YAML or IO errors are handled as empty.
        return {}


def _merge(base: MutableMapping[str, Any], override: Mapping[str, Any]) -> MutableMapping[str, Any]:
    """Shallow merge override keys into base.

    Args:
        base: Dict to update.
        override: New values.

    Returns:
        MutableMapping[str, Any]: Updated base (also returned for convenience).
    """
    for k, v in override.items():
        base[k] = v
    return base


def load_config() -> Dict[str, Any]:
    """Load config respecting precedence: local > home > defaults.

    Local file:
      ./.my-pre-commit-checks.yaml

    Home file:
      ~/.config/my-pre-commit-checks.yaml

    Keys:
      - paths: List[str]
      - ignore_patterns: List[str]
      - extra_regexes: List[str]
      - patterns: Dict[str, List[str]]

    Returns:
        Dict[str, Any]: Fully merged configuration.
    """
    cfg: Dict[str, Any] = dict(_DEFAULTS)

    # 1) Home
    home_file = Path.home() / ".config" / "my-pre-commit-checks.yaml"
    home_cfg = _read_yaml(home_file)
    if home_cfg:
        _merge(cfg, home_cfg)

    # 2) Local
    local_file = Path.cwd() / ".my-pre-commit-checks.yaml"
    local_cfg = _read_yaml(local_file)
    if local_cfg:
        _merge(cfg, local_cfg)

    # Type guards (best effort; keep it permissive for user files).
    cfg.setdefault("paths", _DEFAULTS["paths"])
    if not isinstance(cfg["paths"], list):
        cfg["paths"] = list(_DEFAULTS["paths"])

    cfg.setdefault("ignore_patterns", _DEFAULTS["ignore_patterns"])
    if not isinstance(cfg["ignore_patterns"], list):
        cfg["ignore_patterns"] = list(_DEFAULTS["ignore_patterns"])

    cfg.setdefault("extra_regexes", _DEFAULTS["extra_regexes"])
    if not isinstance(cfg["extra_regexes"], list):
        cfg["extra_regexes"] = list(_DEFAULTS["extra_regexes"])

    cfg.setdefault("patterns", _DEFAULTS["patterns"])
    pats = cfg["patterns"]
    if not isinstance(pats, dict):
        cfg["patterns"] = dict(_DEFAULTS["patterns"])

    return cfg
