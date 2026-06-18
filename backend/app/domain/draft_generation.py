from dataclasses import dataclass


@dataclass(frozen=True)
class DraftBriefContext:
    id: str
    title: str
    rubric: str
    audience: str
    thesis: str
    conflict: str
    author_position: str
    evidence: list[str]
    examples: list[str]
    structure: list[str]
    cta: str
    risks: list[str]
    sources: list[str]


@dataclass(frozen=True)
class DraftEditorialModelContext:
    audience: str
    style_rules: list[str]
    forbidden_topics: list[str]
    goals: list[str]


@dataclass(frozen=True)
class DraftGenerationRequest:
    brief: DraftBriefContext
    editorial_model: DraftEditorialModelContext


@dataclass(frozen=True)
class GeneratedDraft:
    id: str
    brief_id: str
    title: str
    body: str
    version: int
    status: str
    updated_at: str
