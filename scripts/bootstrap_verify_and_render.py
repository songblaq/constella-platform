#!/usr/bin/env python3
from __future__ import annotations

import argparse
import os
import subprocess
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]


def run(cmd: list[str], env: dict[str, str] | None = None) -> subprocess.CompletedProcess[str]:
    return subprocess.run(cmd, check=False, capture_output=True, text=True, env=env)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="bootstrap_verify_and_render")
    parser.add_argument("--home", default=str(Path.home() / ".constellar"))
    parser.add_argument("--profile", default="dev", choices=["bootstrap", "dev", "runtime-only", "ops"])
    return parser


def main() -> int:
    args = build_parser().parse_args()
    home = Path(args.home).expanduser()

    seed = run([sys.executable, str(REPO_ROOT / "scripts" / "bootstrap_constellar.py"), "--home", str(home)])
    if seed.returncode != 0:
        sys.stderr.write(seed.stderr)
        return seed.returncode

    env = {**os.environ, "CONSTELLAR_HOME": str(home)}
    verify = run(
        [
            sys.executable,
            str(home / "bin" / "constella"),
            "verify",
            "bootstrap",
            "--profile",
            args.profile,
        ],
        env=env,
    )
    if verify.returncode != 0:
        sys.stderr.write(verify.stderr)
        return verify.returncode

    render = run(
        [
            sys.executable,
            str(REPO_ROOT / "scripts" / "render_bootstrap_issue_comment.py"),
            "--verification-json",
            str(home / "manifests" / "last-bootstrap-verification.json"),
        ]
    )
    if render.returncode != 0:
        sys.stderr.write(render.stderr)
        return render.returncode

    sys.stdout.write(render.stdout)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
