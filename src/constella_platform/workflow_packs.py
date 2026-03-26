from __future__ import annotations


def list_operator_packs() -> dict:
    packs = [
        {
            "id": "operator-shell-pack",
            "title": "Operator Shell Pack",
            "description": "Shared shell views and parity scaffolding for CLI/TUI/GUI/API.",
        },
        {
            "id": "runtime-family-pack",
            "title": "Runtime Family Pack",
            "description": "Operator-oriented runtime status and control pack.",
        },
        {
            "id": "review-meeting-pack",
            "title": "Review Meeting Pack",
            "description": "Structured review/orchestration surface for governance workflows.",
        },
    ]
    return {
        "packs": packs,
        "summary": {
            "count": len(packs),
        },
    }
