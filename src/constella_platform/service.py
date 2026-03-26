from __future__ import annotations

from typing import Any

from constella_platform.capability_registry import all_capabilities
from constella_platform.domains import agenthive, aria_runtime, orbit, program_history
from constella_platform.models import DecisionCreate, FindingCreate, LessonCreate, PlanCreate
from constella_platform.parity import build_operator_scenarios, build_shell_parity_report
from constella_platform.workflow_packs import list_operator_packs
from constella_platform import store


class CapabilityService:
    def __init__(self) -> None:
        store.ensure_dirs()

    def invoke(self, capability_id: str, payload: dict[str, Any] | None = None) -> dict[str, Any]:
        payload = payload or {}

        if capability_id == "capabilities.list":
            data = all_capabilities()
        elif capability_id == "program.plan.create":
            data = program_history.create_plan(PlanCreate(**payload))
        elif capability_id == "program.plan.list":
            data = program_history.list_plans()
        elif capability_id == "history.lesson.create":
            data = program_history.create_lesson(LessonCreate(**payload))
        elif capability_id == "history.lesson.list":
            data = program_history.list_lessons()
        elif capability_id == "review.finding.create":
            data = program_history.create_finding(FindingCreate(**payload))
        elif capability_id == "review.finding.list":
            data = program_history.list_findings()
        elif capability_id == "decision.create":
            data = program_history.create_decision(DecisionCreate(**payload))
        elif capability_id == "decision.list":
            data = program_history.list_decisions()
        elif capability_id == "aria.runtime.list":
            data = aria_runtime.list_runtimes()
        elif capability_id == "aria.nyx.list":
            data = aria_runtime.list_nyx_agents()
        elif capability_id == "agenthive.project.list":
            data = agenthive.list_projects()
        elif capability_id == "agenthive.backlog.summary":
            data = agenthive.backlog_summary(payload["project"])
        elif capability_id == "orbit.snapshot":
            data = orbit.read_snapshot()
        elif capability_id == "agenthive.project.upsert":
            data = (
                agenthive.upsert_project(payload["project"])
                if payload.get("execute")
                else agenthive.preview_project_upsert(payload["project"])
            )
        elif capability_id == "agenthive.task.upsert":
            data = (
                agenthive.upsert_task(payload["project"], payload["task"])
                if payload.get("execute")
                else agenthive.preview_task_upsert(payload["project"], payload["task"])
            )
        elif capability_id == "orbit.schedule.update":
            data = (
                orbit.apply_schedule_mutation(payload["path"], payload["updates"], execute=True)
                if payload.get("execute")
                else orbit.preview_schedule_mutation(payload["path"], payload["updates"])
            )
        elif capability_id == "orbit.task.update":
            data = (
                orbit.apply_task_mutation(payload["path"], payload["updates"], execute=True)
                if payload.get("execute")
                else orbit.preview_task_mutation(payload["path"], payload["updates"])
            )
        elif capability_id == "aria.runtime.config.update":
            data = (
                aria_runtime.apply_runtime_config_update(payload["patch"])
                if payload.get("execute")
                else aria_runtime.preview_runtime_config_update(payload["patch"])
            )
        elif capability_id == "aria.runtime.enablement.update":
            data = (
                aria_runtime.apply_runtime_enablement_update(payload["runtime_id"], enabled=payload["enabled"])
                if payload.get("execute")
                else aria_runtime.preview_runtime_enablement_update(payload["runtime_id"], enabled=payload["enabled"])
            )
        elif capability_id == "aria.agent.surface.update":
            kwargs = {
                "config_patch": payload.get("config_patch"),
                "harness_patch": payload.get("harness_patch"),
            }
            data = (
                aria_runtime.apply_agent_surface_update(payload["agent_id"], **kwargs)
                if payload.get("execute")
                else aria_runtime.preview_agent_surface_update(payload["agent_id"], **kwargs)
            )
        elif capability_id == "shell.parity.report":
            capabilities = all_capabilities()
            data = {
                "parity": build_shell_parity_report(
                    capabilities=capabilities,
                    shell_status={"cli": True, "api": True, "tui": True, "gui": True},
                ),
                "operator_scenarios": build_operator_scenarios(),
            }
        elif capability_id == "workflow.pack.list":
            data = list_operator_packs()
        elif capability_id == "runtime.dashboard.summary":
            runtimes = aria_runtime.list_runtimes()
            data = {
                "runtime_count": len(runtimes),
                "enabled_count": sum(1 for item in runtimes if item.get("enabled")),
                "types": sorted({str(item.get("type", "unknown")) for item in runtimes}),
                "runtimes": runtimes,
            }
        elif capability_id == "review.meeting.surface":
            data = program_history.review_meeting_surface()
        elif capability_id == "governance.finding.to_task":
            data = program_history.finding_to_task(payload["title"])
        elif capability_id == "governance.lesson.to_guardrail":
            data = program_history.lesson_to_guardrail(payload["title"])
        else:
            raise KeyError(f"unknown capability: {capability_id}")

        store.append_audit(
            {
                "ts": store.timestamp(),
                "capability_id": capability_id,
                "payload": payload,
            }
        )
        return {"capability_id": capability_id, "data": data}
