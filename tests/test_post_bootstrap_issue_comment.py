import subprocess
import sys
from pathlib import Path


REPO_ROOT = Path("/Users/lucablaq/_/projects/constella-platform")
SCRIPT = REPO_ROOT / "scripts" / "post_bootstrap_issue_comment.py"


def test_post_bootstrap_issue_comment_dry_run(tmp_path):
    comment = tmp_path / "last-bootstrap-issue-comment.md"
    comment.write_text(
        "## Bootstrap Verification Result\n\n- machine: `TestMachine`\n",
        encoding="utf-8",
    )

    result = subprocess.run(
        [
            sys.executable,
            str(SCRIPT),
            "--repo",
            "songblaq/constella-platform",
            "--issue",
            "1",
            "--comment-file",
            str(comment),
            "--dry-run",
        ],
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0, result.stderr
    assert "songblaq/constella-platform#1" in result.stdout
    assert "## Bootstrap Verification Result" in result.stdout
