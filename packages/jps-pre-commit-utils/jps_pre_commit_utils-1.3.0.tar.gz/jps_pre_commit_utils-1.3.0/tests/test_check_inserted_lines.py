import subprocess
import sys
from pathlib import Path


def test_check_inserted_lines_runs(monkeypatch: object, tmp_path: object) -> None:
    """Smoke test to ensure the pre-commit utility executes without crashing.

    This test does NOT require a git repository — it simulates an empty diff.

    Args:
        monkeypatch: pytest monkeypatch fixture.
        tmp_path: pytest temporary directory fixture.
    """

    script_path = Path("src/jps_pre_commit_utils/check_inserted_lines.py")
    assert script_path.exists(), f"Missing script: {script_path}"

    original_run = subprocess.run

    # Mock only `git diff --cached`, not the outer script execution
    def mock_run(args, capture_output=True, text=True, check=False):
        if isinstance(args, list) and "git" in args and "diff" in args:

            class MockCompleted:
                stdout = ""  # simulate empty diff
                returncode = 0

            return MockCompleted()
        # fallback to real subprocess.run for the test's own script execution
        return original_run(args, capture_output=capture_output, text=text, check=check)

    monkeypatch.setattr(subprocess, "run", mock_run)

    result = subprocess.run([sys.executable, str(script_path)], capture_output=True, text=True)

    assert result.returncode == 0, f"Script exited with unexpected code {result.returncode}"
    assert (
        "✅" in result.stdout or "No issues detected" in result.stdout
    ), f"Unexpected output:\n{result.stdout}"
