# Radar-to-Candidate Pipeline TO BE 2.17.4.6.2

Status: Slice `2.17.4.6.2` implemented; downstream Radar-to-Candidate stages remain the approved target.

AS IS sources:

- `docs/architecture/RADAR_RUN_PIPELINE_AS_IS.md`;
- `docs/architecture/UPSTREAM_SEARCH_AND_SIGNAL_ARCHITECTURE.md`.

Regenerate PDF:

```powershell
python scripts/generate-draft-run-pipeline-pdf.py `
  --source docs/architecture/RADAR_TO_CANDIDATE_PIPELINE_TO_BE_2_17_4_6_2.md `
  --output docs/architecture/RADAR_TO_CANDIDATE_PIPELINE_TO_BE_2_17_4_6_2.pdf
```

## 1. Change Intent

The current RadarRun can plan and execute web search, but its pre-read triage is too
dependent on provider order, keyword overlap, exact URL equality, and a first-domain
rule. The target pipeline must preserve every discovery decision while reading only
the strongest bounded set of sources.

The same architecture must prevent the later signal and candidate stages from
repeating the DraftRun context-growth problem. Rich upstream artifacts remain stored
for replay and accountability. A provider receives only an operation-specific,
budgeted projection with handles back to those artifacts.

## 2. Target Flow

```mermaid
flowchart TD
    A[SearchPlan] --> B[Budgeted openWebQuery]
    B --> C[RawSearchResult]
    C --> D[Normalization]
    D --> E[Duplicate groups]
    E --> F[Deterministic quality assessment]
    F --> G[Coverage-aware read plan]
    G --> H[URL read outcomes]
    H --> I[FoundMaterial]
    I --> J[Signal extraction dossier]
    J --> K[SourceSignal]
    K --> L[Signal scoring dossier]
    L --> M[SignalScore]
    M --> N[Candidate assembly dossier]
    N --> O[PostCandidate]
```

Only nodes through `FoundMaterial` are implemented in Slice `2.17.4.6.2`.
Signal extraction, scoring, candidate assembly, and candidate ranking remain
`NOT THIS SLICE` and must be implemented by their tracker-backed slices.

## 3. AS IS to TO BE Mapping

| Item | Status | TO BE | Proof |
| --- | --- | --- | --- |
| Search campaign planning | UNCHANGED | Deterministic intents, queries, source strategy, and budget skips remain authoritative. | Existing planner tests and trace. |
| Provider search | CHANGED vs AS IS | Every `openWebQuery` has a direct current-call budget and final serialized-message proof. | Operation trace, boundary tests, architecture smoke. |
| Citation normalization | CHANGED vs AS IS | URL, title, and snippet are bounded and normalized without deleting meaningful query parameters. | Normalization tests. |
| Duplicate handling | CHANGED vs AS IS | Stable duplicate groups retain all query, intent, family, and evidence handles. | Permutation and duplicate-group tests. |
| Pre-read scoring | CHANGED vs AS IS | Six deterministic dimensions and an explicit quality floor replace keyword-order selection. | Policy tests and readable score trace. |
| Read allocation | CHANGED vs AS IS | Required-family coverage is allocated first, then quality and bounded diversity. | Allocation and stress tests. |
| Read failure | CHANGED vs AS IS | Failed reads are failed operations; metadata-only material is not treated as readable. | Integration tests and live trace. |
| Read-format capability | NEW | The read plan does not spend a slot on an obvious unsupported PDF; unexpected binary responses fail safely into metadata-only evidence. | Reader capability tests and final live trace. |
| Found material provenance | NEW | `discoveryTrace` stores resolvable handles without copying rich snippets or full trace objects. | Handle-resolution tests. |
| Signal extraction | NOT THIS SLICE | Future provider call receives an extraction dossier, never the full RadarRun. | Slice `2.17.4.7`. |
| Signal scoring | NOT THIS SLICE | Future scoring receives a bounded signal dossier and direct budget proof. | Slice `2.17.4.7.1`. |
| Candidate assembly and ranking | NOT THIS SLICE | Future assembly receives bounded approved-signal projections. | Slices `2.17.4.8` and `2.17.4.8.1`. |
| Cross-run search memory | NOT THIS SLICE | Reuse of discovered results is owned by a separate durable memory policy. | Slice `2.17.4.6.6`. |

## 4. Search Result Triage Contract

The deterministic triage chain is:

`rawResults -> normalized candidates -> duplicate groups -> dimension scores -> read plan -> read outcomes`.

Each raw result receives exactly one terminal decision:

- `selected`;
- `rejected`;
- `duplicate`;
- `invalid`;
- `deferredByBudget`.

No result may disappear because of list slicing, duplicate replacement, provider
order, or an exception.

### 4.1 Bounded candidate projection

The triage projection contains only:

- URL, capped at 2048 characters;
- title, capped at 300 characters;
- snippet, capped at 1200 characters;
- query, intent, family, and evidence handles;
- deterministic score dimensions and short reason codes;
- diagnostic explanation, capped at 320 characters.

Full page bodies, complete search responses, source ledgers, previous operation
envelopes, and nested budgets are forbidden.

### 4.2 Normalization and duplicates

Canonical URL normalization removes only known tracking parameters: `utm_*`,
`gclid`, `fbclid`, and `ref`. Other query parameters remain because they may identify
different documents or views.

Duplicate groups are stable under input permutation. They may be formed by canonical
URL, tracking variants, or normalized title/snippet fingerprints. The representative
is chosen by deterministic quality and lexical tie-break rules, never by provider
position. A group preserves the union of all discovery handles.

### 4.3 Quality dimensions

Each representative receives scores from 0 to 100 for:

- relevance;
- evidence fit;
- project fit;
- source-quality signals;
- novelty;
- noise risk.

The ordering score is:

`0.30 relevance + 0.20 evidence fit + 0.20 project fit + 0.15 source quality + 0.15 novelty - noise penalty up to 30`.

The quality floor is 45. Unknown domains are neutral. Vendor sources are not rejected
only for being vendors; pricing and generic promotional noise are penalized through
observable content signals.

### 4.4 Coverage-aware reading

The read allocator first gives every executable required family the best available
representative above the quality floor. Remaining capacity is filled by score.
Within a score difference of 10, a new evidence type and then a new domain are
preferred. Diversity never promotes a candidate below the quality floor.

Read caps remain `1/2/4` for `smoke/standard/full`. Any required direction that could
not receive a read is listed in `readCoverageGaps` with a stable reason.

## 5. Read Outcome and Material Contract

A successful URL read creates a normal readable `FoundMaterial`. A failed read:

- produces a failed URL-read operation;
- preserves the discovery metadata in a `metadataOnly` material;
- records a structured read outcome and warning;
- does not count as a successful readable material.

If every produced material is metadata-only, RadarRun status is no better than
`partial`.

`FoundMaterial.discoveryTrace` stores IDs and handles only: raw-result IDs, query IDs,
intent IDs, families, evidence types, duplicate-group ID, decision reason, and read
outcome. It does not copy snippets, page bodies, or the full `searchTriage` report.

## 6. Provider Input Budget Boundary

`openWebQuery` is the first upstream provider-heavy operation governed by a direct
budget contract.

Per call:

| Measure | Limit |
| --- | ---: |
| Query text | 1000 characters |
| Provider input | 1500 characters |
| Serialized messages | 4000 characters |
| Approximate input tokens | 1000 |

Per RadarRun:

| Mode | Input characters | Approximate input tokens | Max results per query |
| --- | ---: | ---: | ---: |
| smoke | 4000 | 1000 | 3 |
| standard | 12000 | 3000 | 5 |
| full | 20000 | 5000 | 8 |

The effective result count cannot exceed `OPENROUTER_WEB_SEARCH_MAX_RESULTS`.
Before the provider call, the direct input gate checks the current query and run
totals. After message construction, a provider-neutral message guard measures the
actual serialized messages. An over-limit operation is not sent and records
`provider-input-over-budget` plus a structured incident.

The operation trace contains the actual `providerInput`, `payloadBudget`,
`inputStats`, `payloadStats`, `messageCharCount`, model selection, and provider usage
when returned. Nested metadata from an older artifact never counts as proof.

Provider-reported prompt tokens can exceed the local message estimate because the
OpenRouter web-search tool adds its own retrieval context. This value is preserved as
usage/cost telemetry, but it is not confused with the Glavred-controlled provider
input. Production limits for provider-owned search cost and reuse belong to Slice
`2.17.4.6.6`.

## 7. Future Provider Context Rule

Every future upstream provider-heavy stage must declare before implementation:

1. a typed rich input artifact;
2. an operation-specific dossier/input owner;
3. `mustHave`, `shouldHave`, `diagnosticOnly`, and `neverSendToProvider` fields;
4. a direct current-call budget profile;
5. a final serialized-message guard;
6. handles back to persisted artifacts;
7. a stress test proving bounded growth;
8. a trace-safe outcome and fallback/incident policy.

Architecture smoke rejects a new operation that does not satisfy this inventory or
carry an explicit tracker-backed debt exception.

## 8. Trace Contract

RadarRun keeps existing fields and adds `searchTriage`:

- policy version;
- normalized candidates and dimension scores;
- duplicate groups;
- read plan and terminal decisions;
- required-family coverage and gaps;
- read outcomes;
- terminal decision counts.

Existing `rawResults`, `selectedForRead`, and `rejectedBeforeRead` remain compatible.
Old runs without `searchTriage` remain readable in the UI.

## 9. Success Criteria

- Every raw result has one terminal decision.
- Selection and duplicate representatives are invariant under provider result order.
- No duplicate group schedules more than one URL read.
- Required-family coverage is maximized inside the read cap and gaps are explicit.
- Known generic-news and pricing noise does not displace a suitable alternative.
- Failed reads remain failed and metadata-only results are not counted as readable.
- One hundred raw results cannot grow provider calls, provider messages, or read count
  beyond the active profile.
- `openWebQuery` has direct input and final-message budget proof.
- RadarRun still creates no `SourceSignal`, `PostCandidate`, plan slot, or DraftRun.
- Recorded and comparable live proof show no quality regression relative to the
  pre-change industrial-AI baseline.

## 10. Implementation Status

- Slice `2.17.4.6.2`: triage v2, selective reading, read-outcome trace, upstream budget
  boundary, UI trace, recorded/live proof. `IMPLEMENTED`.
- Signal extraction, signal scoring, candidate assembly, candidate ranking, and
  cross-run search memory: `NOT THIS SLICE`.

## 11. Implementation Proof

The final live proof on 2026-07-13 returned 52 raw results and exactly 52 terminal
decisions: 2 selected, 7 rejected, 17 duplicate, and 26 deferred by budget. It built
35 stable duplicate groups and produced two readable materials from two domains with
no read warnings, accepted noise, or metadata-only output.

All three `openWebQuery` operations were directly budgeted. Serialized messages used
1,185 characters in total, local approximate input was 297 tokens, and no budget
incident was recorded. The benchmark remained `warning` only because the existing
three-query campaign budget skipped required `limitationCritique`; required coverage
was not lost by triage.

Trace-safe pre/post evidence is committed in
`docs/evidence/radar-runs/2.17.4.6.2/COMPARISON.md` and `comparison.json`.
