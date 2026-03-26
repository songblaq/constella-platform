from __future__ import annotations

import json
import os
import re
import subprocess
from copy import deepcopy
from pathlib import Path
from typing import Any, Sequence


def orbit_home() -> Path:
    override = os.environ.get("CONSTELLA_ARIA_HOME")
    if override:
        return Path(override).expanduser() / "orbit"
    return Path.home() / ".aria" / "orbit"


DEFAULT_ORBIT_HOME = orbit_home()
DEFAULT_STATUS_COMMAND = (
    "python3",
    str(DEFAULT_ORBIT_HOME / "orbit-status.py"),
    "--json",
    "--top",
    "5",
)
DEFAULT_STATUS_JSON = DEFAULT_ORBIT_HOME / "orbit-status.json"
DEFAULT_SYNC_LOG = DEFAULT_ORBIT_HOME / "log" / "orbit-hive-sync.stdout.log"

_SYNC_START = "[orbit-hive-sync] 동기화 시작"
_SYNC_DONE = "[orbit-hive-sync] 동기화 완료"
_AH_NEW = re.compile(r"AH → ORBIT 신규 등록:\s*(?P<count>\d+)\s*tasks")
_AH_CACHE = re.compile(r"AH → ORBIT:\s*(?P<count>\d+)\s*tasks 상태 캐싱")
_COLLAB_RUNS = re.compile(r"ORBIT → Collab:\s*(?P<count>\d+)\s*runs 기록")


class OrbitReadError(RuntimeError):
    """Raised when the read-only ORBIT snapshot cannot be loaded."""


class OrbitMutationError(RuntimeError):
    """Raised when an ORBIT schedule/task mutation cannot be planned or applied."""


def _load_json_text(raw: str) -> dict:
    payload = json.loads(raw)
    if not isinstance(payload, dict):
        raise OrbitReadError("ORBIT status payload must be a JSON object")
    return payload


def _load_json_file(path: Path) -> dict:
    return _load_json_text(path.read_text(encoding="utf-8"))


def _load_json_document(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    raw = path.read_text(encoding="utf-8")
    if not raw.strip():
        return {}
    payload = json.loads(raw)
    if not isinstance(payload, dict):
        raise OrbitMutationError("ORBIT mutation targets must be JSON objects")
    return payload


def _write_json_document(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _json_document_text(payload: dict[str, Any]) -> str:
    return json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n"


def _merge_json_documents(current: Any, updates: Any) -> Any:
    if isinstance(current, dict) and isinstance(updates, dict):
        merged = dict(current)
        for key, value in updates.items():
            if key in current and isinstance(current[key], dict) and isinstance(value, dict):
                merged[key] = _merge_json_documents(current[key], value)
            else:
                merged[key] = deepcopy(value)
        return merged
    return deepcopy(updates)


def _diff_json_documents(current: Any, updated: Any, prefix: str = "") -> list[dict[str, Any]]:
    if isinstance(current, dict) and isinstance(updated, dict):
        changes: list[dict[str, Any]] = []
        for key in sorted(set(current) | set(updated)):
            path = f"{prefix}.{key}" if prefix else key
            if key not in current:
                changes.append({"path": path, "before": None, "after": deepcopy(updated[key])})
                continue
            if key not in updated:
                changes.append({"path": path, "before": deepcopy(current[key]), "after": None})
                continue
            changes.extend(_diff_json_documents(current[key], updated[key], path))
        return changes

    if current != updated:
        return [{"path": prefix or "", "before": deepcopy(current), "after": deepcopy(updated)}]
    return []


def _build_rollback_plan(kind: str, path: Path, before: dict[str, Any]) -> dict[str, Any]:
    return {
        "available": True,
        "mode": "restore",
        "path": str(path),
        "summary": f"Restore the prior ORBIT {kind} snapshot",
        "writes": [
            {
                "path": str(path),
                "kind": "json",
                "content": _json_document_text(before),
            }
        ],
    }


def _mutation_summary(kind: str, execute: bool, change_count: int) -> str:
    phase = "Applied" if execute else "Dry-run"
    noun = "change" if change_count == 1 else "changes"
    return f"{phase} ORBIT {kind} mutation with {change_count} {noun}"


def _plan_json_mutation(kind: str, target_path: Path | str, updates: dict[str, Any], *, execute: bool = False) -> dict:
    path = Path(target_path)
    if not isinstance(updates, dict):
        raise OrbitMutationError("ORBIT mutations must be expressed as a JSON object")

    before = _load_json_document(path)
    after = _merge_json_documents(before, updates)
    changes = _diff_json_documents(before, after)
    mode = "applied" if execute else "preview"
    surface = f"orbit.{kind}"
    writes = [
        {
            "path": str(path),
            "kind": "json",
            "content": _json_document_text(after),
        }
    ]

    if execute:
        _write_json_document(path, after)

    return {
        "kind": kind,
        "surface": surface,
        "preview": not execute,
        "dry_run": not execute,
        "mode": mode,
        "path": str(path),
        "before": before,
        "after": after,
        "changes": changes,
        "summary": _mutation_summary(kind, execute, len(changes)),
        "writes": writes,
        "rollback": _build_rollback_plan(kind, path, before),
    }


def preview_schedule_mutation(schedule_path: Path | str, updates: dict[str, Any]) -> dict:
    """Preview a schedule mutation without writing to disk."""

    return _plan_json_mutation("schedule", schedule_path, updates, execute=False)


def apply_schedule_mutation(
    schedule_path: Path | str,
    updates: dict[str, Any],
    *,
    execute: bool = False,
) -> dict:
    """Plan or apply a schedule mutation, defaulting to preview-only behavior."""

    return _plan_json_mutation("schedule", schedule_path, updates, execute=execute)


def preview_task_mutation(task_path: Path | str, updates: dict[str, Any]) -> dict:
    """Preview a task mutation without writing to disk."""

    return _plan_json_mutation("task", task_path, updates, execute=False)


def apply_task_mutation(
    task_path: Path | str,
    updates: dict[str, Any],
    *,
    execute: bool = False,
) -> dict:
    """Plan or apply a task mutation, defaulting to preview-only behavior."""

    return _plan_json_mutation("task", task_path, updates, execute=execute)


def _status_from_command(command: Sequence[str], timeout: int) -> dict:
    completed = subprocess.run(
        list(command),
        capture_output=True,
        text=True,
        check=True,
        timeout=timeout,
    )
    if not completed.stdout.strip():
        raise OrbitReadError("ORBIT status command returned empty output")
    status = _load_json_text(completed.stdout)
    status["source"] = "command"
    status["command"] = list(command)
    return status


def read_status(
    *,
    status_command: Sequence[str] | None = None,
    status_json_path: str | Path | None = None,
    timeout: int = 30,
) -> dict:
    """Read the latest ORBIT status snapshot without mutating shared state."""

    default_home = orbit_home()
    command = tuple(status_command or ("python3", str(default_home / "orbit-status.py"), "--json", "--top", "5"))
    json_path = Path(status_json_path) if status_json_path else default_home / "orbit-status.json"

    try:
        return _status_from_command(command, timeout)
    except (
        FileNotFoundError,
        subprocess.CalledProcessError,
        subprocess.TimeoutExpired,
        OrbitReadError,
    ):
        if json_path.exists():
            status = _load_json_file(json_path)
            status["source"] = "file"
            status["path"] = str(json_path)
            return status
        raise OrbitReadError(
            "Unable to read ORBIT status from command output or fallback JSON file"
        )


def _latest_sync_block(text: str) -> str | None:
    start = text.rfind(_SYNC_START)
    if start == -1:
        return None
    return text[start:]


def read_sync_summary(*, sync_log_path: str | Path | None = None, text: str | None = None) -> dict:
    """Summarize the latest AgentHive ↔ ORBIT sync block."""

    if text is None:
        log_path = Path(sync_log_path) if sync_log_path else orbit_home() / "log" / "orbit-hive-sync.stdout.log"
        if not log_path.exists():
            return {
                "available": False,
                "source": "missing",
                "path": str(log_path),
                "summary": "no sync log found",
            }
        text = log_path.read_text(encoding="utf-8")
        source_path = str(log_path)
    else:
        source_path = str(sync_log_path) if sync_log_path else None

    block = _latest_sync_block(text)
    if block is None:
        return {
            "available": False,
            "source": "unparsed",
            "path": source_path,
            "summary": "no sync block found",
        }

    new_match = _AH_NEW.search(block)
    cache_match = _AH_CACHE.search(block)
    collab_match = _COLLAB_RUNS.search(block)

    new_count = int(new_match.group("count")) if new_match else None
    cached_count = int(cache_match.group("count")) if cache_match else None
    collab_runs = int(collab_match.group("count")) if collab_match else None
    completed = _SYNC_DONE in block

    lines = [line.strip() for line in block.splitlines() if line.strip()]
    summary_bits = []
    if cached_count is not None:
        summary_bits.append(f"AH→ORBIT cached={cached_count}")
    if new_count is not None:
        summary_bits.append(f"new={new_count}")
    if collab_runs is not None:
        summary_bits.append(f"ORBIT→Collab runs={collab_runs}")
    summary = ", ".join(summary_bits) if summary_bits else "unparsed sync block"

    return {
        "available": True,
        "source": "log",
        "path": source_path,
        "block": lines,
        "completed": completed,
        "new_registrations": new_count,
        "cached_task_count": cached_count,
        "collab_runs_recorded": collab_runs,
        "summary": summary,
    }


def read_snapshot(
    *,
    status_command: Sequence[str] | None = None,
    status_json_path: str | Path | None = None,
    sync_log_path: str | Path | None = None,
    timeout: int = 30,
) -> dict:
    """Return a combined status + sync snapshot for downstream consumers."""

    return {
        "status": read_status(
            status_command=status_command,
            status_json_path=status_json_path,
            timeout=timeout,
        ),
        "sync": read_sync_summary(sync_log_path=sync_log_path),
    }


__all__ = [
    "DEFAULT_ORBIT_HOME",
    "DEFAULT_STATUS_COMMAND",
    "DEFAULT_STATUS_JSON",
    "DEFAULT_SYNC_LOG",
    "OrbitMutationError",
    "OrbitReadError",
    "apply_schedule_mutation",
    "apply_task_mutation",
    "read_snapshot",
    "read_status",
    "read_sync_summary",
    "preview_schedule_mutation",
    "preview_task_mutation",
]
