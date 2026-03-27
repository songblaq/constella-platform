import subprocess
import sys
from pathlib import Path


REPO_ROOT = Path("/Users/lucablaq/_/projects/constella-platform")
SCRIPT = REPO_ROOT / "scripts" / "check_github_workflow_scope.py"


def test_workflow_scope_check_reports_missing_scope(tmp_path):
    sample = tmp_path / "gh-auth-status.txt"
    sample.write_text(
        "\n".join(
            [
                "github.com",
                "  ✓ Logged in to github.com account songblaq (keyring)",
                "  - Active account: true",
                "  - Git operations protocol: https",
                "  - Token scopes: 'gist', 'read:org', 'repo'",
            ]
        )
        + "\n",
        encoding="utf-8",
    )

    result = subprocess.run(
        [sys.executable, str(SCRIPT), "--input-file", str(sample)],
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 1
    assert "missing" in result.stdout.lower()
    assert "workflow" in result.stdout.lower()


def test_workflow_scope_check_reports_present_scope(tmp_path):
    sample = tmp_path / "gh-auth-status.txt"
    sample.write_text(
        "\n".join(
            [
                "github.com",
                "  ✓ Logged in to github.com account songblaq (keyring)",
                "  - Active account: true",
                "  - Git operations protocol: https",
                "  - Token scopes: 'gist', 'read:org', 'repo', 'workflow'",
            ]
        )
        + "\n",
        encoding="utf-8",
    )

    result = subprocess.run(
        [sys.executable, str(SCRIPT), "--input-file", str(sample)],
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0
    assert "present" in result.stdout.lower()
    assert "workflow" in result.stdout.lower()
