from __future__ import annotations

from fastapi import FastAPI
from fastapi.responses import HTMLResponse

from constella_platform.gui import render_shell_response
from constella_platform.models import DecisionCreate, FindingCreate, LessonCreate, PlanCreate
from constella_platform.service import CapabilityService


service = CapabilityService()
app = FastAPI(title="Constella Platform API", version="0.1.0")


@app.get("/", response_class=HTMLResponse, include_in_schema=False)
@app.get("/gui", response_class=HTMLResponse, include_in_schema=False)
def gui_shell() -> HTMLResponse:
    return render_shell_response(service)


@app.get("/capabilities")
def list_capabilities() -> dict:
    return service.invoke("capabilities.list")


@app.get("/shell/parity")
def shell_parity() -> dict:
    return service.invoke("shell.parity.report")


@app.get("/workflow/packs")
def workflow_packs() -> dict:
    return service.invoke("workflow.pack.list")


@app.get("/distribution/release")
def distribution_release_prep() -> dict:
    return service.invoke("distribution.release.prep")


@app.get("/operator/detail-views")
def operator_detail_views() -> dict:
    return service.invoke("operator.detail.views")


@app.get("/runtime/dashboard")
def runtime_dashboard_summary() -> dict:
    return service.invoke("runtime.dashboard.summary")


@app.get("/governance/review-meeting")
def review_meeting_surface() -> dict:
    return service.invoke("review.meeting.surface")


@app.get("/governance/findings/{title}/task")
def governance_finding_to_task(title: str) -> dict:
    return service.invoke("governance.finding.to_task", {"title": title})


@app.get("/governance/lessons/{title}/guardrail")
def governance_lesson_to_guardrail(title: str) -> dict:
    return service.invoke("governance.lesson.to_guardrail", {"title": title})


@app.get("/program/plans")
def list_plans() -> dict:
    return service.invoke("program.plan.list")


@app.post("/program/plans")
def create_plan(payload: PlanCreate) -> dict:
    return service.invoke("program.plan.create", payload.model_dump())


@app.get("/history/lessons")
def list_lessons() -> dict:
    return service.invoke("history.lesson.list")


@app.post("/history/lessons")
def create_lesson(payload: LessonCreate) -> dict:
    return service.invoke("history.lesson.create", payload.model_dump())


@app.get("/review/findings")
def list_findings() -> dict:
    return service.invoke("review.finding.list")


@app.post("/review/findings")
def create_finding(payload: FindingCreate) -> dict:
    return service.invoke("review.finding.create", payload.model_dump())


@app.get("/decisions")
def list_decisions() -> dict:
    return service.invoke("decision.list")


@app.post("/decisions")
def create_decision(payload: DecisionCreate) -> dict:
    return service.invoke("decision.create", payload.model_dump())


@app.get("/aria/runtimes")
def list_runtimes() -> dict:
    return service.invoke("aria.runtime.list")


@app.get("/aria/nyx")
def list_nyx() -> dict:
    return service.invoke("aria.nyx.list")


@app.post("/aria/runtimes/update")
def aria_runtime_update(payload: dict) -> dict:
    return service.invoke("aria.runtime.config.update", payload)


@app.post("/aria/runtimes/{runtime_id}/enablement")
def aria_runtime_enablement_update(runtime_id: str, payload: dict) -> dict:
    return service.invoke("aria.runtime.enablement.update", {**payload, "runtime_id": runtime_id})


@app.post("/aria/agents/{agent_id}/surface/update")
def aria_agent_surface_update(agent_id: str, payload: dict) -> dict:
    return service.invoke("aria.agent.surface.update", {**payload, "agent_id": agent_id})


@app.get("/agenthive/projects")
def list_agenthive_projects() -> dict:
    return service.invoke("agenthive.project.list")


@app.get("/agenthive/backlog/{project}")
def agenthive_backlog_summary(project: str) -> dict:
    return service.invoke("agenthive.backlog.summary", {"project": project})


@app.post("/agenthive/projects/upsert")
def agenthive_project_upsert(payload: dict) -> dict:
    return service.invoke("agenthive.project.upsert", payload)


@app.post("/agenthive/tasks/upsert")
def agenthive_task_upsert(payload: dict) -> dict:
    return service.invoke("agenthive.task.upsert", payload)


@app.get("/orbit/snapshot")
def orbit_snapshot() -> dict:
    return service.invoke("orbit.snapshot")


@app.post("/orbit/schedules/update")
def orbit_schedule_update(payload: dict) -> dict:
    return service.invoke("orbit.schedule.update", payload)


@app.post("/orbit/tasks/update")
def orbit_task_update(payload: dict) -> dict:
    return service.invoke("orbit.task.update", payload)
