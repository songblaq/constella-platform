from __future__ import annotations

import json
import os
import re
from datetime import date, datetime
from pathlib import Path
from typing import Any

try:  # pragma: no cover - fallback only matters when PyYAML is unavailable.
    import yaml
except Exception:  # pragma: no cover
    yaml = None


SECTION_NAMES = ("Backlog", "Ready", "Doing", "Review", "Done", "Blocked")


def agenthive_home() -> Path:
    override = os.environ.get("AGENTHIVE_HOME")
    if override:
        return Path(override).expanduser()
    return Path.home() / ".agenthive"


def _load_text(path: Path) -> str | None:
    if not path.exists():
        return None
    return path.read_text(encoding="utf-8")


def _parse_scalar(value: str) -> Any:
    text = value.strip()
    if text == "null" or text == "~":
        return None
    if text == "true":
        return True
    if text == "false":
        return False
    if text == "[]":
        return []
    if text == "{}":
        return {}
    if (text.startswith('"') and text.endswith('"')) or (text.startswith("'") and text.endswith("'")):
        return text[1:-1]
    if re.fullmatch(r"-?\d+", text):
        return int(text)
    if re.fullmatch(r"-?\d+\.\d+", text):
        return float(text)
    return text


def _yaml_fallback_load(text: str) -> Any:
    lines = [line.rstrip("\n") for line in text.splitlines() if line.strip() and not line.lstrip().startswith("#")]

    def parse_block(index: int, indent: int) -> tuple[Any, int]:
        if index >= len(lines):
            return {}, index

        stripped = lines[index].lstrip(" ")
        current_indent = len(lines[index]) - len(stripped)
        if current_indent < indent:
            return {}, index

        if stripped.startswith("- "):
            items: list[Any] = []
            while index < len(lines):
                stripped = lines[index].lstrip(" ")
                current_indent = len(lines[index]) - len(stripped)
                if current_indent < indent or not stripped.startswith("- "):
                    break
                item_text = stripped[2:].strip()
                index += 1
                if item_text:
                    if ":" in item_text and not item_text.startswith(("'", '"')):
                        key, remainder = item_text.split(":", 1)
                        item: dict[str, Any] = {key.strip(): _parse_scalar(remainder.strip()) if remainder.strip() else None}
                        while index < len(lines):
                            next_stripped = lines[index].lstrip(" ")
                            next_indent = len(lines[index]) - len(next_stripped)
                            if next_indent <= current_indent:
                                break
                            nested, index = parse_block(index, current_indent + 2)
                            if isinstance(nested, dict):
                                item.update(nested)
                            else:
                                item = nested
                                break
                        items.append(item)
                    else:
                        items.append(_parse_scalar(item_text))
                else:
                    nested, index = parse_block(index, current_indent + 2)
                    items.append(nested)
            return items, index

        mapping: dict[str, Any] = {}
        while index < len(lines):
            stripped = lines[index].lstrip(" ")
            current_indent = len(lines[index]) - len(stripped)
            if current_indent < indent:
                break
            if stripped.startswith("- "):
                break
            if ":" not in stripped:
                index += 1
                continue
            key, remainder = stripped.split(":", 1)
            key = key.strip()
            remainder = remainder.strip()
            index += 1
            if remainder:
                mapping[key] = _parse_scalar(remainder)
                continue
            nested, index = parse_block(index, current_indent + 2)
            mapping[key] = nested
        return mapping, index

    parsed, _ = parse_block(0, 0)
    return parsed


def _load_yaml(path: Path) -> Any:
    text = _load_text(path)
    if text is None:
        return None
    if not text.strip():
        return None
    if yaml is not None:
        return yaml.safe_load(text)
    return _yaml_fallback_load(text)


def _read_yaml_dict(path: Path) -> dict[str, Any]:
    data = _load_yaml(path)
    if isinstance(data, dict):
        return data
    return {}


def _yaml_dump(data: Any) -> str:
    normalized = _normalize_scalars(data)
    if yaml is not None:
        return yaml.safe_dump(normalized, sort_keys=False, default_flow_style=False, allow_unicode=True)
    return _yaml_fallback_dump(normalized)


def _yaml_fallback_dump(data: Any, indent: int = 0) -> str:
    prefix = " " * indent
    if isinstance(data, dict):
        lines: list[str] = []
        for key, value in data.items():
            rendered_key = str(key)
            if isinstance(value, dict):
                lines.append(f"{prefix}{rendered_key}:")
                lines.append(_yaml_fallback_dump(value, indent + 2))
            elif isinstance(value, list):
                lines.append(f"{prefix}{rendered_key}:")
                lines.append(_yaml_fallback_dump(value, indent + 2))
            else:
                lines.append(f"{prefix}{rendered_key}: {_yaml_fallback_scalar(value)}")
        return "\n".join(lines)
    if isinstance(data, list):
        lines = []
        for item in data:
            if isinstance(item, dict):
                nested = _yaml_fallback_dump(item, indent + 2)
                nested_lines = nested.splitlines()
                lines.append(f"{prefix}- {nested_lines[0].strip()}")
                lines.extend(f"{' ' * (indent + 2)}{line.strip()}" for line in nested_lines[1:])
            elif isinstance(item, list):
                nested = _yaml_fallback_dump(item, indent + 2)
                nested_lines = nested.splitlines()
                lines.append(f"{prefix}- {nested_lines[0].strip()}")
                lines.extend(f"{' ' * (indent + 2)}{line.strip()}" for line in nested_lines[1:])
            else:
                lines.append(f"{prefix}- {_yaml_fallback_scalar(item)}")
        return "\n".join(lines)
    return f"{prefix}{_yaml_fallback_scalar(data)}"


def _yaml_fallback_scalar(value: Any) -> str:
    if value is None:
        return "null"
    if value is True:
        return "true"
    if value is False:
        return "false"
    if isinstance(value, (int, float)):
        return str(value)
    return json.dumps(str(value), ensure_ascii=False)


def _write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def registry_path(home: Path | None = None) -> Path:
    return (home or agenthive_home()) / "registry.yaml"


def projects_root(home: Path | None = None) -> Path:
    return (home or agenthive_home()) / "projects"


def project_root(slug: str, home: Path | None = None) -> Path:
    return projects_root(home) / slug


def project_yaml_path(slug: str, home: Path | None = None) -> Path:
    return project_root(slug, home) / "project.yaml"


def project_backlog_path(slug: str, home: Path | None = None) -> Path:
    return project_root(slug, home) / "tasks" / "BACKLOG.md"


def list_projects(home: Path | None = None) -> list[dict[str, Any]]:
    registry = _read_yaml_dict(registry_path(home))
    projects = registry.get("projects", [])
    if isinstance(projects, list):
        return [_normalize_scalars(item) for item in projects if isinstance(item, dict)]
    return []


def _normalize_scalars(value: Any) -> Any:
    if isinstance(value, dict):
        return {key: _normalize_scalars(item) for key, item in value.items()}
    if isinstance(value, list):
        return [_normalize_scalars(item) for item in value]
    if isinstance(value, tuple):
        return [_normalize_scalars(item) for item in value]
    if isinstance(value, (datetime, date)):
        return value.isoformat()
    if isinstance(value, Path):
        return str(value)
    return value


def _mapping_or_raise(payload: Any, kind: str) -> dict[str, Any]:
    if not isinstance(payload, dict):
        raise TypeError(f"AgentHive {kind} payload must be a mapping")
    return payload


def _project_document(project: dict[str, Any]) -> dict[str, Any]:
    document = {
        "id": project.get("id", project.get("slug")),
        "slug": project.get("slug"),
        "name": project.get("name"),
        "description": project.get("description"),
        "path": project.get("path"),
        "active": project.get("active"),
        "created_at": project.get("created_at"),
        "updated_at": project.get("updated_at"),
        "paths": project.get("paths"),
        "active_agents": project.get("active_agents"),
        "branching": project.get("branching"),
        "git": project.get("git"),
        "review": project.get("review"),
    }
    return {key: value for key, value in document.items() if value is not None}


def _merge_project_record(project: dict[str, Any], home: Path | None = None) -> dict[str, Any]:
    slug = str(project.get("slug", "")).strip()
    if not slug:
        raise KeyError("AgentHive project upsert requires a slug")

    existing = get_project(slug, home)
    merged: dict[str, Any] = {}
    if existing is not None:
        merged.update(existing)
    merged.update(_normalize_scalars(project))
    merged["slug"] = slug
    merged["id"] = merged.get("id") or slug
    merged["name"] = merged.get("name") or slug
    if merged.get("path") is None:
        if existing is not None and existing.get("path") is not None:
            merged["path"] = existing.get("path")
        else:
            merged["path"] = str(project_root(slug, home))
    return merged


def _upsert_registry_and_project(
    project: dict[str, Any], home: Path | None = None, preview: bool = False
) -> dict[str, Any]:
    merged = _merge_project_record(project, home)
    registry_file = registry_path(home)
    project_file = project_yaml_path(str(merged["slug"]), home)

    registry = _read_yaml_dict(registry_file)
    projects = registry.get("projects", [])
    if not isinstance(projects, list):
        projects = []

    updated_projects: list[dict[str, Any]] = []
    replaced = False
    for item in projects:
        if isinstance(item, dict) and str(item.get("slug", "")).casefold() == str(merged["slug"]).casefold():
            updated_projects.append({**_normalize_scalars(item), **merged})
            replaced = True
        elif isinstance(item, dict):
            updated_projects.append(_normalize_scalars(item))
    if not replaced:
        updated_projects.append(merged)

    registry_doc = _normalize_scalars({**registry, "projects": updated_projects})
    project_doc = _project_document(merged)
    writes = [
        {"path": str(registry_file), "kind": "registry", "content": _yaml_dump(registry_doc)},
        {"path": str(project_file), "kind": "project", "content": _yaml_dump(project_doc)},
    ]

    if not preview:
        for item in writes:
            _write_text(Path(item["path"]), item["content"])

    return {
        "preview": preview,
        "project": merged,
        "writes": writes,
    }


def preview_project_upsert(project: dict[str, Any], home: Path | None = None) -> dict[str, Any]:
    return _upsert_registry_and_project(_mapping_or_raise(project, "project"), home=home, preview=True)


def upsert_project(project: dict[str, Any], home: Path | None = None) -> dict[str, Any]:
    return _upsert_registry_and_project(_mapping_or_raise(project, "project"), home=home, preview=False)


def _task_document(task: dict[str, Any]) -> dict[str, Any]:
    document = {
        "id": task.get("id"),
        "title": task.get("title"),
        "category": task.get("category"),
        "tags": task.get("tags"),
        "workflow_mode": task.get("workflow_mode"),
        "status": task.get("status"),
        "priority": task.get("priority"),
        "owner": task.get("owner"),
        "role": task.get("role"),
        "created_by": task.get("created_by"),
        "created_at": task.get("created_at"),
        "scope": task.get("scope"),
        "acceptance": task.get("acceptance"),
        "branch": task.get("branch"),
        "handoff": task.get("handoff"),
    }
    return {key: value for key, value in document.items() if value is not None}


def _merge_task_record(project_slug: str, task: dict[str, Any], home: Path | None = None) -> dict[str, Any]:
    task_id = str(task.get("id", "")).strip()
    if not task_id:
        raise KeyError("AgentHive task upsert requires an id")

    existing_task = next((item for item in list_project_tasks(project_slug, home) if str(item.get("id")) == task_id), None)
    merged: dict[str, Any] = {}
    if existing_task is not None:
        merged.update(existing_task)
    merged.update(_normalize_scalars(task))
    merged["id"] = task_id
    for key in ("task_path", "task_dir", "project_slug"):
        merged.pop(key, None)
    return merged


def _upsert_task_record(
    project_slug_or_name: str, task: dict[str, Any], home: Path | None = None, preview: bool = False
) -> dict[str, Any]:
    project = _resolve_project(project_slug_or_name, home)
    project_slug = str(project["slug"])
    merged = _merge_task_record(project_slug, task, home)
    task_file = project_root(project_slug, home) / "tasks" / merged["id"] / "task.yaml"
    task_doc = _task_document(merged)
    write = {"path": str(task_file), "kind": "task", "content": _yaml_dump(task_doc)}

    if not preview:
        _write_text(task_file, write["content"])

    return {
        "preview": preview,
        "project_slug": project_slug,
        "task": merged,
        "writes": [write],
    }


def preview_task_upsert(
    project_slug_or_name: str, task: dict[str, Any], home: Path | None = None
) -> dict[str, Any]:
    return _upsert_task_record(project_slug_or_name, _mapping_or_raise(task, "task"), home=home, preview=True)


def upsert_task(project_slug_or_name: str, task: dict[str, Any], home: Path | None = None) -> dict[str, Any]:
    return _upsert_task_record(project_slug_or_name, _mapping_or_raise(task, "task"), home=home, preview=False)


def _file_snapshot(path: Path, kind: str) -> dict[str, Any]:
    if not path.exists():
        raise FileNotFoundError(f"missing AgentHive {kind} file: {path}")
    return {
        "path": str(path),
        "kind": kind,
        "content": path.read_text(encoding="utf-8"),
    }


def _delete_guardrails(preview: bool, rollback_files: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [
        {
            "name": "preview_first",
            "status": "preview" if preview else "execute",
            "detail": "Deletion is preview-only unless execute=True is passed explicitly",
        },
        {
            "name": "narrow_scope",
            "status": "pass",
            "detail": "Only the managed AgentHive YAML records listed in deletes are targeted",
        },
        {
            "name": "rollback_snapshot",
            "status": "pass" if rollback_files and all("content" in target for target in rollback_files) else "blocked",
            "detail": "Rollback metadata captures exact file content before deletion",
        },
    ]


def _delete_project_record(project_slug_or_name: str, home: Path | None = None, execute: bool = False) -> dict[str, Any]:
    project = _resolve_project(project_slug_or_name, home)
    project_slug = str(project["slug"])
    registry_file = registry_path(home)
    project_file = project_yaml_path(project_slug, home)
    deletes = [
        {"path": str(registry_file), "kind": "registry"},
        {"path": str(project_file), "kind": "project"},
    ]
    rollback_files = [
        _file_snapshot(registry_file, "registry"),
        _file_snapshot(project_file, "project"),
    ]

    if execute:
        registry = _read_yaml_dict(registry_file)
        projects = registry.get("projects", [])
        if not isinstance(projects, list):
            projects = []
        updated_projects = [
            _normalize_scalars(item)
            for item in projects
            if not (
                isinstance(item, dict)
                and str(item.get("slug", "")).casefold() == project_slug.casefold()
            )
        ]
        _write_text(registry_file, _yaml_dump({**registry, "projects": updated_projects}))
        project_file.unlink()

    return {
        "preview": not execute,
        "project": project,
        "deletes": deletes,
        "guardrails": _delete_guardrails(not execute, rollback_files),
        "rollback": {"files": rollback_files},
    }


def preview_project_delete(project_slug_or_name: str, home: Path | None = None) -> dict[str, Any]:
    return _delete_project_record(project_slug_or_name, home=home, execute=False)


def delete_project(
    project_slug_or_name: str, home: Path | None = None, execute: bool = False
) -> dict[str, Any]:
    return _delete_project_record(project_slug_or_name, home=home, execute=execute)


def _delete_task_record(
    project_slug_or_name: str, task_id: str, home: Path | None = None, execute: bool = False
) -> dict[str, Any]:
    project = _resolve_project(project_slug_or_name, home)
    project_slug = str(project["slug"])
    cleaned_task_id = str(task_id).strip()
    if not re.fullmatch(r"TASK-\d+", cleaned_task_id):
        raise ValueError("AgentHive task delete requires a TASK-### id")

    task = next(
        (item for item in list_project_tasks(project_slug, home) if str(item.get("id")) == cleaned_task_id),
        None,
    )
    if task is None:
        raise KeyError(f"unknown AgentHive task: {cleaned_task_id}")

    task_file = project_root(project_slug, home) / "tasks" / cleaned_task_id / "task.yaml"
    deletes = [{"path": str(task_file), "kind": "task"}]
    rollback_files = [_file_snapshot(task_file, "task")]

    if execute:
        task_file.unlink()

    return {
        "preview": not execute,
        "project_slug": project_slug,
        "task": task,
        "deletes": deletes,
        "guardrails": _delete_guardrails(not execute, rollback_files),
        "rollback": {"files": rollback_files},
    }


def preview_task_delete(
    project_slug_or_name: str, task_id: str, home: Path | None = None
) -> dict[str, Any]:
    return _delete_task_record(project_slug_or_name, task_id, home=home, execute=False)


def delete_task(
    project_slug_or_name: str, task_id: str, home: Path | None = None, execute: bool = False
) -> dict[str, Any]:
    return _delete_task_record(project_slug_or_name, task_id, home=home, execute=execute)


def get_project(slug_or_name: str, home: Path | None = None) -> dict[str, Any] | None:
    target = slug_or_name.casefold()
    for project in list_projects(home):
        slug = str(project.get("slug", "")).casefold()
        name = str(project.get("name", "")).casefold()
        if target == slug or target == name:
            return project
    return None


def _resolve_project(slug_or_name: str, home: Path | None = None) -> dict[str, Any]:
    project = get_project(slug_or_name, home)
    if project is None:
        raise KeyError(f"unknown AgentHive project: {slug_or_name}")
    return project


def _task_sort_key(task: dict[str, Any]) -> tuple[int, str]:
    task_id = str(task.get("id", ""))
    match = re.search(r"(\d+)$", task_id)
    return (int(match.group(1)) if match else 10**9, task_id)


def list_project_tasks(slug_or_name: str, home: Path | None = None) -> list[dict[str, Any]]:
    project = _resolve_project(slug_or_name, home)
    slug = str(project["slug"])
    tasks_dir = project_root(slug, home) / "tasks"
    if not tasks_dir.exists():
        return []

    tasks: list[dict[str, Any]] = []
    for item in tasks_dir.iterdir():
        if not item.is_dir() or not item.name.startswith("TASK-"):
            continue
        task = _read_yaml_dict(item / "task.yaml")
        if not task:
            continue
        task["task_path"] = str(item / "task.yaml")
        task["task_dir"] = str(item)
        task["project_slug"] = slug
        tasks.append(task)

    tasks.sort(key=_task_sort_key)
    return tasks


_BACKLOG_ITEM_RE = re.compile(
    r"^-\s+(TASK-\d+)\s+\|\s+(?P<title>.+?)\s+\|\s+(?P<priority>.+?)\s+\|\s+(?P<owner>.+?)(?:\s+→.*)?$"
)


def parse_backlog_markdown(text: str) -> dict[str, Any]:
    heading = None
    sections: dict[str, list[dict[str, Any]]] = {name: [] for name in SECTION_NAMES}
    current_section: str | None = None

    for line in text.splitlines():
        stripped = line.strip()
        if not stripped:
            continue
        if stripped.startswith("# Task Index"):
            heading = stripped
            continue
        if stripped.startswith("## "):
            section = stripped[3:].strip()
            current_section = section if section in sections else None
            continue
        if current_section is None:
            continue
        match = _BACKLOG_ITEM_RE.match(stripped)
        if not match:
            continue
        owner = _normalize_owner(match.group("owner").strip(), current_section)
        sections[current_section].append(
            {
                "id": match.group(1),
                "title": match.group("title").strip(),
                "priority": match.group("priority").strip(),
                "owner": owner,
                "status": current_section.lower(),
            }
        )

    return {
        "title": heading,
        "sections": sections,
        "section_counts": {name: len(items) for name, items in sections.items()},
        "total_items": sum(len(items) for items in sections.values()),
    }


def backlog_summary(slug_or_name: str, home: Path | None = None) -> dict[str, Any]:
    project = _resolve_project(slug_or_name, home)
    backlog_path = project_backlog_path(str(project["slug"]), home)
    text = _load_text(backlog_path) or ""
    summary = parse_backlog_markdown(text)
    summary["project"] = {
        "slug": project.get("slug"),
        "name": project.get("name"),
        "path": project.get("path"),
    }
    summary["path"] = str(backlog_path)
    return summary


def _normalize_owner(raw_owner: str, current_section: str) -> str | None:
    cleaned = raw_owner.removeprefix("@")
    section_marker = current_section.lower()
    if cleaned in {"unassigned", "ready", "review", "backlog", "blocked", section_marker}:
        return None
    if cleaned.startswith("**") and cleaned.endswith("**"):
        return None
    return cleaned
