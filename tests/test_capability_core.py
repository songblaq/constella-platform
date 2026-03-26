from constella_platform.service import CapabilityService


def test_capability_list_contains_program_domain(tmp_path, monkeypatch):
    monkeypatch.setenv("CONSTELLAR_HOME", str(tmp_path / ".constellar"))
    service = CapabilityService()

    result = service.invoke("capabilities.list")
    capability_ids = {item["capability_id"] for item in result["data"]}
    assert "program.plan.create" in capability_ids
    assert "history.lesson.create" in capability_ids


def test_program_and_history_entries_are_persisted_and_audited(tmp_path, monkeypatch):
    monkeypatch.setenv("CONSTELLAR_HOME", str(tmp_path / ".constellar"))
    service = CapabilityService()

    service.invoke("program.plan.create", {"title": "Constella V1", "summary": "foundation"})
    service.invoke(
        "history.lesson.create",
        {
            "title": "Missing migration lane",
            "why_failed": "Plan ignored cutover details",
            "what_was_missed": "exact repo/appdata ownership",
            "next_guardrail": "always include migration rail",
        },
    )

    plans = service.invoke("program.plan.list")["data"]
    lessons = service.invoke("history.lesson.list")["data"]
    assert plans[0]["title"] == "Constella V1"
    assert lessons[0]["title"] == "Missing migration lane"

    audit = service.invoke("decision.list")  # create one more audit event through a read capability
    assert audit["capability_id"] == "decision.list"
