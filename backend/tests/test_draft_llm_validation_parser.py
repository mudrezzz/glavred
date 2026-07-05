from backend.app.drafting.application.validation.draft_llm_validation_parser import LlmValidationParser


def test_positive_no_repair_findings_are_observations() -> None:
    findings, observations = LlmValidationParser().parse_report(
        candidate_id="candidate-1",
        payload={
            "summary": "Candidate passes editorial quality checks.",
            "findings": [{
                "validatorId": "llm.publisher-fit",
                "severity": "warning",
                "message": "Excellent publisher fit and coherent author position.",
                "evidenceExcerpt": "Body excerpt",
                "repairGuidance": "No repair needed",
            }],
            "observations": [{
                "validatorId": "llm.coherence",
                "status": "pass",
                "message": "The draft is coherent.",
                "repairGuidance": "No repair needed",
            }],
        },
    )

    assert findings == []
    assert [item.validator_id for item in observations] == ["llm.publisher-fit", "llm.coherence"]


def test_actionable_warning_remains_finding() -> None:
    findings, observations = LlmValidationParser().parse_report(
        candidate_id="candidate-1",
        payload={
            "summary": "Needs repair",
            "findings": [{
                "validatorId": "source-grounding",
                "severity": "warning",
                "message": "Public claim is not grounded.",
                "repairGuidance": "Name the source or remove the claim.",
            }],
        },
    )

    assert observations == []
    assert findings[0].validator_id == "llm.source-grounding"
    assert findings[0].severity.value == "warning"


def test_critical_no_repair_marker_remains_finding() -> None:
    findings, observations = LlmValidationParser().parse_report(
        candidate_id="candidate-1",
        payload={
            "summary": "Critical issue",
            "findings": [{
                "validatorId": "llm.source-grounding",
                "severity": "critical",
                "message": "Invented public proof.",
                "repairGuidance": "No repair needed",
            }],
        },
    )

    assert observations == []
    assert findings[0].severity.value == "critical"
