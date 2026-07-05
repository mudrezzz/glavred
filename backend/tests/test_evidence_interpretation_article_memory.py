from backend.app.drafting.application.artifacts.draft_article_dossier_builder import ArticleDossierBuilder
from backend.app.drafting.application.artifacts.draft_context_pack_builder import ContextPackBuilder
from backend.app.domain.draft_model_roles import DraftModelRole


def test_article_dossier_builder_creates_cards_from_evidence_interpretation() -> None:
    dossier = ArticleDossierBuilder().build(rule_pack={"evidenceInterpretation": interpretation_payload()})
    packs = ContextPackBuilder().build_all(dossier)

    assert any(card.id == "evidence-implication-implication-1" for card in dossier.cards)
    assert packs[DraftModelRole.STRATEGY.value]["metadata"]["itemCount"] >= 1
    assert packs[DraftModelRole.WRITER.value]["items"][0]["cardId"] == "evidence-implication-implication-1"


def interpretation_payload() -> dict:
    return {
        "implications": [{
            "id": "implication-1",
            "title": "Source changes the argument",
            "summary": "The post should discuss workflow adoption, not only model quality.",
            "claimIds": ["external-claim-1"],
            "publicEvidenceItemIds": ["public-1"],
            "ruleIds": ["rule-grounding"],
            "allowedUse": "needsQualification",
        }],
        "limits": [{
            "id": "limit-1",
            "title": "Do not overclaim",
            "summary": "The source qualifies adoption claims but does not prove universal failure.",
            "claimIds": ["external-claim-1"],
            "allowedUse": "needsQualification",
        }],
        "forbiddenOverclaims": [{
            "id": "overclaim-1",
            "title": "No universal claim",
            "summary": "Do not say every AI rollout fails.",
            "claimIds": ["external-claim-1"],
            "allowedUse": "doNotState",
        }],
    }
