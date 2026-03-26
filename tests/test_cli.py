import json
import os
import subprocess
import sys


def run_cli(tmp_path, *args):
    env = os.environ.copy()
    env["CONSTELLAR_HOME"] = str(tmp_path / ".constellar")
    env["PYTHONPATH"] = "/Users/lucablaq/_/projects/constella-platform/src"
    return subprocess.run(
        [sys.executable, "-m", "constella_platform", *args],
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )


def test_cli_create_and_list_lesson(tmp_path):
    result = run_cli(
        tmp_path,
        "history",
        "lesson",
        "create",
        "--title",
        "missed repo ownership",
        "--why-failed",
        "plan was too abstract",
        "--what-was-missed",
        "exact project path",
        "--next-guardrail",
        "always define project home",
    )
    assert result.returncode == 0

    result = run_cli(tmp_path, "history", "lesson", "list")
    payload = json.loads(result.stdout)
    assert payload["data"][0]["title"] == "missed repo ownership"


def test_cli_aria_runtime_and_nyx_list(tmp_path):
    aria_home = tmp_path / ".aria"
    agents_dir = aria_home / "agents"
    agents_dir.mkdir(parents=True)
    (aria_home / "config.json").write_text(
        json.dumps(
            {
                "runtimes": {
                    "openclaw": {"enabled": True, "type": "gateway"},
                    "codex": {"enabled": True, "type": "cli"},
                }
            }
        ),
        encoding="utf-8",
    )
    for name in ["infra", "openclaw"]:
        agent_dir = agents_dir / name
        agent_dir.mkdir()
        (agent_dir / "config.json").write_text(json.dumps({"id": name}), encoding="utf-8")

    env = os.environ.copy()
    env["CONSTELLAR_HOME"] = str(tmp_path / ".constellar")
    env["CONSTELLA_ARIA_HOME"] = str(aria_home)
    env["PYTHONPATH"] = "/Users/lucablaq/_/projects/constella-platform/src"

    result = subprocess.run(
        [sys.executable, "-m", "constella_platform", "aria", "runtime", "list"],
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0
    runtimes = json.loads(result.stdout)
    assert runtimes["data"][0]["id"] == "codex"

    result = subprocess.run(
        [sys.executable, "-m", "constella_platform", "aria", "nyx", "list"],
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0
    nyx = json.loads(result.stdout)
    assert nyx["data"][0]["id"] == "infra"


def test_cli_aria_runtime_enablement_set(tmp_path):
    aria_home = tmp_path / ".aria"
    aria_home.mkdir(parents=True)
    (aria_home / "config.json").write_text(
        json.dumps(
            {
                "runtimes": {
                    "openclaw": {"enabled": True, "type": "gateway"},
                    "codex": {"enabled": True, "type": "cli"},
                }
            }
        ),
        encoding="utf-8",
    )

    env = os.environ.copy()
    env["CONSTELLAR_HOME"] = str(tmp_path / ".constellar")
    env["CONSTELLA_ARIA_HOME"] = str(aria_home)
    env["PYTHONPATH"] = "/Users/lucablaq/_/projects/constella-platform/src"

    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "constella_platform",
            "aria",
            "runtime",
            "enablement",
            "set",
            "--runtime-id",
            "codex",
            "--enabled",
            "false",
        ],
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0
    payload = json.loads(result.stdout)
    assert payload["data"]["runtime_id"] == "codex"
    assert payload["data"]["after"]["runtimes"]["codex"]["enabled"] is False
