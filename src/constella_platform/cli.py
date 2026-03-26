from __future__ import annotations

import argparse
import json
import sys

from constella_platform.service import CapabilityService


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="constella-platform")
    sub = parser.add_subparsers(dest="command", required=True)

    caps = sub.add_parser("capabilities")
    caps_sub = caps.add_subparsers(dest="caps_command", required=True)
    caps_list = caps_sub.add_parser("list")
    caps_list.set_defaults(capability_id="capabilities.list")

    shell = sub.add_parser("shell")
    shell_sub = shell.add_subparsers(dest="shell_command", required=True)
    shell_parity = shell_sub.add_parser("parity")
    shell_parity_sub = shell_parity.add_subparsers(dest="shell_parity_command", required=True)
    shell_parity_report = shell_parity_sub.add_parser("report")
    shell_parity_report.set_defaults(capability_id="shell.parity.report")

    workflow = sub.add_parser("workflow")
    workflow_sub = workflow.add_subparsers(dest="workflow_command", required=True)
    workflow_pack = workflow_sub.add_parser("pack")
    workflow_pack_sub = workflow_pack.add_subparsers(dest="workflow_pack_command", required=True)
    workflow_pack_list = workflow_pack_sub.add_parser("list")
    workflow_pack_list.set_defaults(capability_id="workflow.pack.list")

    distribution = sub.add_parser("distribution")
    distribution_sub = distribution.add_subparsers(dest="distribution_command", required=True)
    distribution_release = distribution_sub.add_parser("release")
    distribution_release_sub = distribution_release.add_subparsers(dest="distribution_release_command", required=True)
    distribution_release_prep = distribution_release_sub.add_parser("prep")
    distribution_release_prep.set_defaults(capability_id="distribution.release.prep")

    governance = sub.add_parser("governance")
    governance_sub = governance.add_subparsers(dest="governance_command", required=True)
    finding = governance_sub.add_parser("finding")
    finding_sub = finding.add_subparsers(dest="governance_finding_command", required=True)
    finding_to_task = finding_sub.add_parser("to-task")
    finding_to_task.add_argument("--title", required=True)
    finding_to_task.set_defaults(capability_id="governance.finding.to_task")
    lesson = governance_sub.add_parser("lesson")
    lesson_sub = lesson.add_subparsers(dest="governance_lesson_command", required=True)
    lesson_to_guardrail = lesson_sub.add_parser("to-guardrail")
    lesson_to_guardrail.add_argument("--title", required=True)
    lesson_to_guardrail.set_defaults(capability_id="governance.lesson.to_guardrail")
    review_meeting = governance_sub.add_parser("review-meeting")
    review_meeting_sub = review_meeting.add_subparsers(dest="review_meeting_command", required=True)
    review_meeting_surface = review_meeting_sub.add_parser("surface")
    review_meeting_surface.set_defaults(capability_id="review.meeting.surface")

    operator = sub.add_parser("operator")
    operator_sub = operator.add_subparsers(dest="operator_command", required=True)
    detail = operator_sub.add_parser("detail")
    detail_sub = detail.add_subparsers(dest="detail_command", required=True)
    detail_views = detail_sub.add_parser("views")
    detail_views.set_defaults(capability_id="operator.detail.views")

    program = sub.add_parser("program")
    program_sub = program.add_subparsers(dest="program_command", required=True)
    program_plan = program_sub.add_parser("plan")
    plan_sub = program_plan.add_subparsers(dest="plan_command", required=True)
    plan_create = plan_sub.add_parser("create")
    plan_create.add_argument("--title", required=True)
    plan_create.add_argument("--summary", required=True)
    plan_create.set_defaults(capability_id="program.plan.create")
    plan_list = plan_sub.add_parser("list")
    plan_list.set_defaults(capability_id="program.plan.list")

    history = sub.add_parser("history")
    history_sub = history.add_subparsers(dest="history_command", required=True)
    lesson = history_sub.add_parser("lesson")
    lesson_sub = lesson.add_subparsers(dest="lesson_command", required=True)
    lesson_create = lesson_sub.add_parser("create")
    lesson_create.add_argument("--title", required=True)
    lesson_create.add_argument("--why-failed", required=True)
    lesson_create.add_argument("--what-was-missed", required=True)
    lesson_create.add_argument("--next-guardrail", required=True)
    lesson_create.set_defaults(capability_id="history.lesson.create")
    lesson_list = lesson_sub.add_parser("list")
    lesson_list.set_defaults(capability_id="history.lesson.list")

    review = sub.add_parser("review")
    review_sub = review.add_subparsers(dest="review_command", required=True)
    finding = review_sub.add_parser("finding")
    finding_sub = finding.add_subparsers(dest="finding_command", required=True)
    finding_create = finding_sub.add_parser("create")
    finding_create.add_argument("--title", required=True)
    finding_create.add_argument("--severity", choices=["critical", "high", "medium", "low"], required=True)
    finding_create.add_argument("--detail", required=True)
    finding_create.set_defaults(capability_id="review.finding.create")
    finding_list = finding_sub.add_parser("list")
    finding_list.set_defaults(capability_id="review.finding.list")

    decision = sub.add_parser("decision")
    decision_sub = decision.add_subparsers(dest="decision_command", required=True)
    decision_create = decision_sub.add_parser("create")
    decision_create.add_argument("--title", required=True)
    decision_create.add_argument("--rationale", required=True)
    decision_create.add_argument("--disposition", required=True)
    decision_create.set_defaults(capability_id="decision.create")
    decision_list = decision_sub.add_parser("list")
    decision_list.set_defaults(capability_id="decision.list")

    aria = sub.add_parser("aria")
    aria_sub = aria.add_subparsers(dest="aria_command", required=True)
    runtime = aria_sub.add_parser("runtime")
    runtime_sub = runtime.add_subparsers(dest="runtime_command", required=True)
    runtime_list = runtime_sub.add_parser("list")
    runtime_list.set_defaults(capability_id="aria.runtime.list")
    runtime_update = runtime_sub.add_parser("update")
    runtime_update.add_argument("--patch-json", required=True)
    runtime_update.add_argument("--execute", action="store_true")
    runtime_update.set_defaults(capability_id="aria.runtime.config.update")
    runtime_enablement = runtime_sub.add_parser("enablement")
    runtime_enablement_sub = runtime_enablement.add_subparsers(dest="runtime_enablement_command", required=True)
    runtime_enablement_set = runtime_enablement_sub.add_parser("set")
    runtime_enablement_set.add_argument("--runtime-id", required=True)
    runtime_enablement_set.add_argument("--enabled", choices=["true", "false"], required=True)
    runtime_enablement_set.add_argument("--execute", action="store_true")
    runtime_enablement_set.set_defaults(capability_id="aria.runtime.enablement.update")
    nyx = aria_sub.add_parser("nyx")
    nyx_sub = nyx.add_subparsers(dest="nyx_command", required=True)
    nyx_list = nyx_sub.add_parser("list")
    nyx_list.set_defaults(capability_id="aria.nyx.list")
    runtime_dashboard = aria_sub.add_parser("dashboard")
    runtime_dashboard_sub = runtime_dashboard.add_subparsers(dest="runtime_dashboard_command", required=True)
    runtime_dashboard_summary = runtime_dashboard_sub.add_parser("summary")
    runtime_dashboard_summary.set_defaults(capability_id="runtime.dashboard.summary")
    agent = aria_sub.add_parser("agent")
    agent_sub = agent.add_subparsers(dest="agent_command", required=True)
    agent_surface = agent_sub.add_parser("surface")
    agent_surface_sub = agent_surface.add_subparsers(dest="agent_surface_command", required=True)
    agent_surface_update = agent_surface_sub.add_parser("update")
    agent_surface_update.add_argument("--agent-id", required=True)
    agent_surface_update.add_argument("--config-patch-json", default=None)
    agent_surface_update.add_argument("--harness-patch-json", default=None)
    agent_surface_update.add_argument("--execute", action="store_true")
    agent_surface_update.set_defaults(capability_id="aria.agent.surface.update")

    hive = sub.add_parser("agenthive")
    hive_sub = hive.add_subparsers(dest="agenthive_command", required=True)
    hive_project = hive_sub.add_parser("project")
    hive_project_sub = hive_project.add_subparsers(dest="agenthive_project_command", required=True)
    hive_project_list = hive_project_sub.add_parser("list")
    hive_project_list.set_defaults(capability_id="agenthive.project.list")
    hive_project_upsert = hive_project_sub.add_parser("upsert")
    hive_project_upsert.add_argument("--project-json", required=True)
    hive_project_upsert.add_argument("--execute", action="store_true")
    hive_project_upsert.set_defaults(capability_id="agenthive.project.upsert")
    hive_task = hive_sub.add_parser("task")
    hive_task_sub = hive_task.add_subparsers(dest="agenthive_task_command", required=True)
    hive_task_upsert = hive_task_sub.add_parser("upsert")
    hive_task_upsert.add_argument("--project", required=True)
    hive_task_upsert.add_argument("--task-json", required=True)
    hive_task_upsert.add_argument("--execute", action="store_true")
    hive_task_upsert.set_defaults(capability_id="agenthive.task.upsert")
    hive_backlog = hive_sub.add_parser("backlog")
    hive_backlog_sub = hive_backlog.add_subparsers(dest="agenthive_backlog_command", required=True)
    hive_backlog_summary = hive_backlog_sub.add_parser("summary")
    hive_backlog_summary.add_argument("--project", required=True)
    hive_backlog_summary.set_defaults(capability_id="agenthive.backlog.summary")

    orbit = sub.add_parser("orbit")
    orbit_sub = orbit.add_subparsers(dest="orbit_command", required=True)
    orbit_snapshot = orbit_sub.add_parser("snapshot")
    orbit_snapshot.set_defaults(capability_id="orbit.snapshot")
    orbit_schedule = orbit_sub.add_parser("schedule")
    orbit_schedule_sub = orbit_schedule.add_subparsers(dest="orbit_schedule_command", required=True)
    orbit_schedule_update = orbit_schedule_sub.add_parser("update")
    orbit_schedule_update.add_argument("--path", required=True)
    orbit_schedule_update.add_argument("--updates-json", required=True)
    orbit_schedule_update.add_argument("--execute", action="store_true")
    orbit_schedule_update.set_defaults(capability_id="orbit.schedule.update")
    orbit_task = orbit_sub.add_parser("task")
    orbit_task_sub = orbit_task.add_subparsers(dest="orbit_task_command", required=True)
    orbit_task_update = orbit_task_sub.add_parser("update")
    orbit_task_update.add_argument("--path", required=True)
    orbit_task_update.add_argument("--updates-json", required=True)
    orbit_task_update.add_argument("--execute", action="store_true")
    orbit_task_update.set_defaults(capability_id="orbit.task.update")

    return parser


def _payload_from_args(args: argparse.Namespace) -> dict:
    payload = {}
    for key in (
        "title",
        "summary",
        "why_failed",
        "what_was_missed",
        "next_guardrail",
        "severity",
        "detail",
        "rationale",
        "disposition",
        "project",
        "runtime_id",
    ):
        if hasattr(args, key):
            payload[key] = getattr(args, key)
    if hasattr(args, "execute"):
        payload["execute"] = bool(args.execute)
    if hasattr(args, "path"):
        payload["path"] = args.path
    if hasattr(args, "project_json"):
        payload["project"] = json.loads(args.project_json)
    if hasattr(args, "task_json"):
        payload["task"] = json.loads(args.task_json)
    if hasattr(args, "updates_json"):
        payload["updates"] = json.loads(args.updates_json)
    if hasattr(args, "patch_json"):
        payload["patch"] = json.loads(args.patch_json)
    if hasattr(args, "runtime_id"):
        payload["runtime_id"] = args.runtime_id
    if hasattr(args, "enabled"):
        payload["enabled"] = args.enabled == "true"
    if hasattr(args, "agent_id"):
        payload["agent_id"] = args.agent_id
    if hasattr(args, "config_patch_json") and args.config_patch_json:
        payload["config_patch"] = json.loads(args.config_patch_json)
    if hasattr(args, "harness_patch_json") and args.harness_patch_json:
        payload["harness_patch"] = json.loads(args.harness_patch_json)
    return payload


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    service = CapabilityService()
    result = service.invoke(args.capability_id, _payload_from_args(args))
    json.dump(result, sys.stdout, ensure_ascii=False, indent=2)
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
