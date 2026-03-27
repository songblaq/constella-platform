#!/usr/bin/env python3
from __future__ import annotations

import argparse
import re
import subprocess
import sys
from pathlib import Path


def load_text(input_file: str | None) -> str:
    if input_file:
        return Path(input_file).read_text(encoding="utf-8")
    result = subprocess.run(["gh", "auth", "status"], check=False, capture_output=True, text=True)
    return (result.stdout or "") + (result.stderr or "")


def workflow_scope_present(text: str) -> bool:
    match = re.search(r"Token scopes:\s*(.+)", text)
    if not match:
        return False
    return "workflow" in match.group(1)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="check_github_workflow_scope")
    parser.add_argument("--input-file")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    text = load_text(args.input_file)
    if workflow_scope_present(text):
        print("workflow scope present")
        return 0
    print("workflow scope missing")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
