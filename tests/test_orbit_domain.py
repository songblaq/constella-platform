from __future__ import annotations

import json
from pathlib import Path
from types import SimpleNamespace

import pytest

from constella_platform.domains import orbit


def test_read_status_prefers_command_output(monkeypatch):
    def fake_run(command, capture_output, text, check, timeout):
        assert command == list(orbit.DEFAULT_STATUS_COMMAND)
        assert capture_output is True
        assert text is True
        assert check is True
        assert timeout == 30
        return SimpleNamespace(
            stdout='{"mode": "active", "week": "2", "tick_count_24h": 12}',
            stderr="",
        )

    monkeypatch.setattr(orbit.subprocess, "run", fake_run)

    status = orbit.read_status()

    assert status["mode"] == "active"
    assert status["week"] == "2"
    assert status["tick_count_24h"] == 12
    assert status["source"] == "command"
    assert status["command"] == list(orbit.DEFAULT_STATUS_COMMAND)


def test_read_status_falls_back_to_json_file(tmp_path, monkeypatch):
    status_path = tmp_path / "orbit-status.json"
    status_path.write_text('{"mode": "shadow", "tick_count_24h": 3}', encoding="utf-8")

    def fake_run(*args, **kwargs):
        raise FileNotFoundError("orbit-status.py missing")

    monkeypatch.setattr(orbit.subprocess, "run", fake_run)

    status = orbit.read_status(status_json_path=status_path)

    assert status["mode"] == "shadow"
    assert status["tick_count_24h"] == 3
    assert status["source"] == "file"
    assert status["path"] == str(status_path)


def test_read_sync_summary_parses_latest_block(tmp_path):
    log_path = tmp_path / "orbit-hive-sync.stdout.log"
    log_path.write_text(
        "\n".join(
            [
                "[orbit-hive-sync] 동기화 시작",
                "  AH → ORBIT 신규 등록: 2 tasks",
                "  AH → ORBIT: 79 tasks 상태 캐싱",
                "  ORBIT → Collab: 1 runs 기록",
                "[orbit-hive-sync] 동기화 완료",
                "[orbit-hive-sync] 동기화 시작",
                "  AH → ORBIT 신규 등록: 0 tasks",
                "  AH → ORBIT: 175 tasks 상태 캐싱",
                "  ORBIT → Collab: 0 runs 기록",
                "[orbit-hive-sync] 동기화 완료",
            ]
        ),
        encoding="utf-8",
    )

    sync = orbit.read_sync_summary(sync_log_path=log_path)

    assert sync["available"] is True
    assert sync["completed"] is True
    assert sync["new_registrations"] == 0
    assert sync["cached_task_count"] == 175
    assert sync["collab_runs_recorded"] == 0
    assert sync["summary"] == "AH→ORBIT cached=175, new=0, ORBIT→Collab runs=0"
    assert sync["block"][-1] == "[orbit-hive-sync] 동기화 완료"


def test_read_snapshot_combines_status_and_sync(tmp_path, monkeypatch):
    orbit_home = tmp_path / ".aria" / "orbit"
    log_dir = orbit_home / "log"
    log_dir.mkdir(parents=True)
    status_path = orbit_home / "orbit-status.json"
    sync_path = log_dir / "orbit-hive-sync.stdout.log"
    status_path.write_text('{"mode": "active", "week": "1"}', encoding="utf-8")
    sync_path.write_text(
        "\n".join(
            [
                "[orbit-hive-sync] 동기화 시작",
                "  AH → ORBIT 신규 등록: 0 tasks",
                "  AH → ORBIT: 12 tasks 상태 캐싱",
                "  ORBIT → Collab: 0 runs 기록",
                "[orbit-hive-sync] 동기화 완료",
            ]
        ),
        encoding="utf-8",
    )

    def fake_run(*args, **kwargs):
        raise FileNotFoundError("orbit-status.py missing")

    monkeypatch.setattr(orbit.subprocess, "run", fake_run)
    monkeypatch.setenv("CONSTELLA_ARIA_HOME", str(tmp_path / ".aria"))

    snapshot = orbit.read_snapshot(
    )

    assert snapshot["status"]["mode"] == "active"
    assert snapshot["status"]["source"] == "file"
    assert snapshot["sync"]["cached_task_count"] == 12
    assert snapshot["sync"]["source"] == "log"


@pytest.mark.parametrize(
    ("helper_name", "filename", "kind"),
    [
        ("preview_schedule_mutation", "orbit-schedule.json", "schedule"),
        ("preview_task_mutation", "orbit-task.json", "task"),
    ],
)
def test_preview_mutation_helpers_merge_without_writing(tmp_path, helper_name, filename, kind):
    target_path = tmp_path / filename
    target_path.write_text(
        json.dumps(
            {
                "enabled": False,
                "window": {"start": "01:00", "end": "02:00"},
                "owner": "orbit",
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    helper = getattr(orbit, helper_name)
    preview = helper(
        target_path,
        {
            "enabled": True,
            "window": {"start": "03:00"},
            "labels": ["preview-first"],
        },
    )

    assert preview["kind"] == kind
    assert preview["mode"] == "preview"
    assert preview["path"] == str(target_path)
    assert preview["before"]["enabled"] is False
    assert preview["after"]["enabled"] is True
    assert preview["after"]["window"] == {"start": "03:00", "end": "02:00"}
    assert preview["after"]["labels"] == ["preview-first"]
    assert [change["path"] for change in preview["changes"]] == ["enabled", "labels", "window.start"]
    assert preview["changes"][0] == {"path": "enabled", "before": False, "after": True}
    assert preview["changes"][1] == {"path": "labels", "before": None, "after": ["preview-first"]}
    assert preview["changes"][2] == {"path": "window.start", "before": "01:00", "after": "03:00"}
    assert json.loads(target_path.read_text(encoding="utf-8"))["enabled"] is False


@pytest.mark.parametrize(
    ("helper_name", "filename", "kind"),
    [
        ("apply_schedule_mutation", "orbit-schedule.json", "schedule"),
        ("apply_task_mutation", "orbit-task.json", "task"),
    ],
)
def test_apply_mutation_helpers_only_write_when_enabled(tmp_path, helper_name, filename, kind):
    target_path = tmp_path / filename
    target_path.write_text('{"enabled": false}', encoding="utf-8")

    helper = getattr(orbit, helper_name)
    preview = helper(target_path, {"enabled": True})

    assert preview["kind"] == kind
    assert preview["mode"] == "preview"
    assert json.loads(target_path.read_text(encoding="utf-8")) == {"enabled": False}

    applied = helper(target_path, {"enabled": True}, execute=True)

    assert applied["kind"] == kind
    assert applied["mode"] == "applied"
    assert json.loads(target_path.read_text(encoding="utf-8")) == {"enabled": True}


@pytest.mark.parametrize(
    ("helper_name", "filename", "kind"),
    [
        ("preview_schedule_mutation", "orbit-schedule.json", "schedule"),
        ("preview_task_mutation", "orbit-task.json", "task"),
    ],
)
def test_mutation_helpers_include_dry_run_and_rollback_metadata(tmp_path, helper_name, filename, kind):
    target_path = tmp_path / filename
    target_path.write_text(
        json.dumps(
            {
                "enabled": False,
                "window": {"start": "01:00", "end": "02:00"},
                "owner": "orbit",
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    helper = getattr(orbit, helper_name)
    preview = helper(
        target_path,
        {
            "enabled": True,
            "window": {"start": "03:00"},
            "labels": ["preview-first"],
        },
    )
    expected_preview_summary = f"Dry-run ORBIT {kind} mutation with 3 changes"

    assert preview["preview"] is True
    assert preview["dry_run"] is True
    assert preview["surface"] == f"orbit.{kind}"
    assert preview["summary"] == expected_preview_summary
    assert preview["rollback"]["available"] is True
    assert preview["rollback"]["mode"] == "restore"
    assert preview["rollback"]["path"] == str(target_path)
    assert preview["rollback"]["summary"] == f"Restore the prior ORBIT {kind} snapshot"
    assert preview["rollback"]["writes"][0]["path"] == str(target_path)
    assert preview["rollback"]["writes"][0]["kind"] == "json"
    assert json.loads(preview["rollback"]["writes"][0]["content"]) == preview["before"]

    applied = getattr(orbit, helper_name.replace("preview_", "apply_"))(
        target_path,
        {
            "enabled": True,
            "window": {"start": "03:00"},
            "labels": ["preview-first"],
        },
        execute=True,
    )
    expected_applied_summary = f"Applied ORBIT {kind} mutation with 3 changes"

    assert applied["preview"] is False
    assert applied["dry_run"] is False
    assert applied["surface"] == f"orbit.{kind}"
    assert applied["summary"] == expected_applied_summary
    assert applied["rollback"]["available"] is True
    assert applied["rollback"]["mode"] == "restore"
    assert json.loads(applied["rollback"]["writes"][0]["content"]) == applied["before"]
    assert json.loads(target_path.read_text(encoding="utf-8"))["enabled"] is True
