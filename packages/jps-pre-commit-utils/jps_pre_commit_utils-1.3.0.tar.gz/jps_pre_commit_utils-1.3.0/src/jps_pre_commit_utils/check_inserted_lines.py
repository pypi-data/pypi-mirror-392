"""Entry point for the jps-pre-commit-utils pre-commit hook.

This wrapper delegates to the main CLI entry point so the utility can be
executed both as a module:

    python -m jps_pre_commit_utils.check_inserted_lines

and directly from its file path:

    python src/jps_pre_commit_utils/check_inserted_lines.py
"""

from __future__ import annotations

# Support running either as part of an installed package or as a standalone file.
try:
    from .cli import main as cli_main
except ImportError:  # pragma: no cover
    from jps_pre_commit_utils.cli import main as cli_main


def main() -> int:
    """Invoke the CLI entry point and return its exit code.

    Returns:
        int: Exit code from the CLI main function.
    """
    return cli_main()


if __name__ == "__main__":
    raise SystemExit(main())
