from constella_platform.service import CapabilityService


def test_workflow_operator_pack_foundation_is_exposed(tmp_path, monkeypatch):
    monkeypatch.setenv("CONSTELLAR_HOME", str(tmp_path / ".constellar"))
    service = CapabilityService()

    result = service.invoke("workflow.pack.list")

    assert result["capability_id"] == "workflow.pack.list"
    pack_ids = [item["id"] for item in result["data"]["packs"]]
    assert "operator-shell-pack" in pack_ids
    assert "runtime-family-pack" in pack_ids
    assert "review-meeting-pack" in pack_ids


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


def test_runtime_dashboard_and_review_meeting_surface_are_operator_visible(tmp_path, monkeypatch):
    monkeypatch.setenv("CONSTELLAR_HOME", str(tmp_path / ".constellar"))
    aria_home = tmp_path / ".aria"
    aria_home.mkdir()
    (aria_home / "config.json").write_text(
        '{"runtimes":{"openclaw":{"enabled":true,"type":"gateway"},"codex":{"enabled":true,"type":"cli"}}}',
        encoding="utf-8",
    )
    monkeypatch.setenv("CONSTELLA_ARIA_HOME", str(aria_home))

    service = CapabilityService()
    service.invoke("review.finding.create", {"title": "Need drilldown", "severity": "medium", "detail": "detail view missing"})
    service.invoke("decision.create", {"title": "Use shared core", "rationale": "parity", "disposition": "accepted"})

    runtime_result = service.invoke("runtime.dashboard.summary")
    review_result = service.invoke("review.meeting.surface")

    assert runtime_result["data"]["runtime_count"] == 2
    assert review_result["data"]["summary"]["findings"] == 1
    assert review_result["data"]["summary"]["decisions"] == 1
    assert any(flow["id"] == "review-meeting-core" for flow in review_result["data"]["flows"])
