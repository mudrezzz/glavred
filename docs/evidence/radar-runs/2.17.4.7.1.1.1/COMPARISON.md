# Slice 2.17.4.7.1.1.1 live comparison

Checked on 2026-07-23 against the remote `flowise` Docker runtime.

## Accepted run

- Project: `project-ai-design-patterns`.
- Radar: `ai-pattern-radar-industrial-cases`.
- RadarRun: `radar-run-ai-pattern-radar-industrial-cases-4`.
- Run and scoring status: `succeeded`.
- Opportunity coverage: `search-opportunity-coverage-v2`, status `sufficient`.
- Search calls: `3`; read cap: `2`; both limits are unchanged.
- Results: `34` raw results, `2` selected readable materials, `1` review-eligible signal.
- Delivered requirements: `3`; required delivery gaps: `0`; optional delivery gaps: `4`.
- Every requirement, query, raw result, read decision, material, fragment, and signal
  handle resolves; unresolved counts are zero.

## Evidence delivery

The two read slots have different jobs:

1. `global.andersen.com` is the core implementation case. It supports the industrial
   context, practical applicability, and implementation mechanism.
2. `arxiv.org` is an independent benchmark candidate. It was selected with
   `independent-evidence-priority` and supports the outcome/source-evidence search
   targets.

The arXiv material did not automatically corroborate the Andersen claim. It is
independent, but it does not prove the same concrete result. The trace therefore keeps
`corroboration-not-found` instead of treating query lineage or a broadly related
benchmark as delivered confirmation.

The report also distinguishes partial progress:

- productive tension stopped at `queryExecuted` because no result was found;
- novelty and advertising-noise requirements stayed at `planned` because the fixed
  three-call budget prioritized required evidence;
- outcome and source-credibility evidence reached `readableEvidence`, but was not used
  by the accepted signal.

These are optional gaps. They remain visible without turning a useful first-party case
into a false required failure.

## Source posture consistency

The accepted signal is:

- ownership: `firstParty`;
- claim support: `singleSource`;
- outcome support: `reported`;
- source-credibility criterion: `partial / caution`;
- final recommendation: `reviewWithCaution`.

The criterion says that the source describes its own result and independent
corroboration was not found. The system source-posture check says the same thing.
`benchmarkReport.sourcePostureConsistency.consistent` is `true`.

This closes the contradiction from RadarRun `radar-run-ai-pattern-radar-industrial-cases-2`,
where executed search could be presented as evidence delivery and source credibility
could disagree with the source-origin check.

## Context and token budget

No provider or read cap was raised.

- Search serialized messages: `207`, `201`, and `284` characters.
- Extraction attempts: `12,750`, `14,029`, and `13,524` of `16,000` characters.
- Scoring: `17,394` of `22,000` characters.
- Direct budget incidents: `0`.
- Known provider usage: search `48,287`, extraction `12,297`, scoring `5,030`;
  total `65,614` tokens.

The previous run recorded `124,367` known tokens. The lower accepted-run total is
useful operational evidence, but not treated as a guaranteed optimization: web-search
provider usage varies by result set. The architectural guarantee is unchanged caps,
bounded context, and zero budget incidents.

## UI and review proof

The authenticated UI shows delivery stages, stop reasons, readable source posture,
outcome support, and corroboration without exposing raw technical IDs. Source and trace
links open successfully. Edit mode preserves source and evidence context; HTML title
whitespace is normalized before persistence.

Manual scoring revision `2` reused saved artifacts, and one review event approved the
signal without mutating evidence. No page-level overflow was found at `390`, `1180`,
`1440`, `1904`, or `2048` pixels.
