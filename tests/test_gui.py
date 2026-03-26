from fastapi.testclient import TestClient

from constella_platform.api import app
from constella_platform.gui import build_shell_state, render_shell_response
from constella_platform.service import CapabilityService


def test_shell_state_reuses_shared_service_and_summaries(tmp_path, monkeypatch):
    constellar_home = tmp_path / ".constellar"
    aria_home = tmp_path / ".aria"
    orbit_home = aria_home / "orbit"
    constellar_home.mkdir()
    aria_home.mkdir()
    orbit_home.mkdir()
    (orbit_home / "orbit-status.json").write_text('{"mode": "active", "tick_count_24h": 7}', encoding="utf-8")

    monkeypatch.setenv("CONSTELLAR_HOME", str(constellar_home))
    monkeypatch.setenv("CONSTELLA_ARIA_HOME", str(aria_home))

    service = CapabilityService()
    service.invoke("program.plan.create", {"title": "foundation", "summary": "shared shell"})
    service.invoke(
        "history.lesson.create",
        {
            "title": "Hide logic behind the same core",
            "why_failed": "shell drift",
            "what_was_missed": "shared service reuse",
            "next_guardrail": "render from the capability service",
        },
    )

    state = build_shell_state(service)

    assert state["capability_summary"]["total"] >= 1
    assert state["history_summary"]["plans"] == 1
    assert state["history_summary"]["lessons"] == 1
    assert state["health_summary"]["status"] == "healthy"
    assert any(check["name"] == "Orbit snapshot" for check in state["health_summary"]["checks"])
    assert state["health_summary"]["checks"][0]["name"] == "Capability registry"


def test_api_root_renders_shell_html(tmp_path, monkeypatch):
    constellar_home = tmp_path / ".constellar"
    aria_home = tmp_path / ".aria"
    orbit_home = aria_home / "orbit"
    constellar_home.mkdir()
    aria_home.mkdir()
    orbit_home.mkdir()
    (orbit_home / "orbit-status.json").write_text('{"mode": "active", "tick_count_24h": 3}', encoding="utf-8")

    monkeypatch.setenv("CONSTELLAR_HOME", str(constellar_home))
    monkeypatch.setenv("CONSTELLA_ARIA_HOME", str(aria_home))

    client = TestClient(app)
    response = client.get("/")

    assert response.status_code == 200
    assert response.headers["content-type"].startswith("text/html")
    assert "Constella Platform" in response.text
    assert "Capability summary" in response.text
    assert "History summary" in response.text
    assert "Health summary" in response.text


def test_shell_response_wrapper_returns_html_response(tmp_path, monkeypatch):
    constellar_home = tmp_path / ".constellar"
    aria_home = tmp_path / ".aria"
    orbit_home = aria_home / "orbit"
    constellar_home.mkdir()
    aria_home.mkdir()
    orbit_home.mkdir()
    (orbit_home / "orbit-status.json").write_text('{"mode": "active"}', encoding="utf-8")

    monkeypatch.setenv("CONSTELLAR_HOME", str(constellar_home))
    monkeypatch.setenv("CONSTELLA_ARIA_HOME", str(aria_home))

    service = CapabilityService()
    response = render_shell_response(service)

    assert response.media_type == "text/html"
    assert "Shared core shell" in response.body.decode("utf-8")
