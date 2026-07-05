from backend.app.drafting.application.validation.draft_validator_orchestrator import DraftValidatorOrchestrator


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
    attribution = next(finding for finding in findings if finding["validatorId"] == "evidence.attribution")
    assert attribution["metadata"]["missingClaimIds"] == ["external-evidence-1"]
    assert "Independent report" in attribution["metadata"]["expectedAttributionMarkers"]["external-evidence-1"]


def test_validator_accepts_author_or_organization_attribution_markers() -> None:
    report = DraftValidatorOrchestrator().validate(
        draft_artifact={
            "candidates": [
                {
                    "id": "candidate-1",
                    "title": "Sourced",
                    "body": "42% of the argument is framed through Tian Pan and SQ Collective.",
                    "usedEvidence": ["external-evidence-tian", "external-evidence-sq"],
                }
            ],
            "selection": {"selectedCandidateId": "candidate-1", "scorecard": []},
        },
        context_artifact={
            "postContract": {},
            "sourceLedger": {
                "claims": [
                    {
                        "id": "external-evidence-tian",
                        "type": "externalEvidenceClaim",
                        "source": "publicEvidence",
                        "provenance": {"sourceTitle": "Tian Pan on product discovery", "sourceUrl": "https://tianpan.co/notes/product-discovery"},
                    },
                    {
                        "id": "external-evidence-sq",
                        "type": "externalEvidenceClaim",
                        "source": "publicEvidence",
                        "provenance": {"sourceTitle": "SQ Collective field note", "sourceUrl": "https://sqcollective.example/note"},
                    },
                ]
            },
        },
        rule_pack={},
        material_plan={"claimsRequiringAttribution": ["external-evidence-tian", "external-evidence-sq"]},
    )

    findings = report.to_payload()["candidateReports"][0]["findings"]
    assert "evidence.attribution" not in {finding["validatorId"] for finding in findings}


def test_validator_resolves_free_text_attribution_requirements_to_claim_markers() -> None:
    report = DraftValidatorOrchestrator().validate(
        draft_artifact={
            "candidates": [
                {
                    "id": "candidate-1",
                    "title": "Sourced",
                    "body": "B2BNotes estimates that 95% of pilots fail to scale, while RAND Corporation points to workflow misfit.",
                    "usedEvidence": [],
                }
            ],
            "selection": {"selectedCandidateId": "candidate-1", "scorecard": []},
        },
        context_artifact={
            "postContract": {},
            "sourceLedger": {
                "claims": [
                    {
                        "id": "external-evidence-b2bnotes",
                        "type": "externalEvidenceClaim",
                        "source": "publicEvidence",
                        "provenance": {"sourceTitle": "B2BNotes AI production gap", "sourceUrl": "https://b2bnotes.com/ai-production-gap"},
                    },
                    {
                        "id": "external-evidence-rand",
                        "type": "externalEvidenceClaim",
                        "source": "publicEvidence",
                        "provenance": {"sourceTitle": "RAND Corporation AI project failure report", "sourceUrl": "https://rand.org/ai-failure"},
                    },
                ]
            },
        },
        rule_pack={},
        material_plan={
            "claimsRequiringAttribution": [
                "95% of enterprise B2B AI pilots fail to scale - attribute to B2BNotes",
                "RAND five root causes including workflow misfit - attribute to RAND Corporation",
            ]
        },
    )

    findings = report.to_payload()["candidateReports"][0]["findings"]
    assert "evidence.attribution" not in {finding["validatorId"] for finding in findings}


def test_validator_keeps_unresolved_free_text_attribution_as_diagnostic() -> None:
    report = DraftValidatorOrchestrator().validate(
        draft_artifact={
            "candidates": [
                {
                    "id": "candidate-1",
                    "title": "Sourced",
                    "body": "42% adoption growth according to a public report.",
                    "usedEvidence": [],
                }
            ],
            "selection": {"selectedCandidateId": "candidate-1", "scorecard": []},
        },
        context_artifact={
            "postContract": {},
            "sourceLedger": {
                "claims": [
                    {
                        "id": "external-evidence-known",
                        "type": "externalEvidenceClaim",
                        "source": "publicEvidence",
                        "provenance": {"sourceTitle": "Known Source report", "sourceUrl": "https://known.example/report"},
                    }
                ]
            },
        },
        rule_pack={},
        material_plan={"claimsRequiringAttribution": ["42% adoption growth - attribute to Unknown Source"]},
    )

    payload = report.to_payload()["candidateReports"][0]
    validator_ids = {finding["validatorId"] for finding in payload["findings"]}
    assert "evidence.attribution" not in validator_ids
    assert "evidence.attribution.diagnostic" in validator_ids
    assert payload["status"] == "passed"


def test_validator_matches_attribution_per_claim() -> None:
    report = DraftValidatorOrchestrator().validate(
        draft_artifact={
            "candidates": [
                {
                    "id": "candidate-1",
                    "title": "Partly sourced",
                    "body": "42% of the argument is sourced from Tian Pan, with another public claim left unattributed.",
                    "usedEvidence": ["external-evidence-tian", "external-evidence-vamsee"],
                }
            ],
            "selection": {"selectedCandidateId": "candidate-1", "scorecard": []},
        },
        context_artifact={
            "postContract": {},
            "sourceLedger": {
                "claims": [
                    {
                        "id": "external-evidence-tian",
                        "type": "externalEvidenceClaim",
                        "source": "publicEvidence",
                        "provenance": {"sourceTitle": "Tian Pan on product discovery", "sourceUrl": "https://tianpan.co/notes/product-discovery"},
                    },
                    {
                        "id": "external-evidence-vamsee",
                        "type": "externalEvidenceClaim",
                        "source": "publicEvidence",
                        "provenance": {"sourceTitle": "AI Product Discovery with Vamsee Jasti", "sourceUrl": "https://example.com/vamsee-jasti"},
                    },
                ]
            },
        },
        rule_pack={},
        material_plan={"claimsRequiringAttribution": ["external-evidence-tian", "external-evidence-vamsee"]},
    )

    findings = report.to_payload()["candidateReports"][0]["findings"]
    attribution = next(finding for finding in findings if finding["validatorId"] == "evidence.attribution")
    assert attribution["claimIds"] == ["external-evidence-vamsee"]
    assert attribution["metadata"]["matchedClaimIds"] == ["external-evidence-tian"]
    assert attribution["metadata"]["missingClaimIds"] == ["external-evidence-vamsee"]


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
