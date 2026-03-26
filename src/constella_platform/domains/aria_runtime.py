from __future__ import annotations

import json
import os
from copy import deepcopy
from pathlib import Path
from typing import Any


def aria_home() -> Path:
    override = os.environ.get("CONSTELLA_ARIA_HOME")
    if override:
        return Path(override).expanduser()
    return Path.home() / ".aria"


def _load_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"expected JSON object at {path}")
    return payload


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(payload, indent=2, ensure_ascii=False, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def _merge_dicts(current: dict[str, Any], patch: dict[str, Any]) -> dict[str, Any]:
    merged = deepcopy(current)
    for key, value in patch.items():
        if isinstance(value, dict) and isinstance(merged.get(key), dict):
            merged[key] = _merge_dicts(merged[key], value)
        else:
            merged[key] = deepcopy(value)
    return merged


def _safe_relative_path(raw_path: str) -> Path:
    rel_path = Path(raw_path)
    if not raw_path or rel_path == Path(".") or rel_path.is_absolute() or ".." in rel_path.parts:
        raise ValueError(f"unsafe harness path: {raw_path}")
    return rel_path


def runtime_config_path() -> Path:
    return aria_home() / "config.json"


def agent_config_path(agent_id: str) -> Path:
    return aria_home() / "agents" / agent_id / "config.json"


def agent_harness_dir(agent_id: str) -> Path:
    return aria_home() / "agents" / agent_id / "harness"


def list_runtimes() -> list[dict]:
    payload = _load_json(runtime_config_path())
    runtimes = payload.get("runtimes", {})
    return [
        {
            "id": runtime_id,
            "enabled": bool(config.get("enabled", False)),
            "type": config.get("type", "unknown"),
        }
        for runtime_id, config in sorted(runtimes.items())
    ]


def list_nyx_agents() -> list[dict]:
    agents_dir = aria_home() / "agents"
    if not agents_dir.exists():
        return []
    agents = []
    for config_path in sorted(agents_dir.glob("*/config.json")):
        config = _load_json(config_path)
        agents.append(
            {
                "id": config.get("id", config_path.parent.name),
                "path": str(config_path.parent),
                "type": config.get("type", "unknown"),
                "has_harness": (config_path.parent / "harness").exists(),
            }
        )
    return agents


def preview_runtime_config_update(patch: dict[str, Any]) -> dict[str, Any]:
    current = _load_json(runtime_config_path())
    merged = _merge_dicts(current, patch)
    return {
        "surface": "aria.runtime.config",
        "path": str(runtime_config_path()),
        "before": current,
        "after": merged,
        "writes": [{"path": str(runtime_config_path()), "kind": "json"}],
    }


def preview_runtime_enablement_update(runtime_id: str, *, enabled: bool) -> dict[str, Any]:
    current = _load_json(runtime_config_path())
    runtimes = current.get("runtimes", {})
    if runtime_id not in runtimes:
        raise KeyError(f"unknown runtime: {runtime_id}")
    merged = _merge_dicts(current, {"runtimes": {runtime_id: {"enabled": enabled}}})
    return {
        "surface": "aria.runtime.enablement",
        "path": str(runtime_config_path()),
        "runtime_id": runtime_id,
        "enabled": enabled,
        "before": current,
        "after": merged,
        "writes": [{"path": str(runtime_config_path()), "kind": "json"}],
    }


def apply_runtime_config_update(patch: dict[str, Any]) -> dict[str, Any]:
    preview = preview_runtime_config_update(patch)
    _write_json(runtime_config_path(), preview["after"])
    return preview


def apply_runtime_enablement_update(runtime_id: str, *, enabled: bool) -> dict[str, Any]:
    preview = preview_runtime_enablement_update(runtime_id, enabled=enabled)
    _write_json(runtime_config_path(), preview["after"])
    return preview


def preview_agent_surface_update(
    agent_id: str,
    *,
    config_patch: dict[str, Any] | None = None,
    harness_patch: dict[str, str] | None = None,
) -> dict[str, Any]:
    config_path = agent_config_path(agent_id)
    harness_dir = agent_harness_dir(agent_id)
    current_config = _load_json(config_path)
    merged_config = _merge_dicts(current_config, config_patch or {})
    harness_patch = harness_patch or {}
    before_harness = {
        raw_path: (
            (harness_dir / _safe_relative_path(raw_path)).read_text(encoding="utf-8")
            if (harness_dir / _safe_relative_path(raw_path)).exists()
            else ""
        )
        for raw_path in harness_patch
    }
    after_harness = {raw_path: content for raw_path, content in harness_patch.items()}
    return {
        "surface": "aria.agent",
        "agent_id": agent_id,
        "config_path": str(config_path),
        "harness_dir": str(harness_dir),
        "before": {"config": current_config, "harness": before_harness},
        "after": {"config": merged_config, "harness": after_harness},
        "writes": (
            [{"path": str(config_path), "kind": "json"}]
            + [
                {
                    "path": str(harness_dir / _safe_relative_path(raw_path)),
                    "kind": "text",
                }
                for raw_path in harness_patch
            ]
        ),
    }


def apply_agent_surface_update(
    agent_id: str,
    *,
    config_patch: dict[str, Any] | None = None,
    harness_patch: dict[str, str] | None = None,
) -> dict[str, Any]:
    preview = preview_agent_surface_update(
        agent_id,
        config_patch=config_patch,
        harness_patch=harness_patch,
    )
    _write_json(agent_config_path(agent_id), preview["after"]["config"])
    harness_dir = agent_harness_dir(agent_id)
    for raw_path, content in (harness_patch or {}).items():
        target = harness_dir / _safe_relative_path(raw_path)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content, encoding="utf-8")
    return preview
