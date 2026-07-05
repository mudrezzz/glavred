"""Owner: drafting.application.evidence

Used by: DraftRun evidence migration and legacy compatibility shims.
Does not own: API routing, SQLite persistence, provider transport, or UI trace layout.
Architecture doc: docs/architecture/BACKEND_ARCHITECTURE_TARGET.md
"""

from typing import Any

from backend.app.drafting.application.evidence.draft_rule_registry_sections import registry_rule
from backend.app.domain.draft_rule_registry import RuleRegistrySeverity, RuleRegistryValidatorType


class RuleRegistrySizePolicy:
    """Owns migrated helper behavior; module-level aliases remain compatibility-only."""

    @staticmethod
    def publication_size_registry(contract: dict[str, Any]) -> list:
        size = contract.get("publicationSizeContract")
        if not isinstance(size, dict):
            return []
        return [
            registry_rule(
                "contract:size:hard-max",
                "hardConstraints",
                "Hard publication length limit",
                f"Draft must not exceed {size.get('hardMaxChars')} characters.",
                "postContract.publicationSizeContract.hardMaxChars",
                RuleRegistrySeverity.HARD,
                validator=RuleRegistryValidatorType.DETERMINISTIC,
                priority=3,
                contract_refs=["publicationSizeContract"],
                scope="postContract.size",
            ),
            registry_rule(
                "contract:size:target-range",
                "qualityRubric",
                "Target publication length",
                f"Aim for {size.get('minChars')}-{size.get('maxChars')} characters around target {size.get('targetChars')}.",
                "postContract.publicationSizeContract.targetChars",
                RuleRegistrySeverity.WARNING,
                validator=RuleRegistryValidatorType.DETERMINISTIC,
                priority=22,
                contract_refs=["publicationSizeContract"],
                scope="postContract.size",
            ),
            registry_rule(
                "contract:size:paragraph-range",
                "dramaturgyRequirements",
                "Paragraph range",
                _range_statement("paragraphs", size.get("paragraphRange")),
                "postContract.publicationSizeContract.paragraphRange",
                RuleRegistrySeverity.WARNING,
                validator=RuleRegistryValidatorType.DETERMINISTIC,
                priority=32,
                contract_refs=["publicationSizeContract"],
                scope="postContract.size",
            ),
            registry_rule(
                "contract:size:section-range",
                "dramaturgyRequirements",
                "Section range",
                _range_statement("sections", size.get("sectionRange")),
                "postContract.publicationSizeContract.sectionRange",
                RuleRegistrySeverity.SOFT,
                validator=RuleRegistryValidatorType.DETERMINISTIC,
                priority=34,
                contract_refs=["publicationSizeContract"],
                scope="postContract.size",
            ),
            registry_rule(
                "contract:size:density",
                "qualityRubric",
                "Density expectation",
                f"Use {size.get('density')} information density for {size.get('publicationKind')}.",
                "postContract.publicationSizeContract.density",
                RuleRegistrySeverity.SOFT,
                validator=RuleRegistryValidatorType.DETERMINISTIC,
                priority=36,
                contract_refs=["publicationSizeContract"],
                scope="postContract.size",
            ),
        ]

    @staticmethod
    def _range_statement(label: str, value: Any) -> str:
        if not isinstance(value, dict):
            return ""
        return f"Use {value.get('min')}-{value.get('max')} {label}."

publication_size_registry = RuleRegistrySizePolicy.publication_size_registry
_range_statement = RuleRegistrySizePolicy._range_statement


__all__ = (
    'publication_size_registry',
    'RuleRegistrySizePolicy',
)
