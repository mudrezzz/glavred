from backend.app.drafting.application.quality import DraftRunQualityFidelityReporter


FINAL_ID = "revised-revised-candidate-research"


def test_non_final_candidate_findings_stay_visible_without_blocking_delivered_text() -> None:
    deterministic = [
        report("candidate-research", warnings=2),
        report("candidate-contrast", critical=1, warnings=2),
        report("candidate-practical", warnings=3),
        report("alternative-angle", warnings=1),
    ]
    llm = [
        report("candidate-research", warnings=2),
        report("candidate-contrast", critical=1, warnings=4),
        report("candidate-practical", critical=1, warnings=3),
        report("alternative-angle", warnings=3),
    ]
    quality = DraftRunQualityFidelityReporter().build(
        run_status="succeeded",
        steps=[
            step(
                "validation",
                {
                    "candidateReports": deterministic,
                    "llmValidationReport": {"candidateReports": llm},
                    "rankingRevision": {
                        "finalDecision": {"finalCandidateId": FINAL_ID},
                        "finalQualityGate": {
                            "status": "warning",
                            "independentReview": {
                                "candidateId": FINAL_ID,
                                "findings": [
                                    {
                                        "id": "style.paragraph-fragmentation.1",
                                        "validatorId": "finalQuality.independentReview",
                                        "severity": "warning",
                                        "candidateId": FINAL_ID,
                                        "message": "Paragraphs are fragmented.",
                                    }
                                ],
                            },
                            "finalDecision": {"finalCandidateId": FINAL_ID},
                        },
                    },
                },
            ),
            step("complete", {}),
        ],
        final_draft={"title": "Final", "body": "A useful final post."},
    )

    lifecycle = quality["issueLifecycle"]
    assert lifecycle["finalCandidateId"] == FINAL_ID
    assert lifecycle["criticalCount"] == 3
    assert lifecycle["diagnosticCriticalCount"] == 3
    assert lifecycle["diagnosticWarningCount"] == 20
    assert lifecycle["openCriticalCount"] == 0
    assert lifecycle["openWarningCount"] == 1
    assert lifecycle["finalGateWarningCount"] == 1
    assert quality["editorialStatus"] == "publishableWithCaution"
    assert quality["overallVerdict"] != "needsAttention"
    assert not any(item["validatorId"] == "finalQualityGate.status" for item in lifecycle["items"])


def test_unknown_candidate_scope_remains_open_conservatively() -> None:
    quality = DraftRunQualityFidelityReporter().build(
        run_status="succeeded",
        steps=[
            step(
                "validation",
                {
                    "candidateReports": [
                        {"findings": [{"validatorId": "legacy.warning", "severity": "warning", "message": "Unknown scope"}]}
                    ],
                    "rankingRevision": {
                        "finalDecision": {"finalCandidateId": "final-1"},
                        "finalQualityGate": {"status": "passed"},
                    },
                },
            ),
            step("complete", {}),
        ],
        final_draft={"title": "Final", "body": "Body"},
    )

    item = quality["issueLifecycle"]["items"][0]
    assert item["scope"] == "unknown"
    assert item["status"] == "open"
    assert item["appliesToFinalDraft"] is True


def test_accepted_repair_uses_effective_gate_and_resolves_initial_status() -> None:
    quality = DraftRunQualityFidelityReporter().build(
        run_status="succeeded",
        steps=[
            step(
                "validation",
                {
                    "rankingRevision": {
                        "finalDecision": {"finalCandidateId": "repaired-1"},
                        "finalQualityGate": {
                            "status": "critical",
                            "candidateId": "original-1",
                            "acceptedRepair": True,
                            "repairGate": {"status": "passed", "candidateId": "repaired-1", "independentReview": {"candidateId": "repaired-1", "findings": []}},
                            "finalDecision": {"finalCandidateId": "repaired-1", "source": "finalQualityRepair"},
                        },
                    }
                },
            ),
            step("complete", {}),
        ],
        final_draft={"title": "Final", "body": "Body"},
    )

    initial = next(item for item in quality["issueLifecycle"]["items"] if item["validatorId"] == "finalQualityGate.status")
    assert initial["status"] == "resolved"
    assert initial["statusReason"] == "accepted-final-repair"
    assert quality["issueLifecycle"]["openCriticalCount"] == 0
    assert quality["editorialStatus"] == "publishable"


def report(candidate_id: str, *, critical: int = 0, warnings: int = 0) -> dict:
    findings = [
        {
            "id": f"{candidate_id}-critical-{index}",
            "validatorId": f"critical.{index}",
            "severity": "critical",
            "message": "Critical issue",
        }
        for index in range(critical)
    ]
    findings.extend(
        {
            "id": f"{candidate_id}-warning-{index}",
            "validatorId": f"warning.{index}",
            "severity": "warning",
            "message": "Warning issue",
        }
        for index in range(warnings)
    )
    return {"candidateId": candidate_id, "findings": findings}


def step(key: str, artifact: dict) -> dict:
    return {"key": key, "status": "succeeded", "artifact": artifact}
