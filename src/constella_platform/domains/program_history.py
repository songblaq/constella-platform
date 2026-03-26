from __future__ import annotations

from constella_platform.models import DecisionCreate, FindingCreate, LessonCreate, PlanCreate
from constella_platform import store


def create_plan(payload: PlanCreate) -> dict:
    entry = {
        "ts": store.timestamp(),
        "title": payload.title,
        "summary": payload.summary,
    }
    store.append_plan(entry)
    return entry


def list_plans() -> list[dict]:
    return store.list_plans()


def create_lesson(payload: LessonCreate) -> dict:
    entry = {
        "ts": store.timestamp(),
        "title": payload.title,
        "why_failed": payload.why_failed,
        "what_was_missed": payload.what_was_missed,
        "next_guardrail": payload.next_guardrail,
    }
    store.append_lesson(entry)
    return entry


def list_lessons() -> list[dict]:
    return store.list_lessons()


def create_finding(payload: FindingCreate) -> dict:
    entry = {
        "ts": store.timestamp(),
        "title": payload.title,
        "severity": payload.severity,
        "detail": payload.detail,
    }
    store.append_finding(entry)
    return entry


def list_findings() -> list[dict]:
    return store.list_findings()


def create_decision(payload: DecisionCreate) -> dict:
    entry = {
        "ts": store.timestamp(),
        "title": payload.title,
        "rationale": payload.rationale,
        "disposition": payload.disposition,
    }
    store.append_decision(entry)
    return entry


def list_decisions() -> list[dict]:
    return store.list_decisions()


def finding_to_task(title: str) -> dict:
    findings = list_findings()
    match = next((item for item in findings if item.get("title") == title), None)
    if match is None:
        raise KeyError(f"unknown finding: {title}")
    return {
        "source_title": match["title"],
        "severity": match["severity"],
        "task_title": f"Follow-up: {match['title']}",
        "task_summary": match["detail"],
    }


def lesson_to_guardrail(title: str) -> dict:
    lessons = list_lessons()
    match = next((item for item in lessons if item.get("title") == title), None)
    if match is None:
        raise KeyError(f"unknown lesson: {title}")
    return {
        "source_title": match["title"],
        "guardrail_title": f"Guardrail: {match['title']}",
        "guardrail_summary": match["next_guardrail"],
    }
