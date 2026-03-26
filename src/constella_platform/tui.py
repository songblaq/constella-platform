from __future__ import annotations

import argparse

from constella_platform.domains import aria_runtime, orbit, program_history
from constella_platform.service import CapabilityService


def build_shell_snapshot() -> dict:
    service = CapabilityService()
    capabilities = service.invoke("capabilities.list")["data"]
    plans = program_history.list_plans()
    lessons = program_history.list_lessons()
    findings = program_history.list_findings()
    decisions = program_history.list_decisions()

    runtimes = aria_runtime.list_runtimes()
    nyx_agents = aria_runtime.list_nyx_agents()

    try:
        orbit_snapshot = orbit.read_snapshot()
        orbit_health = {
            "available": True,
            "status": orbit_snapshot["status"].get("summary")
            or orbit_snapshot["status"].get("state")
            or orbit_snapshot["status"].get("mode", "unknown"),
            "sync_available": orbit_snapshot["sync"].get("available", False),
            "value": orbit_snapshot,
        }
    except Exception as exc:  # pragma: no cover - defensive on live systems
        orbit_health = {"available": False, "error": str(exc)}

    return {
        "capabilities": {
            "count": len(capabilities),
            "registered": [item["capability_id"] for item in capabilities],
        },
        "history": {
            "plans": {"count": len(plans), "latest": plans[-1]["title"] if plans else None},
            "lessons": {"count": len(lessons), "latest": lessons[-1]["title"] if lessons else None},
            "findings": {"count": len(findings), "latest": findings[-1]["title"] if findings else None},
            "decisions": {"count": len(decisions), "latest": decisions[-1]["title"] if decisions else None},
        },
        "health": {
            "runtimes": {"available": True, "value": runtimes},
            "nyx_agents": {"available": True, "value": nyx_agents},
            "orbit": orbit_health,
        },
    }


def render_shell(snapshot: dict) -> str:
    lines = [
        "Constella Platform Shell",
        "========================",
        "",
        "[Capabilities]",
        f"registered: {snapshot['capabilities']['count']}",
        "",
        "[History]",
        f"plans: {snapshot['history']['plans']['count']} latest={snapshot['history']['plans']['latest']}",
        f"lessons: {snapshot['history']['lessons']['count']} latest={snapshot['history']['lessons']['latest']}",
        f"findings: {snapshot['history']['findings']['count']} latest={snapshot['history']['findings']['latest']}",
        f"decisions: {snapshot['history']['decisions']['count']} latest={snapshot['history']['decisions']['latest']}",
        "",
        "[Health]",
        f"runtimes: {len(snapshot['health']['runtimes']['value'])}",
        f"nyx_agents: {len(snapshot['health']['nyx_agents']['value'])}",
    ]
    orbit_health = snapshot["health"]["orbit"]
    if orbit_health.get("available"):
        lines.append(f"orbit: {orbit_health['status']}")
    else:
        lines.append(f"orbit: unavailable ({orbit_health.get('error', 'unknown')})")
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="constella-tui")
    parser.add_argument("--once", action="store_true", help="Render a single snapshot")
    parser.parse_args(argv)
    print(render_shell(build_shell_snapshot()))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
