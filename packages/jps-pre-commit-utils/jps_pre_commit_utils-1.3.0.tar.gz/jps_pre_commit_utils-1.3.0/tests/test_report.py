# tests/test_report.py
from jps_pre_commit_utils import report


def test_print_report_outputs_expected(capsys: object) -> None:
    """Ensure report correctly prints findings with Rich formatting.

    Args:
        capsys: pytest capture system fixture.
    """
    findings = [
        {"pattern": "TODO", "line": "Added TODO in code"},
        {"pattern": "print", "line": "print('debug')"},
    ]

    report.print_report(findings)
    captured = capsys.readouterr()

    assert "🔍 Pre-commit inserted-line scan results" in captured.out
    assert "⚠️ Total findings: 2" in captured.out


def test_print_report_no_issues(capsys: object) -> None:
    """Should print the success message when no issues are found.

    Args:
        capsys: pytest capture system fixture.
    """
    report.print_report([])
    captured = capsys.readouterr()
    assert "✅ No issues detected." in captured.out
