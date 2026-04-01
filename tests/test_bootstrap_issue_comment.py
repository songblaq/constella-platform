import subprocess
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT = REPO_ROOT / "scripts" / "render_bootstrap_issue_comment.py"


def test_render_bootstrap_issue_comment(tmp_path):
    verification = tmp_path / "last-bootstrap-verification.json"
    verification.write_text(
        """{
  "mode": "bootstrap-verification",
  "profile": "dev",
  "machine": {
    "hostname": "TestMachine",
    "platform": "darwin",
    "python": "3.14.3",
    "constellar_home": "/tmp/.constellar"
  },
  "required_repos": ["agent-hive", "aria", "openclaw"],
  "required_artifacts": ["~/.constellar/manifests/install-bundle.json"],
  "runtime_family": ["openclaw", "codex"],
  "checks": [
    {"id": "layout", "label": "constellar layout exists"}
  ],
  "next_action": "Attach the generated JSON/Markdown artifacts to GitHub issue #1."
}
""",
        encoding="utf-8",
    )

    output_path = tmp_path / "issue-comment.md"
    result = subprocess.run(
        [
            sys.executable,
            str(SCRIPT),
            "--verification-json",
            str(verification),
            "--output",
            str(output_path),
        ],
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0, result.stderr
    assert "## Bootstrap Verification Result" in result.stdout
    assert "- machine: `TestMachine`" in result.stdout
    assert "- install mode: `dev`" in result.stdout
    assert "- `agent-hive`" in result.stdout
    assert "- `openclaw`" in result.stdout
    assert output_path.exists()
    assert "## Bootstrap Verification Result" in output_path.read_text(encoding="utf-8")
