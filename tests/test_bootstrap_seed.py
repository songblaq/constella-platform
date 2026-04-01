import json
import os
import subprocess
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
BOOTSTRAP_SCRIPT = REPO_ROOT / "scripts" / "bootstrap_constellar.py"


def test_bootstrap_script_seeds_constellar_home(tmp_path):
    home = tmp_path / ".constellar"
    result = subprocess.run(
        [
            sys.executable,
            str(BOOTSTRAP_SCRIPT),
            "--home",
            str(home),
        ],
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0, result.stderr
    assert (home / "bin" / "constella").exists()
    assert (home / "profiles" / "dev.json").exists()
    assert (home / "manifests" / "install-bundle.json").exists()

    verify = subprocess.run(
        [
            sys.executable,
            str(home / "bin" / "constella"),
            "verify",
            "bootstrap",
            "--profile",
            "dev",
        ],
        check=False,
        capture_output=True,
        text=True,
        env={**os.environ, "CONSTELLAR_HOME": str(home)},
    )

    assert verify.returncode == 0, verify.stderr
    payload = json.loads((home / "manifests" / "last-bootstrap-verification.json").read_text(encoding="utf-8"))
    assert payload["profile"] == "dev"
    assert payload["runtime_family"]
