import json

from constella_platform.service import CapabilityService


def test_release_prep_and_drilldown_surfaces_are_exposed(tmp_path, monkeypatch):
    monkeypatch.setenv("CONSTELLAR_HOME", str(tmp_path / ".constellar"))
    service = CapabilityService()

    release = service.invoke("distribution.release.prep")
    drilldown = service.invoke("operator.detail.views")

    assert release["capability_id"] == "distribution.release.prep"
    assert release["data"]["package_name"] == "constella-platform"
    assert "install_bundle" in release["data"]["artifacts"]

    assert drilldown["capability_id"] == "operator.detail.views"
    assert any(item["id"] == "agenthive-project-detail" for item in drilldown["data"]["views"])
    assert any(item["id"] == "runtime-control-detail" for item in drilldown["data"]["views"])
