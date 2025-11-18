"""Reporting utilities (Rich with plain-text fallback)."""

from __future__ import annotations

from typing import Iterable, Mapping

try:
    from rich.console import Console
except Exception:  # pragma: no cover
    Console = None


def _console_print(msg: str) -> None:
    """Print using Rich if available; otherwise plain print.

    Args:
        msg: Message string, may include Rich markup.
    """
    if Console is not None:
        Console().print(msg)
    else:
        # Strip simple [color] tags for a plain fallback.
        txt = msg.replace("[bold cyan]", "").replace("[/bold cyan]", "")
        txt = txt.replace("[green]", "").replace("[/green]", "")
        txt = txt.replace("[yellow]", "").replace("[/yellow]", "")
        txt = txt.replace("[red]", "").replace("[/red]", "")
        print(txt)


def print_report(findings: Iterable[Mapping[str, str]]) -> None:
    """Pretty-print the findings with a header and summary.

    Args:
        findings: Iterable of result dicts with at least:
            - 'pattern' (str)
            - 'line' (str)
            - optional: 'group' (str)
    """
    items = list(findings)

    _console_print("\n[bold cyan]🔍 Pre-commit inserted-line scan results[/bold cyan]")

    if not items:
        _console_print("[green]✅ No issues detected.[/green]")
        return

    for f in items:
        pat = f.get("pattern", "?")
        line = f.get("line", "")
        group = f.get("group", "")
        if group:
            _console_print(
                "[yellow]Added line contains pattern:[/yellow] "
                f"'{pat}' (group: {group}) → {line}"
            )
        else:
            _console_print("[yellow]Added line contains pattern:[/yellow] " f"'{pat}' → {line}")

    _console_print(f"\n[red]⚠️ Total findings: {len(items)}[/red]")
