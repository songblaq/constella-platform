import json

from constella_platform.service import CapabilityService


def test_service_exposes_agenthive_and_orbit_capabilities(tmp_path, monkeypatch):
    agenthive_home = tmp_path / ".agenthive"
    project_tasks = agenthive_home / "projects" / "alpha" / "tasks"
    project_tasks.mkdir(parents=True)
    (agenthive_home / "registry.yaml").write_text(
        """
version: "1.0"
projects:
  - slug: "alpha"
    name: "Alpha"
    path: "/work/alpha"
""".strip()
        + "\n",
        encoding="utf-8",
    )
    (project_tasks / "BACKLOG.md").write_text(
        """
# Task Index — Alpha

## Ready
- TASK-001 | First | high | unassigned
""".strip()
        + "\n",
        encoding="utf-8",
    )

    orbit_home = tmp_path / ".aria" / "orbit"
    orbit_home.mkdir(parents=True)
    (orbit_home / "orbit-status.json").write_text('{"mode":"active","tick_count_24h":12}', encoding="utf-8")
    log_dir = orbit_home / "log"
    log_dir.mkdir()
    (log_dir / "orbit-hive-sync.stdout.log").write_text(
        "\n".join(
            [
                "[orbit-hive-sync] 동기화 시작",
                "  AH → ORBIT 신규 등록: 0 tasks",
                "  AH → ORBIT: 10 tasks 상태 캐싱",
                "  ORBIT → Collab: 0 runs 기록",
                "[orbit-hive-sync] 동기화 완료",
            ]
        ),
        encoding="utf-8",
    )

    monkeypatch.setenv("CONSTELLAR_HOME", str(tmp_path / ".constellar"))
    monkeypatch.setenv("AGENTHIVE_HOME", str(agenthive_home))
    monkeypatch.setenv("CONSTELLA_ARIA_HOME", str(tmp_path / ".aria"))

    service = CapabilityService()

    projects = service.invoke("agenthive.project.list")["data"]
    backlog = service.invoke("agenthive.backlog.summary", {"project": "alpha"})["data"]
    orbit = service.invoke("orbit.snapshot")["data"]

    assert projects[0]["slug"] == "alpha"
    assert backlog["total_items"] == 1
    assert orbit["status"]["mode"] == "active"
    assert orbit["sync"]["cached_task_count"] == 10
