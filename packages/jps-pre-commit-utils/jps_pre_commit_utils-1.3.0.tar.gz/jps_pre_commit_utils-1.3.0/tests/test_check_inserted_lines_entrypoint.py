# tests/test_check_inserted_lines_entrypoint.py
import subprocess
import sys
from pathlib import Path


def test_entrypoint_invokes_cli(monkeypatch: object, tmp_path: object) -> None:
    """Run the module as a subprocess to ensure imports resolve correctly.

    Args:
        monkeypatch: pytest monkeypatch fixture.
        tmp_path: pytest temporary directory fixture.
    """
    script_path = Path("src/jps_pre_commit_utils/check_inserted_lines.py")
    assert script_path.exists()

    # Mock out subprocess.run for git diff calls inside the subprocess
    result = subprocess.run(
        [sys.executable, "-m", "jps_pre_commit_utils.check_inserted_lines"],
        capture_output=True,
        text=True,
    )

    # Should exit cleanly — even if no staged diff is found
    assert result.returncode in (0, 1)
    assert "Traceback" not in result.stderr
