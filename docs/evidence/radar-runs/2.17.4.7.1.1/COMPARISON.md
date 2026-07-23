# Slice 2.17.4.7.1.1 live comparison

Checked on 2026-07-23 against the remote `flowise` Docker runtime.

## Accepted run

- Project: `project-ai-design-patterns`.
- Radar: `ai-pattern-radar-industrial-cases`.
- RadarRun: `radar-run-ai-pattern-radar-industrial-cases-2`.
- Run status: `succeeded`.
- Opportunity status: `sufficient`; first failure stage: none.
- Eight enabled filters received an explicit search role. Six searchable requirements
  were executed; required uncovered requirements: `0`.
- Executed query families: `caseExample`, `benchmarkPaper`, `limitationCritique`.
- Raw decisions: 60 total, 2 selected, 10 rejected, 10 duplicate, 38 deferred by the
  unchanged read budget.
- Both selected URLs were readable. One material produced one grounded Russian signal;
  its recommendation is `reviewWithCaution`.
- Extracted yield: `1/2`; review-eligible yield: `1/1`.
- Unresolved requirement/query/material/fragment handles: `0/0/0/0`.
- Accepted generic-news, pricing, and model-leaderboard noise: `0`.
- No `PostCandidate`, plan slot, or DraftRun was created.

## What changed from the baseline

The pre-slice editorial baseline is RadarRun
`radar-run-ai-pattern-radar-industrial-cases-9` from 2026-07-22. It used three family
queries but had no filter-derived requirement profile or post-scoring useful-yield
report. It returned 40 raw results, two materials, and three caution signals, while
retrieval stayed `partial` because one search response was malformed and one URL read
returned HTTP 403.

The accepted run keeps the same three-call search cap but changes the meaning of the
campaign:

| Proof | Baseline | Accepted run |
| --- | --- | --- |
| Search calls | 3 planned; 2 succeeded | 3 planned; 3 succeeded |
| Requirement handles | absent | present on every executed query |
| Required coverage gaps | limitation direction skipped | none |
| Query families | broad, case, benchmark | case, benchmark, limitation |
| Raw results | 40 | 60 |
| Readable materials | 1 (plus one failed read) | 2 |
| Signals | 3 | 1 |
| Review-eligible signals | 3 | 1 |
| Useful-yield diagnosis | absent | `sufficient`, no failed stage |
| Resolvable end-to-end lineage | not available | complete, 0 unresolved handles |

The accepted run does not maximize signal count. It proves that the radar searched the
configured evidence directions and produced at least one review-worthy signal without
weakening filters.

## Context and token budget

All direct current-call and serialized-message gates passed. Search calls used 692
serialized characters in total versus 834 in the baseline, despite carrying explicit
requirement handles. No provider-input or message cap was increased.

Provider-reported token consumption was higher:

- Baseline known total: 75,474 tokens. This excludes the failed search call, for which
  usage was unavailable.
- Accepted known total: 124,367 tokens.
- Accepted search: 106,055 tokens across three successful OpenRouter web-search calls.
- Accepted extraction: 13,255 tokens across failed primary, failed repair, and accepted
  backup attempts.
- Accepted scoring: 5,057 tokens on the accepted primary attempt.

This is not hidden as an efficiency win. The increase is mainly provider-side web
search usage plus two strict extraction retries, not growth of the repository-owned
context. Extraction messages stayed at or below 13,697/16,000 characters; scoring used
17,283/22,000. Future provider/search-cost optimization can use this trace without
relaxing language or grounding checks.

## UI and retry proof

The authenticated UI displayed the requirement and useful-yield blocks, opened source
and trace links, and stayed within the page width at 390, 1180, 1440, 1904, and 2048
pixels. Manual scoring revision 2 reused saved artifacts and did not launch search,
URL reading, or extraction. One human review event approved the signal without changing
its source evidence.
