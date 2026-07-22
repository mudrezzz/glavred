"""Owner: upstream.domain

Used by: signal utility, explainability, and relationship contracts.
Does not own: evaluation behavior, persistence, provider calls, or UI labels.
Architecture doc: docs/architecture/RADAR_TO_CANDIDATE_PIPELINE_TO_BE_2_17_4_6_2.md
"""

from enum import StrEnum


class SignalUtilityDimension(StrEnum):
    EVIDENCE_STRENGTH = "evidenceStrength"
    FACTUAL_SPECIFICITY = "factualSpecificity"
    SOURCE_CREDIBILITY = "sourceCredibility"
    MECHANISM = "mechanism"
    OBSERVABLE_OUTCOME = "observableOutcome"
    ACTIONABILITY = "actionability"
    TOPIC_AFFINITY = "topicAffinity"
    AUTHOR_FIT = "authorFit"
    AUDIENCE_VALUE = "audienceValue"
    POSITIONING = "positioningContribution"
    PROJECT_GOAL = "projectGoalContribution"
    NOVELTY = "novelty"
    PRODUCTIVE_TENSION = "productiveTension"
    FRESHNESS = "freshness"
    DUPLICATION_RISK = "duplicationRisk"
    PROMOTIONAL_NOISE = "promotionalNoise"
    PROHIBITED_CONTENT = "prohibitedContent"


class SignalUtilityStatus(StrEnum):
    MATCHED = "matched"
    PARTIAL = "partial"
    NOT_PROVEN = "notProven"
    CONFLICT = "conflict"


class SignalUtilityImportance(StrEnum):
    BLOCKING = "blocking"
    WEIGHTED = "weighted"
    DIAGNOSTIC = "diagnostic"


class SignalUtilityRecommendation(StrEnum):
    RECOMMENDED = "recommended"
    REVIEW_WITH_CAUTION = "reviewWithCaution"
    NOT_RECOMMENDED = "notRecommended"
    INCONCLUSIVE = "inconclusive"


class SignalCriterionOrigin(StrEnum):
    RADAR = "radar"
    PROJECT = "project"
    SYSTEM = "system"


class SignalCriterionEffect(StrEnum):
    PASS = "pass"
    CAUTION = "caution"
    BLOCK = "block"
    DIAGNOSTIC = "diagnostic"


class SignalResultSupport(StrEnum):
    OBSERVED = "observed"
    REPORTED = "reported"
    CAPABILITY_ONLY = "capabilityOnly"
    EXPECTED = "expected"
    MISSING = "missing"
    NOT_APPLICABLE = "notApplicable"


class SignalSourcePosture(StrEnum):
    INDEPENDENT = "independent"
    CORROBORATED = "corroborated"
    FIRST_PARTY = "firstParty"
    VENDOR = "vendor"
    UNKNOWN = "unknown"


class SignalRelationshipKind(StrEnum):
    EXACT_DUPLICATE = "exactDuplicate"
    SAME_CLAIM = "sameClaim"
    RELATED_SAME_SOURCE = "relatedSameSource"
    CORROBORATES = "corroborates"
    CONTRADICTS = "contradicts"
    DISTINCT = "distinct"
    INCONCLUSIVE = "inconclusive"


__all__ = tuple(name for name in globals() if name.startswith("Signal"))
