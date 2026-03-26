from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def constellar_home() -> Path:
    override = os.environ.get("CONSTELLAR_HOME")
    if override:
        return Path(override).expanduser()
    return Path.home() / ".constellar"


def ensure_dirs() -> None:
    for name in ["history", "reviews", "audit", "capabilities"]:
        (constellar_home() / name).mkdir(parents=True, exist_ok=True)


def _append_jsonl(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(payload, ensure_ascii=False) + "\n")


def _read_jsonl(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    with path.open("r", encoding="utf-8") as handle:
        return [json.loads(line) for line in handle if line.strip()]


def timestamp() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def append_plan(payload: dict[str, Any]) -> None:
    _append_jsonl(constellar_home() / "history" / "plans.jsonl", payload)


def list_plans() -> list[dict[str, Any]]:
    return _read_jsonl(constellar_home() / "history" / "plans.jsonl")


def append_lesson(payload: dict[str, Any]) -> None:
    _append_jsonl(constellar_home() / "history" / "lessons.jsonl", payload)


def list_lessons() -> list[dict[str, Any]]:
    return _read_jsonl(constellar_home() / "history" / "lessons.jsonl")


def append_finding(payload: dict[str, Any]) -> None:
    _append_jsonl(constellar_home() / "reviews" / "findings.jsonl", payload)


def list_findings() -> list[dict[str, Any]]:
    return _read_jsonl(constellar_home() / "reviews" / "findings.jsonl")


def append_decision(payload: dict[str, Any]) -> None:
    _append_jsonl(constellar_home() / "history" / "decisions.jsonl", payload)


def list_decisions() -> list[dict[str, Any]]:
    return _read_jsonl(constellar_home() / "history" / "decisions.jsonl")


def append_audit(payload: dict[str, Any]) -> None:
    _append_jsonl(constellar_home() / "audit" / "capability-events.jsonl", payload)


def list_audit() -> list[dict[str, Any]]:
    return _read_jsonl(constellar_home() / "audit" / "capability-events.jsonl")
