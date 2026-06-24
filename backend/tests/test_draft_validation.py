from backend.app.application.draft_validator_orchestrator import DraftValidatorOrchestrator


def test_validator_checks_all_candidates_and_marks_selected() -> None:
    report = DraftValidatorOrchestrator().validate(
        draft_artifact={
            "candidates": [
                {"id": "candidate-1", "title": "Good", "body": "Short body"},
                {"id": "candidate-2", "title": "", "body": "{'id': 'raw'}"},
            ],
            "selection": {
                "selectedCandidateId": "candidate-1",
                "scorecard": [
                    {"candidateId": "candidate-2", "selectionStatus": "excluded", "selectionReasons": ["raw-artifact-dump"]},
                ],
            },
        },
        context_artifact={"postContract": {}},
        rule_pack={},
        material_plan={},
    )

    payload = report.to_payload()
    assert payload["summary"]["candidateCount"] == 2
    assert payload["candidateReports"][0]["selected"] is True
    assert payload["candidateReports"][1]["status"] == "critical"
    assert payload["candidateReports"][1]["findings"][0]["validatorId"] == "publishability.title"


def test_validator_reports_size_cta_and_attribution_findings() -> None:
    report = DraftValidatorOrchestrator().validate(
        draft_artifact={
            "candidates": [
                {
                    "id": "candidate-1",
                    "title": "Oversized",
                    "body": "42% adoption growth without source.\n\n" + ("x" * 80),
                    "usedEvidence": ["external-evidence-1"],
                }
            ],
            "selection": {"selectedCandidateId": "candidate-1", "scorecard": []},
        },
        context_artifact={
            "postContract": {
                "cta": "Check the product loop.",
                "publicationSizeContract": {
                    "minChars": 20,
                    "maxChars": 60,
                    "hardMaxChars": 70,
                    "paragraphRange": {"min": 3, "max": 4},
                },
            },
            "sourceLedger": {
                "claims": [
                    {
                        "id": "external-evidence-1",
                        "type": "externalEvidenceClaim",
                        "source": "Independent report",
                        "provenance": {"sourceTitle": "Independent report", "sourceUrl": "https://example.com/report"},
                    }
                ]
            },
        },
        rule_pack={},
        material_plan={"claimsRequiringAttribution": ["external-evidence-1"]},
    )

    findings = report.to_payload()["candidateReports"][0]["findings"]
    validator_ids = {finding["validatorId"] for finding in findings}
    assert "size.hard-max" in validator_ids
    assert "shape.paragraph-range" in validator_ids
    assert "contract.cta" in validator_ids
    assert "evidence.attribution" in validator_ids


def test_validator_detects_forbidden_moves_and_rejected_evidence() -> None:
    report = DraftValidatorOrchestrator().validate(
        draft_artifact={
            "candidates": [
                {
                    "id": "candidate-1",
                    "title": "Risky",
                    "body": "This draft invent facts and cites rejected-claim as proof.",
                    "usedEvidence": ["rejected-claim"],
                }
            ],
            "selection": {"selectedCandidateId": "candidate-1", "scorecard": []},
        },
        context_artifact={"postContract": {}},
        rule_pack={
            "forbiddenMoves": [
                {"id": "forbidden-invent", "statement": "invent facts"},
            ]
        },
        material_plan={"rejectedEvidence": ["rejected-claim"]},
    )

    findings = report.to_payload()["candidateReports"][0]["findings"]
    validator_ids = {finding["validatorId"] for finding in findings}
    assert "rules.forbidden-move" in validator_ids
    assert "evidence.rejected-proof" in validator_ids
