import json

from constella_platform.service import CapabilityService
from constella_platform.tui import build_shell_snapshot, render_shell


def _write_json(path, payload):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload), encoding="utf-8")


def test_tui_snapshot_renders_core_summaries(tmp_path, monkeypatch):
    constellar_home = tmp_path / ".constellar"
    aria_home = tmp_path / ".aria"
    orbit_home = aria_home / "orbit"

    monkeypatch.setenv("CONSTELLAR_HOME", str(constellar_home))
    monkeypatch.setenv("CONSTELLA_ARIA_HOME", str(aria_home))

    service = CapabilityService()
    service.invoke("program.plan.create", {"title": "Constella shell", "summary": "foundation"})
    service.invoke(
        "history.lesson.create",
        {
            "title": "missing shell",
            "why_failed": "ui was not wired",
            "what_was_missed": "a local terminal surface",
            "next_guardrail": "ship the shell first",
        },
    )
    service.invoke(
        "review.finding.create",
        {
            "title": "no shell entrypoint",
            "severity": "medium",
            "detail": "terminal surface was not exposed yet",
        },
    )
    service.invoke(
        "decision.create",
        {
            "title": "build shell foundation",
            "rationale": "a standalone terminal view reduces web coupling",
            "disposition": "accepted",
        },
    )

    _write_json(
        aria_home / "config.json",
        {
            "runtimes": {
                "openclaw": {"enabled": True, "type": "gateway"},
                "codex": {"enabled": False, "type": "cli"},
            }
        },
    )
    for name in ["infra", "navigator"]:
        agent_dir = aria_home / "agents" / name
        agent_dir.mkdir(parents=True, exist_ok=True)
        _write_json(agent_dir / "config.json", {"id": name})

    _write_json(
        orbit_home / "orbit-status.json",
        {
            "state": "green",
            "summary": "status file available",
        },
    )
    (orbit_home / "log").mkdir(parents=True, exist_ok=True)
    (orbit_home / "log" / "orbit-hive-sync.stdout.log").write_text(
        "\n".join(
            [
                "[orbit-hive-sync] 동기화 시작",
                "AH → ORBIT 신규 등록: 2 tasks",
                "AH → ORBIT: 7 tasks 상태 캐싱",
                "ORBIT → Collab: 4 runs 기록",
                "[orbit-hive-sync] 동기화 완료",
            ]
        ),
        encoding="utf-8",
    )

    snapshot = build_shell_snapshot()

    assert snapshot["capabilities"]["count"] > 0
    assert snapshot["history"]["plans"]["latest"] == "Constella shell"
    assert snapshot["history"]["lessons"]["latest"] == "missing shell"
    assert snapshot["history"]["findings"]["latest"] == "no shell entrypoint"
    assert snapshot["history"]["decisions"]["latest"] == "build shell foundation"
    assert snapshot["health"]["runtimes"]["available"] is True
    assert len(snapshot["health"]["runtimes"]["value"]) == 2
    assert snapshot["health"]["nyx_agents"]["available"] is True
    assert len(snapshot["health"]["nyx_agents"]["value"]) == 2
    assert snapshot["health"]["orbit"]["available"] is True
    assert snapshot["health"]["orbit"]["status"] == "status file available"
    assert snapshot["health"]["orbit"]["sync_available"] is True

    rendered = render_shell(snapshot)
    assert "Constella Platform Shell" in rendered
    assert "[Capabilities]" in rendered
    assert "[History]" in rendered
    assert "[Health]" in rendered
    assert "registered:" in rendered
    assert "orbit: status file available" in rendered


def test_tui_snapshot_handles_orbit_failure(tmp_path, monkeypatch):
    monkeypatch.setenv("CONSTELLAR_HOME", str(tmp_path / ".constellar"))
    monkeypatch.setenv("CONSTELLA_ARIA_HOME", str(tmp_path / ".aria"))

    def raise_orbit_error():
        raise RuntimeError("orbit offline")

    monkeypatch.setattr("constella_platform.tui.orbit.read_snapshot", raise_orbit_error)

    snapshot = build_shell_snapshot()

    assert snapshot["health"]["orbit"]["available"] is False
    assert "orbit offline" in snapshot["health"]["orbit"]["error"]
    rendered = render_shell(snapshot)
    assert "orbit: unavailable" in rendered
