from __future__ import annotations


def build_detail_views() -> dict:
    views = [
        {
            "id": "agenthive-project-detail",
            "title": "AgentHive project detail",
            "description": "Project metadata, backlog state, and linked CRUD actions.",
        },
        {
            "id": "runtime-control-detail",
            "title": "Runtime control detail",
            "description": "Runtime status, enablement controls, and pack-linked actions.",
        },
        {
            "id": "governance-history-detail",
            "title": "Governance history detail",
            "description": "Decisions, findings, lessons, and follow-up traces.",
        },
    ]
    return {"views": views, "summary": {"count": len(views)}}
