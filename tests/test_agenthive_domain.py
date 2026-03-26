from __future__ import annotations

from pathlib import Path

from constella_platform.domains.agenthive import (
    backlog_summary,
    delete_project,
    delete_task,
    get_project,
    list_project_tasks,
    list_projects,
    preview_project_upsert,
    preview_project_delete,
    preview_task_upsert,
    preview_task_delete,
    upsert_project,
    upsert_task,
)


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def create_agenthive_hub(tmp_path: Path) -> Path:
    home = tmp_path / ".agenthive"
    write_text(
        home / "registry.yaml",
        """
version: "1.0"
projects:
  - slug: "alpha-platform"
    name: "Alpha Platform"
    path: "/work/alpha-platform"
    active: true
    created_at: "2026-03-26T00:00:00Z"
  - slug: "beta-platform"
    name: "Beta Platform"
    path: "/work/beta-platform"
    active: false
    created_at: "2026-03-26T00:00:00Z"
""".strip()
        + "\n",
    )
    write_text(
        home / "projects" / "alpha-platform" / "project.yaml",
        """
id: "alpha-platform"
name: "Alpha Platform"
description: "Primary platform project"
slug: "alpha-platform"
paths:
  - "/work/alpha-platform"
git:
  remote: null
  default_branch: "main"
branching:
  pattern: "agent/{agent-id}/{task-id}"
  base: "main"
review:
  max_rounds: 2
  require_test_pass: true
active_agents: []
created_at: "2026-03-26T00:00:00Z"
""".strip()
        + "\n",
    )
    write_text(
        home / "projects" / "alpha-platform" / "tasks" / "TASK-002" / "task.yaml",
        """
id: "TASK-002"
title: "Second task"
category: "implementation"
tags: []
workflow_mode: "kanban"
status: "ready"
priority: "high"
owner: null
role: null
created_by: "codex"
created_at: "2026-03-26T00:00:00Z"
scope:
  path: "/work/alpha-platform"
  files: []
  not_touch: []
acceptance:
  - "passes tests"
branch: null
handoff:
  next_role: "builder"
  next_agent: null
""".strip()
        + "\n",
    )
    write_text(
        home / "projects" / "alpha-platform" / "tasks" / "TASK-001" / "task.yaml",
        """
id: "TASK-001"
title: "First task"
category: "implementation"
tags: []
workflow_mode: "kanban"
status: "backlog"
priority: "medium"
owner: "mira"
role: null
created_by: "codex"
created_at: "2026-03-26T00:00:00Z"
scope:
  path: "/work/alpha-platform"
  files: []
  not_touch: []
acceptance:
  - "docs updated"
branch: null
handoff:
  next_role: "builder"
  next_agent: null
""".strip()
        + "\n",
    )
    write_text(
        home / "projects" / "alpha-platform" / "tasks" / "BACKLOG.md",
        """
# Task Index — Alpha Platform

## Backlog
- TASK-001 | First task | medium | @mira

## Ready
- TASK-002 | Second task | high | unassigned

## Doing
- 없음

## Review
- TASK-003 | Review task | low | @lee

## Done
- 없음

## Blocked
- TASK-004 | Blocked task | high | @sam
""".strip()
        + "\n",
    )
    return home


def test_list_projects_reads_registry(tmp_path, monkeypatch):
    home = create_agenthive_hub(tmp_path)
    monkeypatch.setenv("AGENTHIVE_HOME", str(home))

    projects = list_projects()

    assert [item["slug"] for item in projects] == ["alpha-platform", "beta-platform"]
    assert projects[0]["name"] == "Alpha Platform"
    assert projects[1]["active"] is False


def test_get_project_matches_slug_or_name(tmp_path, monkeypatch):
    home = create_agenthive_hub(tmp_path)
    monkeypatch.setenv("AGENTHIVE_HOME", str(home))

    by_name = get_project("Alpha Platform")
    by_slug = get_project("alpha-platform")

    assert by_name is not None
    assert by_slug is not None
    assert by_name["slug"] == "alpha-platform"
    assert by_slug["path"] == "/work/alpha-platform"
    assert by_name["created_at"] == "2026-03-26T00:00:00Z"


def test_list_projects_normalizes_yaml_timestamps_to_strings(tmp_path, monkeypatch):
    home = tmp_path / ".agenthive"
    write_text(
        home / "registry.yaml",
        """
version: "1.0"
projects:
  - slug: alpha
    name: Alpha
    path: /work/alpha
    created_at: 2026-03-26T00:00:00Z
""".strip()
        + "\n",
    )
    monkeypatch.setenv("AGENTHIVE_HOME", str(home))

    projects = list_projects()

    assert projects[0]["created_at"] == "2026-03-26T00:00:00Z"


def test_list_project_tasks_reads_and_sorts_task_yaml(tmp_path, monkeypatch):
    home = create_agenthive_hub(tmp_path)
    monkeypatch.setenv("AGENTHIVE_HOME", str(home))

    tasks = list_project_tasks("alpha-platform")

    assert [task["id"] for task in tasks] == ["TASK-001", "TASK-002"]
    assert tasks[0]["status"] == "backlog"
    assert tasks[1]["priority"] == "high"


def test_backlog_summary_extracts_sections_and_counts(tmp_path, monkeypatch):
    home = create_agenthive_hub(tmp_path)
    monkeypatch.setenv("AGENTHIVE_HOME", str(home))

    summary = backlog_summary("alpha-platform")

    assert summary["project"]["slug"] == "alpha-platform"
    assert summary["total_items"] == 4
    assert summary["section_counts"] == {
        "Backlog": 1,
        "Ready": 1,
        "Doing": 0,
        "Review": 1,
        "Done": 0,
        "Blocked": 1,
    }
    assert summary["sections"]["Backlog"][0]["id"] == "TASK-001"
    assert summary["sections"]["Ready"][0]["owner"] is None
    assert summary["sections"]["Blocked"][0]["owner"] == "sam"


def test_preview_project_upsert_reports_writes_without_touching_disk(tmp_path, monkeypatch):
    home = create_agenthive_hub(tmp_path)
    monkeypatch.setenv("AGENTHIVE_HOME", str(home))

    preview = preview_project_upsert(
        {
            "slug": "gamma-platform",
            "name": "Gamma Platform",
            "path": "/work/gamma-platform",
            "active": True,
            "created_at": "2026-03-26T12:00:00Z",
        }
    )

    assert preview["preview"] is True
    assert [item["path"] for item in preview["writes"]] == [
        str(home / "registry.yaml"),
        str(home / "projects" / "gamma-platform" / "project.yaml"),
    ]
    assert "gamma-platform" in preview["writes"][0]["content"]
    assert not (home / "projects" / "gamma-platform").exists()
    assert get_project("gamma-platform") is None


def test_upsert_project_creates_project_files_and_registry_entry(tmp_path, monkeypatch):
    home = create_agenthive_hub(tmp_path)
    monkeypatch.setenv("AGENTHIVE_HOME", str(home))

    result = upsert_project(
        {
            "slug": "gamma-platform",
            "name": "Gamma Platform",
            "path": "/work/gamma-platform",
            "description": "Preview-friendly project write slice",
            "active": True,
        }
    )

    assert result["preview"] is False
    assert result["project"]["slug"] == "gamma-platform"
    assert get_project("gamma-platform")["name"] == "Gamma Platform"
    assert get_project("gamma-platform")["description"] == "Preview-friendly project write slice"
    assert (home / "projects" / "gamma-platform" / "project.yaml").exists()
    assert [item["slug"] for item in list_projects()] == [
        "alpha-platform",
        "beta-platform",
        "gamma-platform",
    ]


def test_preview_task_upsert_reports_single_task_write(tmp_path, monkeypatch):
    home = create_agenthive_hub(tmp_path)
    monkeypatch.setenv("AGENTHIVE_HOME", str(home))

    preview = preview_task_upsert(
        "alpha-platform",
        {
            "id": "TASK-002",
            "title": "Second task revised",
            "status": "doing",
            "owner": "aria",
        },
    )

    assert preview["preview"] is True
    assert preview["writes"][0]["path"] == str(home / "projects" / "alpha-platform" / "tasks" / "TASK-002" / "task.yaml")
    assert preview["writes"][0]["kind"] == "task"
    assert "Second task revised" in preview["writes"][0]["content"]
    assert list_project_tasks("alpha-platform")[1]["title"] == "Second task"


def test_upsert_task_updates_existing_task_without_losing_fields(tmp_path, monkeypatch):
    home = create_agenthive_hub(tmp_path)
    monkeypatch.setenv("AGENTHIVE_HOME", str(home))

    result = upsert_task(
        "alpha-platform",
        {
            "id": "TASK-002",
            "title": "Second task revised",
            "status": "doing",
            "owner": "aria",
        },
    )

    task = next(item for item in list_project_tasks("alpha-platform") if item["id"] == "TASK-002")
    assert result["preview"] is False
    assert task["title"] == "Second task revised"
    assert task["status"] == "doing"
    assert task["owner"] == "aria"
    assert task["workflow_mode"] == "kanban"
    assert task["created_by"] == "codex"
    assert task["scope"]["path"] == "/work/alpha-platform"


def test_preview_project_delete_is_preview_first_and_returns_rollback_metadata(tmp_path, monkeypatch):
    home = create_agenthive_hub(tmp_path)
    monkeypatch.setenv("AGENTHIVE_HOME", str(home))

    preview = preview_project_delete("alpha-platform")

    assert preview["preview"] is True
    assert {item["path"] for item in preview["deletes"]} == {
        str(home / "registry.yaml"),
        str(home / "projects" / "alpha-platform" / "project.yaml"),
    }
    assert preview["rollback"]["files"][0]["content"]
    assert preview["rollback"]["files"][1]["content"]
    assert get_project("alpha-platform") is not None
    assert (home / "projects" / "alpha-platform" / "project.yaml").exists()


def test_delete_project_execute_removes_registry_entry_but_keeps_task_files(tmp_path, monkeypatch):
    home = create_agenthive_hub(tmp_path)
    monkeypatch.setenv("AGENTHIVE_HOME", str(home))

    result = delete_project("alpha-platform", execute=True)

    assert result["preview"] is False
    assert get_project("alpha-platform") is None
    assert [item["slug"] for item in list_projects()] == ["beta-platform"]
    assert not (home / "projects" / "alpha-platform" / "project.yaml").exists()
    assert (home / "projects" / "alpha-platform" / "tasks" / "TASK-001" / "task.yaml").exists()
    assert (home / "projects" / "alpha-platform" / "tasks" / "TASK-002" / "task.yaml").exists()


def test_preview_task_delete_is_preview_first_and_returns_rollback_metadata(tmp_path, monkeypatch):
    home = create_agenthive_hub(tmp_path)
    monkeypatch.setenv("AGENTHIVE_HOME", str(home))

    preview = preview_task_delete("alpha-platform", "TASK-002")

    assert preview["preview"] is True
    assert preview["deletes"] == [
        {"path": str(home / "projects" / "alpha-platform" / "tasks" / "TASK-002" / "task.yaml"), "kind": "task"}
    ]
    assert "Second task" in preview["rollback"]["files"][0]["content"]
    assert list_project_tasks("alpha-platform")[1]["title"] == "Second task"


def test_delete_task_execute_removes_only_task_manifest(tmp_path, monkeypatch):
    home = create_agenthive_hub(tmp_path)
    monkeypatch.setenv("AGENTHIVE_HOME", str(home))

    result = delete_task("alpha-platform", "TASK-002", execute=True)

    assert result["preview"] is False
    assert not (home / "projects" / "alpha-platform" / "tasks" / "TASK-002" / "task.yaml").exists()
    assert (home / "projects" / "alpha-platform" / "tasks" / "TASK-001" / "task.yaml").exists()
    assert [task["id"] for task in list_project_tasks("alpha-platform")] == ["TASK-001"]
