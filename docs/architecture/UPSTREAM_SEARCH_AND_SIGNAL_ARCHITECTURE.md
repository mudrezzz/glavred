# Upstream Search and Signal Architecture

Current as of Slice 2.17.4.7.1.1.

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
- `searchPlan`: filter-derived requirement profile, strategy, language, intents,
  query families, evidence types, requirement handles, source strategy, uncovered
  required requirements, and budget limits;
- planned and executed coverage: `plannedCoverage`, `executedCoverage`, and
  `skippedRequiredCoverage`, not only the existence of good planned intents;
- execution trace: query operations, raw results, selected URL reads, rejected-before-
  read results, warnings, and errors;
- output boundary: retrieval creates `FoundMaterial`; dedicated extraction may create
  unreviewed `SourceSignal` candidates, but no upstream stage creates `PostCandidate`,
  plan slots, or `DraftRun`;
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
- `SourceSignal` starts as an evidence-backed extraction candidate. It answers:
  "what did we find, which exact fragments prove it, and what uncertainty or
  limitation remains?" Project usefulness and human review are separate stages.
- `SourceSignal` does not own topic, fabula, target audience, value, goal, platform,
  format, or publication channel. Those belong to candidate assembly and planning.
- `BlogProject.language` owns the editorial language. `RadarDefinition` separately
  owns source-language eligibility. Search queries, source text, and editorial signal
  fields are not assumed to share one language.
- `PostCandidate` is an editorial composition: `Signal x Topic x Fabula`, with
  audience value, thesis, evidence summary, risks, and ranking rationale.
- React feature code renders and edits upstream read models. It must not own provider
  search, signal extraction, scoring, or candidate assembly policy.
- Provider-backed search and extraction must live behind application/infrastructure
  adapters. Domain contracts stay provider-free.

## Core Contracts

These contracts are the upstream boundary. Slices 2.17.4.6-2.17.4.7.1 implement the
provider-backed retrieval, extraction, utility scoring, and review pass: project-scoped `SourceRegistry`,
`RadarRun`, typed search plan, OpenRouter web-search operations, selective URL reads,
raw result triage, normalized `FoundMaterial`, bounded evidence fragments and
candidate `SourceSignal`, bounded project utility reports, and human review history.
Candidate assembly v2 remains a later slice.

| Contract | Owns | Does Not Own |
| --- | --- | --- |
| `SourceHandle` | Project-owned source descriptor: type, title, locator, status, notes. | Search execution, scoring, post idea selection. |
| `SourceRegistry` | The set of internal and external source handles available to a project. | Cross-project sources or global author memory. |
| `RadarLanguageContext` | Canonical editorial language, source-language policy, actual query languages, allowed source languages, unknown-language rule, and legacy fallback reason. | Full project metadata or translation of source evidence. |
| `RadarSearchRequirementProfile` | Bounded mapping of every enabled radar filter to required, optional, exclusion, tension, or explicit scoring-only search applicability. | Provider calls, utility verdicts, full workspace, publications, or fabulas. |
| `RadarRun` | One execution attempt for a radar: status, budget, operations, found material ids, errors. | Final signal approval or post candidate approval. |
| `RadarRunOperation` | One read/search/import operation inside a run. | Domain scoring or candidate ranking. |
| `FoundMaterial` | Retrieved material with source/run provenance, title, URL or source ref, snippet/summary, bounded hashed fragments, capturedAt, warnings. | Topic/fabula assignment or approval. |
| `SignalExtractionReport` | Versioned terminal decisions, provider attempts, grounding incidents, budgets, usage and signal ids. | Project usefulness scoring or final post candidate ranking. |
| `SourceSignal` candidate | Evidence-backed extracted observation with uncertainty, reason codes and exact material/fragment handles. | Automatic approval or topic/fabula/audience/value ownership. |
| `SignalUtilityReport` | Dimension-level editorial utility, setting/evidence refs, deterministic recommendation, provider proof and revision. | Human approval, evidence mutation, topic/fabula ownership, or draft quality. |
| `SearchOpportunityCoverageReport` | Requirement execution, full requirement-to-verdict lineage, material/signal/recommendation counts, review-eligible yield, first failure stage and remediation. | Weakening filters or manufacturing positive signals. |
| `SourceSignalReviewEvent` | Authenticated reversible human decision with revision, reason and changed editorial fields. | Automatic recommendation or evidence mutation. |
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
     mode, editorial filters, source-language policy, execution mode, and budget caps.
   - `RadarLanguageContext` assigns an actual language to each bounded query family
     without adding provider operations and records language coverage gaps.
   - `RadarSearchRequirementProfileFactory` maps every enabled filter to an honest
     search role or explicit scoring-only reason. Required requirements are allocated
     before evidence diversity and optional directions within the existing call cap.
   - Every intent/query carries requirement handles. Uncovered required requirements
     remain visible instead of silently weakening the radar.
   - A `RadarRun` records what was attempted, skipped, failed, and found.
   - Runs may be manual, scheduled later, or deficit-driven later. V1 should start
     manual.

3. **Found material**
   - The runner normalizes heterogeneous retrieval output into `FoundMaterial`.
   - Bounded title/snippet/fragments receive a deterministic source-language
     assessment. A confidently detected forbidden language is not read; unknown and
     mixed content remains eligible with a trace warning.
   - Found material remains visible even when weak, duplicate, or failed-filter. It is
     not silently promoted and not silently dropped.

4. **Signal extraction, scoring and review**
   - Implemented extraction turns one or more readable found materials into zero or
     more grounded candidate source signals and gives every material a terminal
     decision.
   - A retry reuses persisted fragments and creates a new extraction revision without
     repeating search or URL reading.
   - Editorial signal fields use `BlogProject.language`; original source title and
     exact evidence quotation remain unchanged. A terminal localization failure emits
     no mixed-language signal.
   - Implemented utility scoring uses a bounded project profile and signal dossier,
     validates setting/evidence refs, and applies a deterministic categorical
     recommendation after provider semantic evaluation.
   - Recommendation never changes the human status. Review actions are authenticated,
     reversible and revision-checked; correction may change only editorial title,
     summary and author comment and then triggers a rescore.
   - After scoring, deterministic opportunity coverage reconstructs the complete
     lineage from radar requirement to utility verdict, counts review-eligible output,
     and identifies the first failed stage for zero-yield runs.

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
- the backend external runner builds a deterministic typed search campaign from a
  bounded projection of enabled radar filters, radar scope, source handles, project
  language, benchmark profile, research depth, and budget mode; full topics, fabulas,
  publisher rules, publications and trace do not enter query construction;
- each external run records `searchPlan`, directly budgeted query operations, bounded
  raw search results, deterministic `searchTriage`, selected URL reads, every terminal
  rejected/duplicate/invalid/deferred decision, read outcomes, and found materials;
- `searchPlan.requirementProfile`, requirement handles on intents/queries, and
  `uncoveredRequiredSearchRequirements` prove whether configured filters influenced
  executable search;
- expanded radar rows keep configuration in an internal settings tab and run
  diagnostics in an internal run-trace tab;
- URL read failures and unsupported binary formats are failed read outcomes and may
  be kept only as `metadataOnly`; they do not count as readable material;
- readable materials now enter backend-owned extraction; accepted results are merged
  into workspace `sourceSignals` as unreviewed candidates with exact evidence refs;
- extraction status is independent from retrieval status, and provider failure can
  produce an explicit failed/not-run extraction without rewriting successful search;
- the retry API reuses persisted fragments, replaces only signals belonging to the
  same run and does not repeat search or reads;
- extraction/scoring retries rebuild `searchOpportunityCoverage v2` and benchmark
  status from stored artifacts without repeating search or URL reads;
- query lineage (`discoveredRequirementIds`) is distinct from semantic evidence fit
  (`supportedRequirementIds`); only supported evidence advances requirement delivery
  through read, fragment, signal and optional corroboration stages;
- source reliability uses one backend-owned assessment with independent ownership and
  claim-support axes, so first-party/vendor evidence cannot conflict with the
  source-credibility criterion or become independent merely through provider wording;
- `createPostCandidates` currently does approved-signal x topic/fabula pairing and
  keeps the first three candidates;
- some compatibility fields such as `suggestedTopicId` and `suggestedFabulaId` may
  remain on `SourceSignal`, but UI and new services must not treat them as ownership.

Until Slice 2.17.4.8 replaces candidate assembly, blind pairing is legacy behavior and
must be kept working only as a fallback. Running a radar may create only candidate
`SourceSignal` through extraction; it must not create `PostCandidate`, plan slots or
DraftRuns.

## Trace Requirements

The complete RadarRun trace contract lives in
`docs/architecture/RADAR_RUN_PIPELINE_AS_IS.md`. At the broader upstream level, every
future upstream run should make the handoff readable:

- what sources were eligible;
- how every enabled radar filter became a search requirement, exclusion, tension
  direction, or explicit scoring-only decision;
- what search plan, query families, query intents, evidence types, and source
  strategy were built;
- what query intents were skipped and why;
- what operations ran or were skipped by budget;
- what raw search results were returned;
- which results were selected for URL reading and which were rejected before reading;
- what material was found;
- which exact fragments were retained;
- which materials became signals and which received insufficient, duplicate,
  corroborating, contradiction, noise or extraction-failed decisions;
- which provider attempt was accepted, what grounding incidents were rejected, and
  whether direct input/message budgets were respected;
- how signal scoring dimensions were decided;
- which requirements stopped at planned/query/result/read/material/signal/
  corroboration, how many signals were review-eligible, and which exact reason
  prevented delivery;
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
unacceptable noise, categorical utility distribution, useful-yield behavior, and the
rule that no `PostCandidate`, plan slot, or DraftRun is created.

Run the backend benchmark regression with:

```powershell
python -m pytest backend/tests/test_upstream_golden_radar_benchmark.py
```

Live provider-backed runs for the same industrial AI radar are evaluated with the
same scenario expectations, but not by exact URL matching. The live evaluator writes
`run.benchmarkReport` when the project/radar match the golden scenario. Detailed
planned/executed coverage rules live in the dedicated RadarRun AS IS contract. The
status vocabulary is:

The accepted evidence-delivery and source-posture proof for Slice
`2.17.4.7.1.1.1` is RadarRun
`radar-run-ai-pattern-radar-industrial-cases-4`. It preserves the three-query and
two-read limits, resolves the complete requirement-to-signal lineage, distinguishes
the first-party implementation case from the independent benchmark candidate, and
keeps missing same-claim corroboration explicit. The trace-safe report and
authenticated screenshots live in
`docs/evidence/radar-runs/2.17.4.7.1.1.1/`.

Backend ownership after Slice `2.17.4.6.0.12` is intentionally split: the external
run service orchestrates the campaign, `OpenWebQueryOperationRunner` owns one
provider-backed web query operation, `RadarRunBenchmarkReporter` owns scenario
matching and report attachment, and benchmark evaluation delegates status,
expectations, coverage, and trace/provider-health rules to separate policy classes.
After Slice `2.17.4.6.2`, normalization, duplicate grouping, quality assessment, read
allocation, URL-read execution, payload construction, and upstream budget policy also
have separate application owners. The provider-neutral final-message guard lives in
`backend.app.shared.llm_operations`; upstream does not import DraftRun budget runtime.

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

Inspect a saved extraction run with:

```powershell
python scripts/analyze_radar_signal_extraction.py --project-id <project-id> --run-id <run-id> --format markdown
```

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
- `2.17.4.6.2`: Search Result Triage v2 and Selective Reading. Done: bounded
  normalization, stable duplicate groups, six-dimensional deterministic assessment,
  coverage-aware `1/2/4` read plans, complete terminal decisions, honest read
  outcomes, `metadataOnly` fallback, `discoveryTrace`, upstream provider-input and
  final-message budgets, readable trace UI, recorded tests, and pre/post live proof.
- `2.17.4.6.3`: Source Strategy Adapters and Domain-Aware Search.
- `2.17.4.6.4`: LLM-Assisted Query Expansion and Search Critic.
- `2.17.4.6.5`: Radar Search Evaluation Harness and Benchmark Corpus.
- `2.17.4.6.6`: Search Memory, Refresh Policy, and Production Controls.
- `2.17.4.7`: FoundMaterial to SourceSignal Extraction. Done: bounded evidence
  fragments, extraction dossier, direct budgets, final-message guard,
  primary/repair/backup recovery, strict grounding, terminal material decisions,
  revision retry without retrieval, trace/UI, recorded benchmark and live proof.
- `2.17.4.7.0.2`: Radar Language Policy and Signal Evidence Presentation. Done:
  canonical editorial-language handoff, three source-language policies, bounded
  query-language allocation, deterministic source eligibility, extraction
  localization validation, original evidence links, trace links, and explicitly
  unscored candidate presentation.
- `2.17.4.7.1`: Signal Editorial Scoring, Explainability and Relationship Integrity.
  Done: bounded project profile/dossier, batch provider recovery and budgets,
  mode-aware radar/project criteria, type-aware system quality checks, categorical
  recommendation, human-readable evidence resolution, non-destructive canonical
  signal relationships, reversible authenticated review and legacy integrity
  separation.
- `2.17.4.7.1.1`: Search-to-Filter Alignment and Useful-Signal Yield Benchmark.
  Done: bounded filter-to-requirement projection, required-first deterministic query
  allocation, requirement lineage through read/material/signal/verdict, explicit
  uncovered requirements, useful-yield and first-failure diagnostics, post-scoring
  benchmark evaluation, retry-safe recomputation, trace UI, stress and live proof.
- `2.17.4.8`: Signal x Topic x Fabula Candidate Assembly v2.
- `2.17.4.9`: Signal Review and Candidate Workbench UX.

Only after this upstream v1 is demonstrable should multi-target planning and
multi-platform DraftRun work resume.
