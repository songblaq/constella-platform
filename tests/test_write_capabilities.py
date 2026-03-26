import json

from constella_platform.service import CapabilityService


def test_service_supports_preview_and_apply_for_write_domains(tmp_path, monkeypatch):
    constellar_home = tmp_path / ".constellar"
    agenthive_home = tmp_path / ".agenthive"
    aria_home = tmp_path / ".aria"
    orbit_home = aria_home / "orbit"
    agent_dir = aria_home / "agents" / "browser"
    harness_dir = agent_dir / "harness"

    monkeypatch.setenv("CONSTELLAR_HOME", str(constellar_home))
    monkeypatch.setenv("AGENTHIVE_HOME", str(agenthive_home))
    monkeypatch.setenv("CONSTELLA_ARIA_HOME", str(aria_home))

    (agenthive_home / "projects" / "alpha" / "tasks").mkdir(parents=True)
    aria_home.mkdir(parents=True)
    (agenthive_home / "registry.yaml").write_text(
        'version: "1.0"\nprojects:\n  - slug: "alpha"\n    name: "Alpha"\n    path: "/work/alpha"\n',
        encoding="utf-8",
    )
    (aria_home / "config.json").write_text(
        json.dumps({"runtimes": {"codex": {"enabled": True, "type": "cli"}}}),
        encoding="utf-8",
    )
    harness_dir.mkdir(parents=True)
    (agent_dir / "config.json").write_text(json.dumps({"id": "browser", "model": "old"}), encoding="utf-8")
    (harness_dir / "README.md").write_text("old\n", encoding="utf-8")
    orbit_home.mkdir(parents=True)
    (orbit_home / "schedule.json").write_text(json.dumps({"window": {"start": "01:00"}}), encoding="utf-8")

    service = CapabilityService()

    project_preview = service.invoke(
        "agenthive.project.upsert",
        {"project": {"slug": "beta", "name": "Beta"}, "execute": False},
    )["data"]
    assert project_preview["preview"] is True

    project_apply = service.invoke(
        "agenthive.project.upsert",
        {"project": {"slug": "beta", "name": "Beta", "path": "/work/beta"}, "execute": True},
    )["data"]
    assert project_apply["preview"] is False

    task_apply = service.invoke(
        "agenthive.task.upsert",
        {
            "project": "alpha",
            "task": {"id": "TASK-010", "title": "Write wave", "status": "ready", "priority": "high"},
            "execute": True,
        },
    )["data"]
    assert task_apply["project_slug"] == "alpha"

    orbit_preview = service.invoke(
        "orbit.schedule.update",
        {"path": str(orbit_home / "schedule.json"), "updates": {"window": {"start": "03:00"}}, "execute": False},
    )["data"]
    assert orbit_preview["mode"] == "preview"

    runtime_apply = service.invoke(
        "aria.runtime.config.update",
        {"patch": {"runtimes": {"codex": {"enabled": False}}}, "execute": True},
    )["data"]
    assert runtime_apply["after"]["runtimes"]["codex"]["enabled"] is False

    runtime_enablement_preview = service.invoke(
        "aria.runtime.enablement.update",
        {"runtime_id": "codex", "enabled": False, "execute": False},
    )["data"]
    assert runtime_enablement_preview["runtime_id"] == "codex"
    assert runtime_enablement_preview["after"]["runtimes"]["codex"]["enabled"] is False

    agent_apply = service.invoke(
        "aria.agent.surface.update",
        {
            "agent_id": "browser",
            "config_patch": {"model": "new"},
            "harness_patch": {"README.md": "updated\n"},
            "execute": True,
        },
    )["data"]
    assert agent_apply["after"]["config"]["model"] == "new"
