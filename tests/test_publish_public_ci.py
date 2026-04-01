import subprocess
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT = REPO_ROOT / "scripts" / "publish_public_ci.py"


def test_publish_public_ci_dry_run_reports_missing_scope(tmp_path):
    auth = tmp_path / "gh-auth-status.txt"
    auth.write_text(
        "\n".join(
            [
                "github.com",
                "  - Token scopes: 'gist', 'read:org', 'repo'",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    commits = tmp_path / "pending-commits.txt"
    commits.write_text("a692f68 ci: add public baseline workflow\n", encoding="utf-8")

    result = subprocess.run(
        [
            sys.executable,
            str(SCRIPT),
            "--repo-path",
            str(REPO_ROOT),
            "--auth-input-file",
            str(auth),
            "--commits-input-file",
            str(commits),
            "--dry-run",
        ],
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 1
    assert "workflow scope missing" in result.stdout.lower()
    assert "a692f68" in result.stdout


def test_publish_public_ci_dry_run_reports_ready_when_scope_present(tmp_path):
    auth = tmp_path / "gh-auth-status.txt"
    auth.write_text(
        "\n".join(
            [
                "github.com",
                "  - Token scopes: 'gist', 'read:org', 'repo', 'workflow'",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    commits = tmp_path / "pending-commits.txt"
    commits.write_text("a692f68 ci: add public baseline workflow\n", encoding="utf-8")

    result = subprocess.run(
        [
            sys.executable,
            str(SCRIPT),
            "--repo-path",
            str(REPO_ROOT),
            "--auth-input-file",
            str(auth),
            "--commits-input-file",
            str(commits),
            "--dry-run",
        ],
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0
    assert "ready to push" in result.stdout.lower()
    assert "a692f68" in result.stdout
