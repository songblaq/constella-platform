import subprocess
import sys
from pathlib import Path


REPO_ROOT = Path("/Users/lucablaq/_/projects/constella-platform")
SCRIPT = REPO_ROOT / "scripts" / "bootstrap_verify_and_render.py"


def test_bootstrap_verify_and_render_helper(tmp_path):
    home = tmp_path / ".constellar"
    result = subprocess.run(
        [
            sys.executable,
            str(SCRIPT),
            "--home",
            str(home),
            "--profile",
            "dev",
        ],
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0, result.stderr
    assert "## Bootstrap Verification Result" in result.stdout
    assert (home / "manifests" / "last-bootstrap-verification.json").exists()
    assert (home / "manifests" / "last-bootstrap-verification.md").exists()
    assert (home / "manifests" / "last-bootstrap-issue-comment.md").exists()
