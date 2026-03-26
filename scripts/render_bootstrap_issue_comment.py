#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path


def load_payload(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def render_markdown(payload: dict) -> str:
    machine = payload.get("machine", {})
    profile = payload.get("profile", "unknown")
    required_repos = payload.get("required_repos", [])
    runtime_family = payload.get("runtime_family", [])
    checks = payload.get("checks", [])
    next_action = payload.get("next_action", "")

    lines = [
        "## Bootstrap Verification Result",
        "",
        f"- machine: `{machine.get('hostname', 'unknown')}`",
        f"- os: `{machine.get('platform', 'unknown')}`",
        f"- install mode: `{profile}`",
        f"- verification artifact: `{payload.get('mode', 'bootstrap-verification')}`",
        "",
        "### Required Repos",
    ]
    lines.extend([f"- `{item}`" for item in required_repos] or ["- none"])
    lines.extend(["", "### Runtime Family"])
    lines.extend([f"- `{item}`" for item in runtime_family] or ["- none"])
    lines.extend(["", "### Checks"])
    lines.extend([f"- `{item.get('id', 'check')}`: {item.get('label', '')}" for item in checks] or ["- none"])
    lines.extend(["", "### Next", f"- {next_action or 'Attach artifacts and report gaps.'}"])
    return "\n".join(lines) + "\n"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="render_bootstrap_issue_comment")
    parser.add_argument("--verification-json", required=True)
    return parser


def main() -> int:
    args = build_parser().parse_args()
    payload = load_payload(Path(args.verification_json))
    print(render_markdown(payload), end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
