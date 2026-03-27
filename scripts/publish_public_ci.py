#!/usr/bin/env python3
from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path


def read_text(path: str | None) -> str:
    if not path:
        return ""
    return Path(path).read_text(encoding="utf-8")


def pending_commits(repo_path: Path, input_file: str | None) -> str:
    if input_file:
        return read_text(input_file)
    result = subprocess.run(
        ["git", "-C", str(repo_path), "log", "--oneline", "origin/main..main"],
        check=False,
        capture_output=True,
        text=True,
    )
    return result.stdout


def workflow_scope_present(text: str) -> bool:
    return "workflow" in text


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="publish_public_ci")
    parser.add_argument("--repo-path", required=True)
    parser.add_argument("--auth-input-file")
    parser.add_argument("--commits-input-file")
    parser.add_argument("--dry-run", action="store_true")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    repo_path = Path(args.repo_path)
    auth_text = read_text(args.auth_input_file)
    commits = pending_commits(repo_path, args.commits_input_file).strip()

    if not workflow_scope_present(auth_text):
        print("workflow scope missing")
        if commits:
            print(commits)
        return 1

    if args.dry_run:
        print("ready to push")
        if commits:
            print(commits)
        return 0

    result = subprocess.run(
        ["git", "-C", str(repo_path), "push", "origin", "main"],
        check=False,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        sys.stderr.write(result.stderr)
        return result.returncode
    print(result.stdout, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
