#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Lists all available CLI tools in the jps-pre-commit-utils package.

This script provides a unified help command for developers using pre-commit
utilities to scan staged changes and prevent anti-patterns from entering the repo.

Usage:
    jps-pre-commit-utils-help
"""

from __future__ import annotations

import textwrap

# ANSI color codes
GREEN = "\033[92m"
YELLOW = "\033[93m"
RESET = "\033[0m"


def main() -> None:
    """Display help for all entrypoint scripts in this package."""
    help_text = (
        textwrap.dedent(
            f"""
    jps-pre-commit-utils — Available Commands
    ====================================================

    {GREEN}jps-pre-commit-utils-checks{RESET}
        Scan staged Git changes (diffs) for anti-patterns:
        - Debug statements (pdb, ipdb, print, logger.debug)
        - Test code leakage (unittest.mock, pytest.skip)
        - Hardcoded paths (/tmp, /home/user, C:\\)
        - Secrets/tokens (high-entropy strings, common patterns)
        - Fully configurable via YAML

        Example:
            {YELLOW}jps-pre-commit-utils-checks --staged{RESET}
            {YELLOW}jps-pre-commit-utils-checks --config .pre-commit-checks.yaml{RESET}

    {GREEN}jps-pre-commit-utils-help{RESET}
        Displays this overview of all available commands.

    ----------------------------------------------------
    Tip: Run each command with '--help' to see detailed options and configuration.
    """
        ).strip()
        + "\n"
    )

    print(help_text)


if __name__ == "__main__":
    main()
