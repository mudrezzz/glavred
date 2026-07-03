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
- the backend external runner builds a deterministic search campaign from radar
  settings, source handles, project language, and budget mode;
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

Every future upstream run should make the handoff readable:

- what sources were eligible;
- what search plan and query intents were built;
- what operations ran or were skipped by budget;
- what raw search results were returned;
- which results were selected for URL reading and which were rejected before reading;
- what material was found;
- which materials became signals and which were rejected as noise;
- how signal scoring dimensions were decided;
- why a topic/fabula candidate was accepted or rejected;
- what human correction or approval changed.

## Benchmark And Trace Inspection Plan

The first stable diagnostic scenario should be a single golden radar, not a broad
benchmark corpus. The planned golden scenario is
`benchmark-industrial-ai-maintenance-cases` for `Опытный цех «Сборочная»`, bound to
the industrial AI cases radar. It should run in recorded-fixture mode without network
access and verify the search campaign against expected query intents, evidence types,
source diversity, selected reads, found materials, unacceptable noise, and the rule
that no `SourceSignal`, `PostCandidate`, plan slot, or DraftRun is created.

The compact `Сигналы -> Радары -> Трасса запуска` panel remains the operational
preview. A dedicated trace page should be added next so a single `RadarRun` can be
inspected like DraftRun/AiRun traces: search plan, source handles, operation timeline,
raw results, selected/rejected read decisions, found materials, warnings, errors, and
benchmark verdict when available.

## Implementation Slices

- `2.17.4.5`: Source Registry and Radar Run Contract. Done: deterministic local run
  only, no provider-backed search.
- `2.17.4.6`: External Search Radar Runner v1. Done: deterministic search campaign,
  provider-backed web search when configured, selective URL reads, triage trace, and
  normalized found material.
- `2.17.4.6.1`: Search Intent Planner and Campaign Trace.
- `2.17.4.6.1.1`: Golden Radar Benchmark Scenario.
- `2.17.4.6.1.2`: RadarRun Trace Page.
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
