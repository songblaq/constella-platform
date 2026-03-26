from __future__ import annotations

from collections import Counter
from html import escape
from typing import Any

from fastapi.responses import HTMLResponse

from constella_platform import store


def _safe_invoke(service: Any, capability_id: str, payload: dict[str, Any] | None = None) -> dict[str, Any]:
    try:
        result = service.invoke(capability_id, payload)
    except Exception as exc:  # pragma: no cover - shell fallback path
        return {"ok": False, "error": str(exc)}
    return {"ok": True, "result": result}


def _count_by(items: list[dict[str, Any]], field: str) -> list[dict[str, Any]]:
    counts = Counter(str(item.get(field, "unknown")) for item in items)
    return [{"label": label, "count": counts[label]} for label in sorted(counts)]


def _latest_timestamp(items: list[dict[str, Any]]) -> str | None:
    timestamps = [str(item.get("ts", "")).strip() for item in items if str(item.get("ts", "")).strip()]
    return max(timestamps) if timestamps else None


def _orbit_summary(payload: dict[str, Any]) -> str:
    if not payload["ok"]:
        return payload["error"]

    data = payload["result"]["data"]
    status = data.get("status", {})
    sync = data.get("sync", {})

    bits = [str(status.get("mode", "unknown"))]
    if status.get("tick_count_24h") is not None:
        bits.append(f"{status['tick_count_24h']} ticks/24h")
    if sync.get("available"):
        bits.append(str(sync.get("summary", "sync available")))
    return " | ".join(bits)


def build_shell_state(service: Any) -> dict[str, Any]:
    capability_payload = _safe_invoke(service, "capabilities.list")
    capability_items = capability_payload["result"]["data"] if capability_payload["ok"] else []

    history_queries = (
        ("plans", "program.plan.list"),
        ("lessons", "history.lesson.list"),
        ("findings", "review.finding.list"),
        ("decisions", "decision.list"),
    )
    history_data: dict[str, list[dict[str, Any]]] = {}
    for label, capability_id in history_queries:
        payload = _safe_invoke(service, capability_id)
        history_data[label] = payload["result"]["data"] if payload["ok"] else []

    orbit_payload = _safe_invoke(service, "orbit.snapshot")

    capability_summary = {
        "total": len(capability_items),
        "domains": _count_by(capability_items, "domain"),
        "surfaces": _count_by(
            [{"surface": surface} for item in capability_items for surface in item.get("surfaces", [])],
            "surface",
        ),
        "effects": _count_by(
            [{"effect": effect} for item in capability_items for effect in item.get("effects", [])],
            "effect",
        ),
        "dangerous": sum(1 for item in capability_items if item.get("dangerous")),
        "audit_required": sum(1 for item in capability_items if item.get("audit_required", True)),
    }

    history_summary = {
        "plans": len(history_data["plans"]),
        "lessons": len(history_data["lessons"]),
        "findings": len(history_data["findings"]),
        "decisions": len(history_data["decisions"]),
        "latest_event": _latest_timestamp([item for values in history_data.values() for item in values]),
    }

    health_checks = [
        {
            "name": "Capability registry",
            "status": "healthy" if capability_payload["ok"] else "degraded",
            "summary": f"{len(capability_items)} capabilities available"
            if capability_payload["ok"]
            else capability_payload["error"],
        },
        {
            "name": "Program history",
            "status": "healthy",
            "summary": (
                f"{history_summary['plans']} plans, {history_summary['lessons']} lessons, "
                f"{history_summary['findings']} findings, {history_summary['decisions']} decisions"
            ),
        },
        {
            "name": "Orbit snapshot",
            "status": "healthy" if orbit_payload["ok"] else "degraded",
            "summary": _orbit_summary(orbit_payload),
        },
    ]

    return {
        "generated_at": store.timestamp(),
        "capabilities": capability_items,
        "capability_summary": capability_summary,
        "history_summary": history_summary,
        "health_summary": {
            "status": "healthy" if all(check["status"] == "healthy" for check in health_checks) else "degraded",
            "checks": health_checks,
        },
    }


def _render_stat(label: str, value: Any) -> str:
    return f"""
      <article class=\"stat-card\">
        <span class=\"stat-label\">{escape(label)}</span>
        <strong class=\"stat-value\">{escape(str(value))}</strong>
      </article>
    """


def _render_count_list(items: list[dict[str, Any]]) -> str:
    if not items:
        return "<p class=\"muted\">No items yet.</p>"
    rows = "".join(
        f"<li><span>{escape(str(item['label']))}</span><strong>{escape(str(item['count']))}</strong></li>"
        for item in items
    )
    return f"<ul class=\"count-list\">{rows}</ul>"


def render_shell_html(state: dict[str, Any]) -> str:
    capability_summary = state["capability_summary"]
    history_summary = state["history_summary"]
    health_summary = state["health_summary"]
    capabilities = state["capabilities"]

    capability_rows = "".join(
        """
        <tr>
          <td>{capability_id}</td>
          <td>{domain}</td>
          <td>{description}</td>
          <td>{surfaces}</td>
        </tr>
        """.format(
            capability_id=escape(str(item["capability_id"])),
            domain=escape(str(item["domain"])),
            description=escape(str(item["description"])),
            surfaces=escape(", ".join(str(surface) for surface in item.get("surfaces", []))),
        )
        for item in capabilities
    )

    health_rows = "".join(
        """
        <li class="health-row">
          <div>
            <strong>{name}</strong>
            <p>{summary}</p>
          </div>
          <span class="health-pill health-{status}">{status}</span>
        </li>
        """.format(
            name=escape(str(check["name"])),
            summary=escape(str(check["summary"])),
            status=escape(str(check["status"])),
        )
        for check in health_summary["checks"]
    )

    latest_event = history_summary["latest_event"] or "none"
    generated_at = state["generated_at"]

    return f"""<!doctype html>
<html lang="en">
  <head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <title>Constella Platform</title>
    <style>
      :root {{
        color-scheme: light;
        --bg: #f5f1e8;
        --panel: #fffaf2;
        --panel-alt: #f2ebe0;
        --text: #1d1a16;
        --muted: #6f6558;
        --line: #d8ccbb;
        --accent: #2f5d50;
        --accent-soft: #d7eadf;
        --warning: #a96d1d;
        --danger: #9a3d36;
        --shadow: 0 18px 50px rgba(42, 33, 19, 0.12);
        font-family: "Iowan Old Style", "Palatino Linotype", Palatino, serif;
      }}
      body {{
        margin: 0;
        background:
          radial-gradient(circle at top left, rgba(47, 93, 80, 0.11), transparent 28%),
          linear-gradient(180deg, #fbf7ef 0%, var(--bg) 100%);
        color: var(--text);
      }}
      .shell {{
        max-width: 1180px;
        margin: 0 auto;
        padding: 32px 20px 48px;
      }}
      .hero {{
        display: grid;
        gap: 18px;
        padding: 28px;
        border: 1px solid var(--line);
        border-radius: 28px;
        background: rgba(255, 250, 242, 0.92);
        box-shadow: var(--shadow);
      }}
      .eyebrow {{
        margin: 0;
        text-transform: uppercase;
        letter-spacing: 0.18em;
        color: var(--accent);
        font: 700 0.75rem/1.2 "SF Mono", "Menlo", monospace;
      }}
      h1 {{
        margin: 0;
        font-size: clamp(2.25rem, 5vw, 4.2rem);
        line-height: 0.96;
        max-width: 9ch;
      }}
      .lead {{
        margin: 0;
        max-width: 66ch;
        color: var(--muted);
        font-size: 1.02rem;
        line-height: 1.6;
      }}
      .meta {{
        display: flex;
        flex-wrap: wrap;
        gap: 10px;
        color: var(--muted);
        font: 600 0.88rem/1.2 "SF Mono", "Menlo", monospace;
      }}
      .meta span {{
        padding: 8px 12px;
        border-radius: 999px;
        background: var(--panel-alt);
        border: 1px solid var(--line);
      }}
      .grid {{
        display: grid;
        gap: 18px;
        grid-template-columns: repeat(12, minmax(0, 1fr));
        margin-top: 20px;
      }}
      .card {{
        padding: 20px;
        border: 1px solid var(--line);
        border-radius: 22px;
        background: rgba(255, 250, 242, 0.95);
        box-shadow: var(--shadow);
      }}
      .span-4 {{ grid-column: span 4; }}
      .span-12 {{ grid-column: span 12; }}
      h2 {{
        margin: 0 0 12px;
        font-size: 1.18rem;
      }}
      .stat-grid {{
        display: grid;
        gap: 12px;
        grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
      }}
      .stat-card {{
        padding: 16px;
        border-radius: 18px;
        background: white;
        border: 1px solid var(--line);
      }}
      .stat-label {{
        display: block;
        margin-bottom: 8px;
        color: var(--muted);
        font: 600 0.78rem/1.2 "SF Mono", "Menlo", monospace;
        text-transform: uppercase;
        letter-spacing: 0.12em;
      }}
      .stat-value {{
        display: block;
        font-size: 1.35rem;
        line-height: 1.1;
      }}
      .count-list, .health-list {{
        list-style: none;
        padding: 0;
        margin: 0;
      }}
      .count-list li, .health-row {{
        display: flex;
        align-items: flex-start;
        justify-content: space-between;
        gap: 18px;
        padding: 12px 0;
        border-top: 1px solid var(--line);
      }}
      .count-list li:first-child, .health-row:first-child {{
        border-top: 0;
        padding-top: 0;
      }}
      .muted {{
        color: var(--muted);
        margin: 0;
      }}
      table {{
        width: 100%;
        border-collapse: collapse;
      }}
      th, td {{
        text-align: left;
        vertical-align: top;
        padding: 10px 8px;
        border-top: 1px solid var(--line);
      }}
      th {{
        color: var(--muted);
        font: 600 0.8rem/1.2 "SF Mono", "Menlo", monospace;
        text-transform: uppercase;
        letter-spacing: 0.12em;
      }}
      .health-pill {{
        flex: 0 0 auto;
        padding: 6px 10px;
        border-radius: 999px;
        font: 700 0.75rem/1.2 "SF Mono", "Menlo", monospace;
        text-transform: uppercase;
        letter-spacing: 0.08em;
      }}
      .health-healthy {{
        color: #1d584b;
        background: var(--accent-soft);
      }}
      .health-degraded {{
        color: var(--warning);
        background: #f4ead6;
      }}
      .section-note {{
        margin: 0 0 14px;
        color: var(--muted);
      }}
      @media (max-width: 900px) {{
        .span-4, .span-12 {{
          grid-column: span 12;
        }}
      }}
    </style>
  </head>
  <body>
    <main class="shell">
      <header class="hero">
        <p class="eyebrow">Constella Platform</p>
        <h1>Shared core shell</h1>
        <p class="lead">
          Server-rendered shell over the same capability/service core used by the API.
          This view summarizes capability coverage, program history, and health signals
          without introducing a separate client-side application.
        </p>
        <div class="meta">
          <span>Generated {escape(str(generated_at))}</span>
          <span>Health {escape(str(health_summary["status"]))}</span>
          <span>Latest activity {escape(str(latest_event))}</span>
        </div>
      </header>

      <section class="grid">
        <article class="card span-4">
          <h2>Capability summary</h2>
          <div class="stat-grid">
            {_render_stat("Total", capability_summary["total"])}
            {_render_stat("Domains", len(capability_summary["domains"]))}
            {_render_stat("Surfaces", len(capability_summary["surfaces"]))}
            {_render_stat("Effects", len(capability_summary["effects"]))}
          </div>
          <div style="margin-top: 16px;">
            <p class="section-note">Domains</p>
            {_render_count_list(capability_summary["domains"])}
          </div>
        </article>

        <article class="card span-4">
          <h2>History summary</h2>
          <div class="stat-grid">
            {_render_stat("Plans", history_summary["plans"])}
            {_render_stat("Lessons", history_summary["lessons"])}
            {_render_stat("Findings", history_summary["findings"])}
            {_render_stat("Decisions", history_summary["decisions"])}
          </div>
          <p class="section-note" style="margin-top: 16px;">Latest event: {escape(str(latest_event))}</p>
          <p class="section-note">Audit-aware entries are served from the shared store behind the capability service.</p>
        </article>

        <article class="card span-4">
          <h2>Health summary</h2>
          <ul class="health-list">
            {health_rows}
          </ul>
        </article>

        <article class="card span-12">
          <h2>Capability registry</h2>
          <p class="section-note">This table is rendered from the same capability registry the API exposes.</p>
          <table>
            <thead>
              <tr>
                <th>Capability</th>
                <th>Domain</th>
                <th>Description</th>
                <th>Surfaces</th>
              </tr>
            </thead>
            <tbody>
              {capability_rows}
            </tbody>
          </table>
        </article>
      </section>
    </main>
  </body>
</html>
"""


def render_shell_response(service: Any) -> HTMLResponse:
    return HTMLResponse(render_shell_html(build_shell_state(service)))


def render_shell(
    *,
    capabilities_count: int | None = None,
    project_count: int | None = None,
    plan_count: int | None = None,
    lesson_count: int | None = None,
    orbit_mode: str | None = None,
    service: Any | None = None,
) -> str:
    """Compatibility wrapper for the older shell entrypoint.

    The API now uses the service-backed render path, but keeping this wrapper
    avoids breaking any ad-hoc imports while the shell foundation is rolling out.
    """

    if service is None:
        return f"""<!doctype html>
<html lang="en">
  <head><meta charset="utf-8"><title>Constella Platform</title></head>
  <body>
    <h1>Constella Platform</h1>
    <p>Shared core shell</p>
    <p>Capabilities: {capabilities_count if capabilities_count is not None else "n/a"}</p>
    <p>Projects: {project_count if project_count is not None else "n/a"}</p>
    <p>Plans: {plan_count if plan_count is not None else "n/a"}</p>
    <p>Lessons: {lesson_count if lesson_count is not None else "n/a"}</p>
    <p>ORBIT mode: {escape(str(orbit_mode if orbit_mode is not None else "n/a"))}</p>
  </body>
</html>"""

    return render_shell_html(build_shell_state(service))
