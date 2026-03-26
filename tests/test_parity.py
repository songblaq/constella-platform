from constella_platform.parity import build_operator_scenarios, build_shell_parity_report


def test_build_shell_parity_report_flags_missing_surfaces():
    capabilities = [
        {
            "capability_id": "agenthive.project.list",
            "surfaces": ["cli", "api"],
        },
        {
            "capability_id": "shell.parity.report",
            "surfaces": ["cli", "api", "tui", "gui"],
        },
    ]

    report = build_shell_parity_report(
        capabilities=capabilities,
        shell_status={"cli": True, "api": True, "tui": True, "gui": True},
    )

    assert report["summary"]["capability_count"] == 2
    assert report["summary"]["gap_count"] == 1
    assert report["gaps"][0]["capability_id"] == "agenthive.project.list"
    assert report["gaps"][0]["missing_surfaces"] == ["tui", "gui"]


def test_operator_scenarios_cover_core_operator_flows():
    scenarios = build_operator_scenarios()

    ids = {item["id"] for item in scenarios}
    assert "SCN-shell-overview" in ids
    assert "SCN-history-drilldown" in ids
    assert "SCN-orbit-health-check" in ids
