from __future__ import annotations

from typing import Any


REQUIRED_SURFACES = ("cli", "api", "tui", "gui")


def build_shell_parity_report(*, capabilities: list[dict[str, Any]], shell_status: dict[str, bool]) -> dict[str, Any]:
    rows = []
    gaps = []
    for item in capabilities:
        available = set(item.get("surfaces", []))
        missing = [surface for surface in REQUIRED_SURFACES if surface not in available]
        row = {
            "capability_id": item["capability_id"],
            "available_surfaces": sorted(available),
            "missing_surfaces": missing,
        }
        rows.append(row)
        if missing:
            gaps.append(row)
    return {
        "shell_status": shell_status,
        "rows": rows,
        "gaps": gaps,
        "summary": {
            "capability_count": len(capabilities),
            "gap_count": len(gaps),
        },
    }


def build_operator_scenarios() -> list[dict[str, Any]]:
    return [
        {
            "id": "SCN-agenthive-crud",
            "title": "AgentHive operator CRUD flow",
            "goal": "An operator can inspect list/detail/create/update expectations for AgentHive through the same product surfaces.",
        },
        {
            "id": "SCN-shell-overview",
            "title": "Shell overview across CLI/TUI/GUI",
            "goal": "An operator can see the same product summary from every shell.",
        },
        {
            "id": "SCN-history-drilldown",
            "title": "Program/history drilldown",
            "goal": "An operator can inspect plans, lessons, findings, and decisions from any shell.",
        },
        {
            "id": "SCN-orbit-health-check",
            "title": "ORBIT health and snapshot check",
            "goal": "An operator can inspect ORBIT state and sync health from any shell.",
        },
    ]
