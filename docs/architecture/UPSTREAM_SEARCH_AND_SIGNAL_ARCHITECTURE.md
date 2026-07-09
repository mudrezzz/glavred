# Upstream Search and Signal Architecture

Current as of Slice 2.17.4.6.

## Purpose

Glavred already has a mature downstream drafting loop: an approved post concept can
move through plan, workbench, DraftRun, validation, revision, HITL versions, and
learning notes. The weaker part is upstream: how the product finds material worth
writing about before a post candidate exists.

This document defines the upstream spine:

`SourceRegistry -> RadarRun -> FoundMaterial -> SourceSignal -> SignalScore -> PostCandidate -> Plan -> DraftRun`

The goal is not to replace the current `Signals` UI in one step. The goal is to make
the next implementation slices decision-complete: raw retrieval, signal review, and
editorial candidate assembly must have separate ownership and trace.

The concrete RadarRun runtime pipeline is maintained separately in
`docs/architecture/RADAR_RUN_PIPELINE_AS_IS.md` with a quick-view PDF at
`docs/architecture/RADAR_RUN_PIPELINE_AS_IS.pdf`. Use that document for step order,
trace proof, benchmark verdict, and RadarRun-specific DoD. Use this document for the
broader upstream boundary from retrieval through signal review and candidate assembly.

## How This AS IS Contract Feeds DoD

Upstream slices must treat this document as a requirement source before
implementation and as a validator at completion. RadarRun/search slices must also use
`RADAR_RUN_PIPELINE_AS_IS.md` as the concrete pipeline contract. A DoD for search,
radar, signal extraction, scoring, or candidate assembly must explicitly say which AS
IS rules are preserved, changed, or superseded.

Minimum DoD inputs from this document and the dedicated RadarRun AS IS:

- source eligibility: which `SourceHandle` records were searchable, readable-only,
  paused, or skipped;
- `searchPlan`: strategy, language, intents, query families, evidence types, source
  strategy, and budget limits;
- planned and executed coverage: `plannedCoverage`, `executedCoverage`, and
  `skippedRequiredCoverage`, not only the existence of good planned intents;
- execution trace: query operations, raw results, selected URL reads, rejected-before-
  read results, warnings, and errors;
- output boundary: `FoundMaterial` can be created by a radar run, but `SourceSignal`,
  `PostCandidate`, plan slots, and `DraftRun` must not be created by upstream search;
- benchmark verdict: when a matching scenario exists, `benchmarkReport` must explain
  whether the result is `passed`, `warning`, `failed`, or `inconclusive`.

The RadarRun AS IS trace contract is currently stricter than older DraftRun provider
input tracing because it already separates planned coverage from executed coverage.
That difference is intentional and should be used as a template for later pipeline DoD
work, not watered down in new radar slices.

## Boundary Rules

- `DraftRun` is downstream. It may enrich evidence for an approved brief, but it is
  not the first place where Glavred discovers what to write about.
- `FoundMaterial` is retrieval output. It can be a search result, URL read, archive
  item, imported note, document excerpt, previous post, or manual research item.
- `SourceSignal` is reviewed material. It answers: "what did we find, why might it
  matter, what evidence/provenance does it carry, and what risks are visible?"
- `SourceSignal` does not own topic, fabula, target audience, value, goal, platform,
  format, or publication channel. Those belong to candidate assembly and planning.
- `PostCandidate` is an editorial composition: `Signal x Topic x Fabula`, with
  audience value, thesis, evidence summary, risks, and ranking rationale.
- React feature code renders and edits upstream read models. It must not own provider
  search, signal extraction, scoring, or candidate assembly policy.
- Provider-backed search and extraction must live behind application/infrastructure
  adapters. Domain contracts stay provider-free.

## Core Contracts

These contracts are the upstream boundary. Slice 2.17.4.6 implements the first
provider-backed retrieval pass: project-scoped `SourceRegistry`, `RadarRun`, typed
search plan, OpenRouter web-search operations, selective URL reads, raw result
triage, and normalized `FoundMaterial`. Signal extraction, scoring, and candidate
assembly v2 remain later slices.

| Contract | Owns | Does Not Own |
| --- | --- | --- |
| `SourceHandle` | Project-owned source descriptor: type, title, locator, status, notes. | Search execution, scoring, post idea selection. |
| `SourceRegistry` | The set of internal and external source handles available to a project. | Cross-project sources or global author memory. |
| `RadarRun` | One execution attempt for a radar: status, budget, operations, found material ids, errors. | Final signal approval or post candidate approval. |
| `RadarRunOperation` | One read/search/import operation inside a run. | Domain scoring or candidate ranking. |
| `FoundMaterial` | Retrieved material with source/run provenance, title, URL or source ref, snippet/summary, capturedAt, warnings. | Topic/fabula assignment or approval. |
| `SignalExtractionReport` | Which materials produced signal candidates, which were rejected as noise, and why. | Final post candidate ranking. |
| `SignalScore` | Dimension-level editorial fit: novelty, source credibility, author fit, audience value, positioning fit, topic affinity, evidence strength, risk. | Draft text quality. |
| `CandidateAssemblyReport` | Accepted/rejected `Signal x Topic x Fabula` matches, candidate ranking, rationale, and risks. | DraftRun generation or publication variants. |

## Data Flow

1. **Source registry**
   - Internal handles: author memory, archive/import queue, previous posts, manual
     notes, accepted learning notes.
   - External handles: URL, open-web query, social/profile handle, document/source
     placeholder, future API/RSS/MCP handles.
   - Project isolation is mandatory. A handle belongs to one `BlogProject` workspace
     unless a later explicit sharing model is introduced.

2. **Radar run**
   - A `RadarDefinition` supplies trigger rules, source handles or source discovery
     mode, editorial filters, execution mode, and budget caps.
   - A `RadarRun` records what was attempted, skipped, failed, and found.
   - Runs may be manual, scheduled later, or deficit-driven later. V1 should start
     manual.

3. **Found material**
   - The runner normalizes heterogeneous retrieval output into `FoundMaterial`.
   - Found material remains visible even when weak, duplicate, or failed-filter. It is
     not silently promoted and not silently dropped.

4. **Signal extraction and scoring**
   - Extraction turns one or more found materials into candidate source signals.
   - Scoring explains whether the material is promising for the project.
   - A human or acceptance policy can approve, reject, archive, or correct signals.

5. **Candidate assembly**
   - Candidate assembly evaluates `approved SourceSignal x active Topic x active Fabula`.
   - It should avoid blind Cartesian products as the main behavior.
   - It should explain why a topic/fabula pair works, why another was rejected, and
     what risks remain before planning.

6. **Plan and DraftRun**
   - Approved candidates can fill plan demand and create editorial work items.
   - DraftRun consumes an approved candidate/brief and may perform post-local evidence
     enrichment. It must not be treated as upstream discovery.

## Project Settings Input

- **Author memory** provides internal source material and author-position evidence.
- **Editorial rules** provide author, audience, goals, positioning, style, forbidden
  topics, and validator-ready project constraints. Upstream uses author/audience/
  goals/positioning/forbidden/topic fit; style remains downstream drafting/review.
- **Topics** define territories. Upstream may compute topic affinity, but the raw
  signal does not own the topic.
- **Fabulas** define reusable editorial forms. They are used in candidate assembly,
  not in raw material retrieval.
- **Publication channels** can influence candidate readiness and platform constraints,
  but project audience must still come from editorial rules/post brief, not channel
  metadata.
- **Research depth and execution mode** cap upstream search breadth, number of source
  operations, accepted materials, extracted signals, and candidate count.

## Ownership Map

| Layer | Future module owner | Responsibility |
| --- | --- | --- |
| Domain | `src/domain/upstream-search` and backend peer when needed | Provider-free DTOs, statuses, validation, transition rules. |
| Application | `src/application/upstream*` and backend application services | Run orchestration, signal scoring policy, candidate assembly policy. |
| Infrastructure | OpenRouter search, URL reader, future RSS/social/document adapters | Provider calls, IO, API errors, raw retrieval normalization. |
| UI | `src/features/signals` | Render radar runs, found material, signals, scores, and candidates; collect human decisions. |
| Persistence | Current workspace snapshot first, backend project snapshot later | Store project-scoped upstream artifacts without cross-project leakage. |
| DraftRun | Existing DraftRun pipeline | Downstream generation from approved candidate/brief only. |

## Compatibility With Current Implementation

The current app already has `RadarDefinition`, `SourceSignal`, `PostCandidate`, and
`Signals` tabs. The compatibility gaps are:

- `SourceRegistry`, `RadarRun`, and `FoundMaterial` now exist in the workspace
  snapshot and are visible in `Сигналы -> Радары`;
- `Run radar` first tries the backend external runner and falls back to the local
  deterministic contract run when the backend is unavailable;
- the backend external runner builds a deterministic typed search campaign from
  radar settings, source handles, project language, topic/fabula context, publisher
  rules, benchmark profile, research depth, and budget mode;
- each external run records `searchPlan`, query operations, raw search results,
  pre-read triage, selected URL reads, rejected-before-read results, warnings, and
  normalized found materials;
- expanded radar rows keep configuration in an internal settings tab and run
  diagnostics in an internal run-trace tab;
- URL read failures are kept as `search-result-only` found material with warnings
  when enough search-result metadata exists;
- `sourceSignals` are still seeded/demo-local or manually reviewed compatibility data
  rather than produced by extraction from `FoundMaterial`;
- `createPostCandidates` currently does approved-signal x topic/fabula pairing and
  keeps the first three candidates;
- some compatibility fields such as `suggestedTopicId` and `suggestedFabulaId` may
  remain on `SourceSignal`, but UI and new services must not treat them as ownership.

Until Slice 2.17.4.8 replaces candidate assembly, blind pairing is legacy behavior and
must be kept working only as a fallback. Running a radar in 2.17.4.6 must not create
`SourceSignal`, `PostCandidate`, plan slots, or DraftRuns.

## Trace Requirements

The complete RadarRun trace contract lives in
`docs/architecture/RADAR_RUN_PIPELINE_AS_IS.md`. At the broader upstream level, every
future upstream run should make the handoff readable:

- what sources were eligible;
- what search plan, query families, query intents, evidence types, and source
  strategy were built;
- what query intents were skipped and why;
- what operations ran or were skipped by budget;
- what raw search results were returned;
- which results were selected for URL reading and which were rejected before reading;
- what material was found;
- which materials became signals and which were rejected as noise;
- how signal scoring dimensions were decided;
- why a topic/fabula candidate was accepted or rejected;
- what human correction or approval changed.

## Benchmark And Trace Inspection Plan

The dedicated RadarRun runtime and benchmark contract is maintained in
`docs/architecture/RADAR_RUN_PIPELINE_AS_IS.md`. This section keeps only the broad
upstream summary and command pointers.

The first stable diagnostic scenario is a single golden radar, not a broad benchmark
corpus. `benchmark-industrial-ai-maintenance-cases` is implemented for `Опытный цех
«Сборочная»`, bound to the industrial AI cases radar. It runs in recorded-fixture
mode without network access and verifies the search campaign against expected query
intents, evidence types, source diversity, selected reads, found materials,
unacceptable noise, and the rule that no `SourceSignal`, `PostCandidate`, plan slot,
or DraftRun is created.

Run the backend benchmark regression with:

```powershell
python -m pytest backend/tests/test_upstream_golden_radar_benchmark.py
```

Live provider-backed runs for the same industrial AI radar are evaluated with the
same scenario expectations, but not by exact URL matching. The live evaluator writes
`run.benchmarkReport` when the project/radar match the golden scenario. Detailed
planned/executed coverage rules live in the dedicated RadarRun AS IS contract. The
status vocabulary is:

Backend ownership after Slice `2.17.4.6.0.12` is intentionally split: the external
run service orchestrates the campaign, `OpenWebQueryOperationRunner` owns one
provider-backed web query operation, `RadarRunBenchmarkReporter` owns scenario
matching and report attachment, and benchmark evaluation delegates status,
expectations, coverage, and trace/provider-health rules to separate policy classes.

- `passed`: required search/evidence coverage was actually executed, trace is
  complete, no noise was accepted, and the provider path was usable;
- `warning`: provider was usable and produced material, but there are non-blocking
  coverage or read-quality gaps, including required directions that were planned but
  skipped by the current query budget;
- `failed`: provider was usable, but required coverage/material/diversity checks fail
  or accepted material contains known noise;
- `inconclusive`: provider/runtime state prevents a fair quality verdict, for example
  disabled search, missing provider configuration, rate-limit/network failure, or no
  executed search trace.

The compact `Сигналы -> Радары -> Трасса запуска` panel remains the operational
preview. The dedicated `/radar-runs?runId=<id>` trace page is defined by the RadarRun
AS IS contract and remains a frontend read model over existing workspace snapshots;
it does not add backend tables or provider calls.

## Implementation Slices

- `2.17.4.5`: Source Registry and Radar Run Contract. Done: deterministic local run
  only, no provider-backed search.
- `2.17.4.6`: External Search Radar Runner v1. Done: deterministic search campaign,
  provider-backed web search when configured, selective URL reads, triage trace, and
  normalized found material.
- `2.17.4.6.1`: Search Intent Planner and Campaign Trace. Done: provider-free
  `SearchPlan`, `SearchIntent`, `SearchQuery`, `SearchCampaignTrace`, and
  `SkippedSearchIntent` contracts; deterministic query families for broad
  discovery, case/example, benchmark/paper, OSS/tooling, limitation/critique, and
  freshness; inline RadarRun trace coverage for intents, source strategy, budget
  skips, and the rule that raw material does not own topic/fabula decisions.
- `2.17.4.6.1.1`: Golden Radar Benchmark Scenario. Done: recorded benchmark runner,
  synthetic search/read fixture, report payload, trace completeness checks, source
  diversity checks, duplicate/noise rejection checks, and downstream-leak guard.
- `2.17.4.6.1.2`: RadarRun Trace Page. Done: standalone `/radar-runs?runId=<id>`
  diagnostics page over local/backend portfolio snapshots, compact-card trace link,
  enriched and legacy run compatibility, raw JSON fallback, and passive benchmark
  verdict display when present.
- `2.17.4.6.1.2.1`: Live Radar Golden Evaluation Harness. Done: recorded benchmark
  runner and live radar runs share a reusable evaluator, matching industrial AI live
  runs attach `benchmarkReport`, live verdicts include evaluation mode, provider
  health, coverage, and inconclusive reasons, and `/radar-runs` renders the report.
- `2.17.4.6.1.2.2`: Live Radar Executed Coverage Gate. Done: live verdicts now
  separate planned coverage from executed coverage, expose skipped required coverage,
  and prevent a planned-but-budget-skipped required direction from producing a clean
  `passed` verdict.
- `2.17.4.6.2`: Search Result Triage, Deduplication, and Selective Reading.
- `2.17.4.6.3`: Source Strategy Adapters and Domain-Aware Search.
- `2.17.4.6.4`: LLM-Assisted Query Expansion and Search Critic.
- `2.17.4.6.5`: Radar Search Evaluation Harness and Benchmark Corpus.
- `2.17.4.6.6`: Search Memory, Refresh Policy, and Production Controls.
- `2.17.4.7`: Signal Extraction and Editorial Scoring.
- `2.17.4.8`: Signal x Topic x Fabula Candidate Assembly v2.
- `2.17.4.9`: Signal Review and Candidate Workbench UX.

Only after this upstream v1 is demonstrable should multi-target planning and
multi-platform DraftRun work resume.
