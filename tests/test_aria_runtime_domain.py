import json

from constella_platform.domains import aria_runtime
from constella_platform.service import CapabilityService


def test_aria_runtime_and_nyx_capabilities_read_from_custom_home(tmp_path, monkeypatch):
    aria_home = tmp_path / ".aria"
    agents_dir = aria_home / "agents"
    agents_dir.mkdir(parents=True)

    (aria_home / "config.json").write_text(
        json.dumps(
            {
                "runtimes": {
                    "openclaw": {"enabled": True, "type": "gateway"},
                    "codex": {"enabled": True, "type": "cli"},
                    "cursor": {"enabled": False, "type": "ide"},
                }
            }
        ),
        encoding="utf-8",
    )
    for name in ["infra", "browser", "openclaw"]:
        agent_dir = agents_dir / name
        agent_dir.mkdir()
        (agent_dir / "config.json").write_text(json.dumps({"id": name}), encoding="utf-8")

    monkeypatch.setenv("CONSTELLAR_HOME", str(tmp_path / ".constellar"))
    monkeypatch.setenv("CONSTELLA_ARIA_HOME", str(aria_home))

    service = CapabilityService()

    runtimes = service.invoke("aria.runtime.list")["data"]
    nyx_agents = service.invoke("aria.nyx.list")["data"]

    assert [item["id"] for item in runtimes] == ["codex", "cursor", "openclaw"]
    assert runtimes[0]["type"] == "cli"
    assert [item["id"] for item in nyx_agents] == ["browser", "infra", "openclaw"]


def test_runtime_editor_preview_and_apply_are_merge_only(tmp_path, monkeypatch):
    aria_home = tmp_path / ".aria"
    aria_home.mkdir()
    config_path = aria_home / "config.json"
    config_path.write_text(
        json.dumps(
            {
                "metadata": {"owner": "ops"},
                "runtimes": {
                    "openclaw": {"enabled": True, "type": "gateway"},
                    "codex": {"enabled": True, "type": "cli"},
                },
            }
        ),
        encoding="utf-8",
    )

    monkeypatch.setenv("CONSTELLA_ARIA_HOME", str(aria_home))

    preview = aria_runtime.preview_runtime_config_update(
        {
            "runtimes": {
                "codex": {"enabled": False},
                "cursor": {"enabled": True, "type": "ide"},
            }
        }
    )

    assert preview["before"]["runtimes"]["codex"]["enabled"] is True
    assert preview["after"]["runtimes"]["codex"]["enabled"] is False
    assert preview["after"]["runtimes"]["cursor"]["type"] == "ide"
    assert preview["after"]["metadata"]["owner"] == "ops"
    assert json.loads(config_path.read_text(encoding="utf-8"))["runtimes"]["codex"]["enabled"] is True

    result = aria_runtime.apply_runtime_config_update(
        {
            "runtimes": {
                "codex": {"enabled": False},
                "cursor": {"enabled": True, "type": "ide"},
            }
        }
    )

    assert result["after"]["runtimes"]["codex"]["enabled"] is False
    assert json.loads(config_path.read_text(encoding="utf-8"))["runtimes"]["cursor"]["enabled"] is True
    assert json.loads(config_path.read_text(encoding="utf-8"))["metadata"]["owner"] == "ops"


def test_runtime_enablement_preview_and_apply_target_a_single_runtime(tmp_path, monkeypatch):
    aria_home = tmp_path / ".aria"
    aria_home.mkdir()
    config_path = aria_home / "config.json"
    config_path.write_text(
        json.dumps(
            {
                "metadata": {"owner": "ops"},
                "runtimes": {
                    "openclaw": {"enabled": True, "type": "gateway"},
                    "codex": {"enabled": True, "type": "cli"},
                },
            }
        ),
        encoding="utf-8",
    )

    monkeypatch.setenv("CONSTELLA_ARIA_HOME", str(aria_home))

    preview = aria_runtime.preview_runtime_enablement_update("codex", enabled=False)

    assert preview["runtime_id"] == "codex"
    assert preview["before"]["runtimes"]["codex"]["enabled"] is True
    assert preview["after"]["runtimes"]["codex"]["enabled"] is False
    assert preview["after"]["runtimes"]["codex"]["type"] == "cli"
    assert preview["after"]["runtimes"]["openclaw"]["enabled"] is True
    assert json.loads(config_path.read_text(encoding="utf-8"))["runtimes"]["codex"]["enabled"] is True

    result = aria_runtime.apply_runtime_enablement_update("codex", enabled=False)

    assert result["runtime_id"] == "codex"
    assert result["after"]["runtimes"]["codex"]["enabled"] is False
    assert json.loads(config_path.read_text(encoding="utf-8"))["runtimes"]["codex"]["enabled"] is False


def test_agent_surface_editor_preview_and_apply_targets_config_and_harness_files(tmp_path, monkeypatch):
    aria_home = tmp_path / ".aria"
    agent_dir = aria_home / "agents" / "browser"
    harness_dir = agent_dir / "harness"
    harness_dir.mkdir(parents=True)
    (agent_dir / "config.json").write_text(
        json.dumps({"id": "browser", "type": "harness", "enabled": True, "model": "old"}),
        encoding="utf-8",
    )
    (harness_dir / "README.md").write_text("old harness notes\n", encoding="utf-8")

    monkeypatch.setenv("CONSTELLA_ARIA_HOME", str(aria_home))

    preview = aria_runtime.preview_agent_surface_update(
        "browser",
        config_patch={"model": "new", "routing": {"mode": "direct"}},
        harness_patch={"README.md": "# Browser\nupdated"},
    )

    assert preview["before"]["config"]["model"] == "old"
    assert preview["after"]["config"]["model"] == "new"
    assert preview["after"]["config"]["routing"]["mode"] == "direct"
    assert preview["writes"][1]["path"].endswith("harness/README.md")
    assert (harness_dir / "README.md").read_text(encoding="utf-8") == "old harness notes\n"

    result = aria_runtime.apply_agent_surface_update(
        "browser",
        config_patch={"model": "new", "routing": {"mode": "direct"}},
        harness_patch={"README.md": "# Browser\nupdated"},
    )

    assert result["after"]["config"]["model"] == "new"
    assert json.loads((agent_dir / "config.json").read_text(encoding="utf-8"))["routing"]["mode"] == "direct"
    assert (harness_dir / "README.md").read_text(encoding="utf-8") == "# Browser\nupdated"
