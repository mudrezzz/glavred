from backend.app.application.draft_article_dossier_builder import ArticleDossierBuilder
from backend.app.application.draft_context_pack_builder import ContextPackBuilder
from backend.app.domain.draft_model_roles import DraftModelRole


def test_article_dossier_builder_creates_cards_from_quality_artifacts() -> None:
    dossier = ArticleDossierBuilder().build(
        context_artifact={
            "enrichedSourceLedger": {
                "claims": [{
                    "id": "external-claim-1",
                    "type": "externalEvidenceClaim",
                    "statement": "Independent report qualifies adoption claims.",
                    "provenance": {"sourceTitle": "Independent report"},
                    "allowedUse": "needsQualification",
                }, {
                    "id": "signal-summary",
                    "type": "sourceClaim",
                    "statement": "Signal says demos fail without workflow adoption.",
                    "allowedUse": "canState",
                }]
            },
            "publicEvidence": {
                "items": [{
                    "id": "public-evidence-1",
                    "sourceTitle": "Independent report",
                    "snippet": "Workflow integration drives adoption.",
                    "allowedUse": "needsQualification",
                }]
            },
            "postContract": {"thesis": "Workflow before model", "forbiddenMoves": ["Do not invent facts"]},
        },
        rule_pack={"ruleRegistrySnapshot": {"rules": [{"id": "hard-size", "title": "Hard size", "severity": "hard"}]}},
        material_plan={"availableEvidence": ["external-claim-1"], "openQuestions": ["Need market counterexample"]},
        draft_artifact={"candidates": [{"id": "candidate-1", "title": "Draft", "rationale": "Grounded route"}], "selection": {"selectedCandidateId": "candidate-1"}},
        validation_artifact={"candidateReports": [{"candidateId": "candidate-1", "findings": [{"validatorId": "evidence.attribution", "severity": "warning", "message": "Needs attribution", "repairGuidance": "Name source"}]}]},
    )

    payload = dossier.to_payload()

    assert payload["metadata"]["byType"]["evidence"] >= 2
    assert payload["metadata"]["byType"]["claim"] >= 1
    assert payload["metadata"]["byType"]["risk"] >= 1
    assert any(card["id"] == "candidate-candidate-1" for card in payload["cards"])


def test_context_pack_builder_selects_role_relevant_cards() -> None:
    dossier = ArticleDossierBuilder().build(
        context_artifact={
            "sourceLedger": {"claims": [{"id": "claim-1", "statement": "Usable claim", "allowedUse": "canState"}]},
            "postContract": {"thesis": "Locked thesis", "forbiddenMoves": ["No hype"]},
        },
        material_plan={"openQuestions": ["Need proof"]},
    )

    packs = ContextPackBuilder().build_all(dossier)

    assert packs[DraftModelRole.WRITER.value]["metadata"]["itemCount"] >= 2
    assert packs[DraftModelRole.REVIEW.value]["items"][0]["cardId"]
    assert all("summary" in item for item in packs[DraftModelRole.STRATEGY.value]["items"])
