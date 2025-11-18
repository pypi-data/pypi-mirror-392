# tests/test_cli.py
from jps_pre_commit_utils import cli


def test_cli_main_invokes_all_components(monkeypatch: object):
    """Ensure main() ties together the expected workflow.

    Args:
        monkeypatch: pytest monkeypatch fixture.
    """

    called = {}

    monkeypatch.setattr(cli, "get_staged_diff", lambda: "diff content")
    monkeypatch.setattr(cli, "load_config", lambda: {"patterns": {"python": ["TODO"]}})
    monkeypatch.setattr(
        cli, "scan_diff", lambda diff, cfg: [{"pattern": "TODO", "line": "TODO: fix"}]
    )
    monkeypatch.setattr(
        cli, "print_report", lambda findings: called.setdefault("printed", findings)
    )

    result = cli.main()
    assert result == 1  # non-zero exit since findings exist
    assert "printed" in called


def test_cli_main_returns_zero_when_no_findings(monkeypatch: object):
    """Ensure it returns 0 when scan_diff reports no findings.

    Args:
        monkeypatch: pytest monkeypatch fixture.
    """

    monkeypatch.setattr(cli, "get_staged_diff", lambda: "")
    monkeypatch.setattr(cli, "load_config", lambda: {"patterns": {}})
    monkeypatch.setattr(cli, "scan_diff", lambda diff, cfg: [])
    monkeypatch.setattr(cli, "print_report", lambda findings: None)

    result = cli.main()
    assert result == 0
