from backend.app.application.draft_rule_registry_size import publication_size_registry
from backend.app.application.publication_size_contract_resolver import PublicationSizeContractResolver


def test_publication_size_contract_uses_slot_profile_and_size_intent() -> None:
    resolver = PublicationSizeContractResolver()
    contract = resolver.resolve(
        {
            "publicationSize": {
                "slotProfileId": "linkedin-article",
                "selectedProfile": {
                    "id": "linkedin-article",
                    "title": "LinkedIn article",
                    "platform": "LinkedIn",
                    "publicationKind": "article",
                    "minChars": 5000,
                    "targetChars": 7000,
                    "maxChars": 9000,
                    "hardMaxChars": 9500,
                    "paragraphRange": {"min": 10, "max": 18},
                    "sectionRange": {"min": 3, "max": 6},
                    "density": "deep",
                },
                "fabulaSizeIntent": "deep",
            }
        }
    )

    assert contract.profile_id == "linkedin-article"
    assert contract.source == "slotProfile"
    assert contract.target_chars == 8050
    assert contract.max_chars == 9500
    assert contract.hard_max_chars == 9500


def test_publication_size_contract_falls_back_to_demo_default() -> None:
    contract = PublicationSizeContractResolver().resolve({"publicationSize": {"platform": "Telegram"}})

    assert contract.profile_id == "telegram-post"
    assert contract.platform == "Telegram"
    assert contract.source == "demoDefault"


def test_publication_size_rules_are_machine_readable() -> None:
    rules = publication_size_registry(
        {
            "status": "created",
            "publicationSizeContract": PublicationSizeContractResolver().resolve({}).to_payload(),
        }
    )

    rule_ids = {rule.id for rule in rules}
    assert "contract:size:hard-max" in rule_ids
    assert "contract:size:target-range" in rule_ids
    assert "contract:size:paragraph-range" in rule_ids
    assert "contract:size:density" in rule_ids
