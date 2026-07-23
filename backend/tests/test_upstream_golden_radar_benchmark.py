from backend.app.upstream.application.benchmark import (
    get_golden_radar_benchmark_scenarios,
    run_radar_benchmark,
)


def test_golden_radar_benchmark_scenario_loads() -> None:
    scenarios = get_golden_radar_benchmark_scenarios()

    assert [scenario.id for scenario in scenarios] == ["benchmark-industrial-ai-maintenance-cases"]
    scenario = scenarios[0]
    assert scenario.project_id == "project-ai-design-patterns"
    assert scenario.radar_id == "ai-pattern-radar-industrial-cases"
    assert "limitationCritique" in scenario.expected_intent_families
    assert "ossTooling" in scenario.optional_intent_families


def test_golden_radar_benchmark_passes_with_recorded_fixture() -> None:
    report = run_radar_benchmark("benchmark-industrial-ai-maintenance-cases")
    payload = report.to_payload()

    assert report.status == "passed"
    assert report.missing_expectations == []
    assert report.unacceptable_noise_hits == []
    assert report.downstream_leaks == []
    assert report.trace_complete is True
    assert payload["counters"]["rawResultCount"] >= 5
    assert payload["counters"]["selectedReadCount"] >= 2
    assert payload["counters"]["foundMaterialCount"] >= 2
    assert payload["counters"]["distinctSelectedDomainCount"] >= 2
    assert payload["plannedCoverage"]["queryFamilies"]["missing"] == []
    assert payload["executedCoverage"]["queryFamilies"]["missing"] == []
    assert payload["usefulYield"]["counts"]["reviewEligibleCount"] == 2
    assert payload["usefulYield"]["recommendationDistribution"] == {
        "notRecommended": 1,
        "recommended": 1,
        "reviewWithCaution": 1,
    }


def test_golden_radar_benchmark_reports_campaign_trace_and_rejections() -> None:
    report = run_radar_benchmark("benchmark-industrial-ai-maintenance-cases")
    run = report.run
    plan = run["searchPlan"]

    assert {intent["family"] for intent in plan["intents"]} >= {
        "broadDiscovery",
        "caseExample",
        "benchmarkPaper",
        "limitationCritique",
    }
    assert len(plan["trace"]["intentCoverage"]) == len(plan["intents"])
    assert plan["trace"]["ownershipBoundary"].startswith("Search uses only bounded radar requirements")
    assert plan["requirementProfile"]["requirements"]
    assert plan["uncoveredRequiredSearchRequirements"] == []
    assert any(item["reason"] == "duplicate-url" for item in run["rejectedBeforeRead"])
    assert any("vendor.example" in item["url"] for item in run["rejectedBeforeRead"])
    assert all("vendor pricing" not in material["summary"].lower() for material in report.found_materials)


def test_golden_radar_benchmark_does_not_create_downstream_artifacts() -> None:
    report = run_radar_benchmark("benchmark-industrial-ai-maintenance-cases")
    payload_text = str(report.to_payload())

    assert report.downstream_leaks == []
    assert "sourceSignals" not in report.run
    assert "postCandidates" not in report.run
    assert "draftRuns" not in report.run
    assert "SourceSignal" not in payload_text
    assert "DraftRun" not in payload_text
