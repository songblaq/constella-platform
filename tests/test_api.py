import os

from fastapi.testclient import TestClient

from constella_platform.api import app


def test_api_plan_and_decision_routes(tmp_path, monkeypatch):
    monkeypatch.setenv("CONSTELLAR_HOME", str(tmp_path / ".constellar"))
    client = TestClient(app)

    response = client.post("/program/plans", json={"title": "v1", "summary": "core"})
    assert response.status_code == 200
    assert response.json()["data"]["title"] == "v1"

    response = client.post("/decisions", json={"title": "core-first", "rationale": "shared capability model", "disposition": "accepted"})
    assert response.status_code == 200

    response = client.get("/decisions")
    assert response.status_code == 200
    assert response.json()["data"][0]["title"] == "core-first"


def test_api_aria_runtime_and_nyx_routes(tmp_path, monkeypatch):
    aria_home = tmp_path / ".aria"
    agents_dir = aria_home / "agents"
    agents_dir.mkdir(parents=True)
    (aria_home / "config.json").write_text(
        '{"runtimes":{"openclaw":{"enabled":true,"type":"gateway"},"claude-code":{"enabled":true,"type":"cli"}}}',
        encoding="utf-8",
    )
    for name in ["browser", "infra"]:
        agent_dir = agents_dir / name
        agent_dir.mkdir()
        (agent_dir / "config.json").write_text(f'{{"id":"{name}"}}', encoding="utf-8")

    monkeypatch.setenv("CONSTELLAR_HOME", str(tmp_path / ".constellar"))
    monkeypatch.setenv("CONSTELLA_ARIA_HOME", str(aria_home))
    client = TestClient(app)

    response = client.get("/aria/runtimes")
    assert response.status_code == 200
    assert response.json()["data"][0]["id"] == "claude-code"

    response = client.get("/aria/nyx")
    assert response.status_code == 200
    assert response.json()["data"][0]["id"] == "browser"


def test_api_aria_runtime_enablement_route(tmp_path, monkeypatch):
    aria_home = tmp_path / ".aria"
    aria_home.mkdir()
    (aria_home / "config.json").write_text(
        '{"runtimes":{"openclaw":{"enabled":true,"type":"gateway"},"claude-code":{"enabled":true,"type":"cli"}}}',
        encoding="utf-8",
    )

    monkeypatch.setenv("CONSTELLAR_HOME", str(tmp_path / ".constellar"))
    monkeypatch.setenv("CONSTELLA_ARIA_HOME", str(aria_home))
    client = TestClient(app)

    response = client.post("/aria/runtimes/openclaw/enablement", json={"enabled": False})
    assert response.status_code == 200
    assert response.json()["data"]["runtime_id"] == "openclaw"
