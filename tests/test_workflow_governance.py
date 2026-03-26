from constella_platform.service import CapabilityService


def test_workflow_operator_pack_foundation_is_exposed(tmp_path, monkeypatch):
    monkeypatch.setenv("CONSTELLAR_HOME", str(tmp_path / ".constellar"))
    service = CapabilityService()

    result = service.invoke("workflow.pack.list")

    assert result["capability_id"] == "workflow.pack.list"
    assert result["data"]["packs"][0]["id"] == "operator-shell-pack"


def test_governance_hooks_turn_findings_and_lessons_into_structured_suggestions(tmp_path, monkeypatch):
    monkeypatch.setenv("CONSTELLAR_HOME", str(tmp_path / ".constellar"))
    service = CapabilityService()

    service.invoke(
        "review.finding.create",
        {
            "title": "Missing detail view",
            "severity": "high",
            "detail": "Operator cannot drill down into project details.",
        },
    )
    service.invoke(
        "history.lesson.create",
        {
            "title": "Migration ownership missing",
            "why_failed": "plan too abstract",
            "what_was_missed": "exact appdata and project ownership",
            "next_guardrail": "always declare ownership",
        },
    )

    finding_result = service.invoke("governance.finding.to_task", {"title": "Missing detail view"})
    lesson_result = service.invoke("governance.lesson.to_guardrail", {"title": "Migration ownership missing"})

    assert finding_result["data"]["task_title"].startswith("Follow-up:")
    assert finding_result["data"]["source_title"] == "Missing detail view"
    assert lesson_result["data"]["guardrail_title"].startswith("Guardrail:")
    assert lesson_result["data"]["source_title"] == "Migration ownership missing"
