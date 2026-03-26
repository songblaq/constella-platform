#!/usr/bin/env python3
from __future__ import annotations

import argparse
import shutil
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
SEED_ROOT = REPO_ROOT / "bootstrap_seed"


def copy_tree(src: Path, dst: Path) -> None:
    dst.mkdir(parents=True, exist_ok=True)
    for child in src.iterdir():
        target = dst / child.name
        if child.is_dir():
            copy_tree(child, target)
        else:
            shutil.copy2(child, target)


def bootstrap(home: Path, overwrite: bool) -> list[str]:
    home = home.expanduser()
    written: list[str] = []
    for directory in [
        "atlas",
        "registry",
        "runtime",
        "knowledge",
        "collab",
        "logs",
        "backups",
        "manifests",
        "profiles",
        "tmp",
        "bin",
    ]:
        (home / directory).mkdir(parents=True, exist_ok=True)

    for relative in [
        Path("bin"),
        Path("profiles"),
        Path("manifests"),
        Path("backups"),
    ]:
        src = SEED_ROOT / relative
        dst = home / relative
        for child in src.rglob("*"):
            if child.is_dir():
                continue
            target = dst / child.relative_to(src)
            target.parent.mkdir(parents=True, exist_ok=True)
            if target.exists() and not overwrite:
                continue
            shutil.copy2(child, target)
            written.append(str(target))

    cli_path = home / "bin" / "constella"
    cli_path.chmod(0o755)
    return written


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="bootstrap_constellar")
    parser.add_argument("--home", default=str(Path.home() / ".constellar"))
    parser.add_argument("--overwrite", action="store_true")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    home = Path(args.home)
    written = bootstrap(home, overwrite=args.overwrite)
    print(f"constellar home ready: {home}")
    print(f"seed files written: {len(written)}")
    print(f"next: {home / 'bin' / 'constella'} verify bootstrap --profile dev")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
