from backend.app.upstream.application.search_opportunity_report import SearchOpportunityCoverageReportBuilder


def test_useful_yield_report_resolves_complete_requirement_to_signal_lineage() -> None:
    report = SearchOpportunityCoverageReportBuilder().build(
        run=run_fixture(),
        found_materials=[material_fixture()],
        source_signals=[signal_fixture("recommended")],
    ).to_payload()

    assert report["status"] == "sufficient"
    assert report["firstFailureStage"] is None
    assert report["reviewEligibleYield"] == {"count": 1, "denominator": 1, "ratio": 1.0}
    assert report["version"] == "search-opportunity-coverage-v2"
    assert report["deliveredRequirementIds"] == ["requirement-topic"]
    assert report["requirementCoverage"][0]["furthestStage"] == "usedBySignal"
    assert report["corroborationCoverage"]["gaps"] == [{
        "signalId": "signal-1",
        "reason": "corroboration-not-found",
    }]
    assert report["unresolvedHandles"] == {
        "requirement": 0,
        "query": 0,
        "rawResult": 0,
        "readDecision": 0,
        "material": 0,
        "fragment": 0,
        "signal": 0,
    }
    assert report["lineage"][-1]["requirementIds"] == ["requirement-topic"]


def test_zero_yield_identifies_each_first_failure_stage() -> None:
    builder = SearchOpportunityCoverageReportBuilder()
    no_search = run_fixture()
    no_search["operations"] = []
    no_search["rawResults"] = []
    assert builder.build(run=no_search, found_materials=[], source_signals=[]).first_failure_stage == "providerSearch"

    no_raw = run_fixture()
    no_raw["rawResults"] = []
    assert builder.build(run=no_raw, found_materials=[], source_signals=[]).first_failure_stage == "triage"

    assert builder.build(run=run_fixture(), found_materials=[], source_signals=[]).first_failure_stage == "read"
    assert builder.build(run=run_fixture(), found_materials=[material_fixture()], source_signals=[]).first_failure_stage == "signalExtraction"
    assert builder.build(
        run=run_fixture(), found_materials=[material_fixture()], source_signals=[signal_fixture("notRecommended")]
    ).first_failure_stage == "signalScoring"


def test_provider_outage_is_inconclusive_instead_of_zero_yield() -> None:
    run = run_fixture()
    run["operations"] = [{"kind": "openWebQuery", "status": "skipped", "skippedReason": "openrouter-not-configured"}]
    run["rawResults"] = []

    report = SearchOpportunityCoverageReportBuilder().build(run=run, found_materials=[], source_signals=[])

    assert report.status == "inconclusive"
    assert report.first_failure_stage == "providerSearch"
    assert "provider-runtime-inconclusive" in report.reason_codes


def test_unresolved_lineage_handles_are_counted_not_silently_ignored() -> None:
    signal = signal_fixture("reviewWithCaution")
    signal["evidenceRefs"] = [{"materialId": "missing-material", "fragmentId": "missing-fragment"}]

    report = SearchOpportunityCoverageReportBuilder().build(
        run=run_fixture(), found_materials=[material_fixture()], source_signals=[signal]
    )

    assert report.unresolved_handles["material"] == 1
    assert report.unresolved_handles["fragment"] == 1


def test_executed_query_without_result_is_not_delivered_evidence() -> None:
    run = run_fixture()
    run["rawResults"] = []
    run["searchTriage"]["readPlan"]["decisions"] = []

    report = SearchOpportunityCoverageReportBuilder().build(
        run=run,
        found_materials=[],
        source_signals=[],
    ).to_payload()

    coverage = report["requirementCoverage"][0]
    assert coverage["furthestStage"] == "queryExecuted"
    assert coverage["delivered"] is False
    assert coverage["stopReason"] == "no-result-found"
    assert report["status"] == "zeroYield"


def test_discovered_but_unsupported_result_stops_at_result_found() -> None:
    run = run_fixture()
    run["rawResults"][0]["supportedRequirementIds"] = []
    run["searchTriage"]["readPlan"]["decisions"][0]["supportedRequirementIds"] = []

    report = SearchOpportunityCoverageReportBuilder().build(
        run=run,
        found_materials=[],
        source_signals=[],
    ).to_payload()

    coverage = report["requirementCoverage"][0]
    assert coverage["furthestStage"] == "resultFound"
    assert coverage["stopReason"] == "evidence-target-not-supported"
    assert coverage["delivered"] is False


def run_fixture() -> dict:
    return {
        "id": "run-1",
        "searchPlan": {
            "requirementProfile": {
                "requirements": [{"id": "requirement-topic", "role": "required"}],
            },
            "queries": [{
                "id": "query-1",
                "family": "caseExample",
                "evidenceTarget": "caseExample",
                "query": "industrial AI case study",
                "requirementIds": ["requirement-topic"],
            }],
            "intents": [{"family": "caseExample", "evidenceTarget": "caseExample"}],
            "uncoveredRequiredSearchRequirements": [],
        },
        "operations": [{"kind": "openWebQuery", "status": "succeeded", "target": "industrial AI case study"}],
        "rawResults": [{
            "id": "raw-1",
            "queryId": "query-1",
            "discoveredRequirementIds": ["requirement-topic"],
            "supportedRequirementIds": ["requirement-topic"],
        }],
        "searchTriage": {
            "readPlan": {
                "decisions": [{
                    "rawResultId": "raw-1",
                    "status": "selected",
                    "requirementIds": ["requirement-topic"],
                    "supportedRequirementIds": ["requirement-topic"],
                }],
            },
        },
        "signalExtraction": {"status": "succeeded"},
        "signalScoring": {"status": "succeeded"},
    }


def material_fixture() -> dict:
    return {
        "id": "material-1",
        "status": "found",
        "discoveryTrace": {
            "requirementIds": ["requirement-topic"],
            "discoveredRequirementIds": ["requirement-topic"],
            "supportedRequirementIds": ["requirement-topic"],
            "queryIds": ["query-1"],
            "rawResultIds": ["raw-1"],
            "families": ["caseExample"],
            "evidenceTypes": ["caseExample"],
        },
        "contentFragments": [{"id": "fragment-1", "text": "Evidence"}],
    }


def signal_fixture(recommendation: str) -> dict:
    return {
        "id": "signal-1",
        "evidenceRefs": [{"materialId": "material-1", "fragmentId": "fragment-1"}],
        "utilityReport": {
            "recommendation": recommendation,
            "qualityChecks": [{
                "checkId": "source-posture",
                "details": {
                    "ownershipPosture": "firstParty",
                    "claimSupport": "singleSource",
                },
            }],
        },
    }
