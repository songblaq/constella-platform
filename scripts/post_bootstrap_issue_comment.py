#!/usr/bin/env python3
from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="post_bootstrap_issue_comment")
    parser.add_argument("--repo", required=True)
    parser.add_argument("--issue", required=True)
    parser.add_argument("--comment-file", required=True)
    parser.add_argument("--dry-run", action="store_true")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    comment_path = Path(args.comment_file)
    body = comment_path.read_text(encoding="utf-8")

    if args.dry_run:
        print(f"dry-run target: {args.repo}#{args.issue}")
        print(body, end="" if body.endswith("\n") else "\n")
        return 0

    result = subprocess.run(
        [
            "gh",
            "issue",
            "comment",
            args.issue,
            "-R",
            args.repo,
            "--body-file",
            str(comment_path),
        ],
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
