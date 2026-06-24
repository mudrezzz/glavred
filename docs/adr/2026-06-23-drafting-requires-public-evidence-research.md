# ADR: Drafting requires public evidence research before prose

## Status

Accepted

## Context

Glavred's queued `DraftRun` already separates context, source ledger, feasibility,
post contract, rule registry, material plan, rhetorical plans, draft candidates, and
trace inspection.

That structure prevents one large opaque prompt, but the current path can still produce
dry or over-internal drafts. The approved fabula may contain `sources`: URLs, search
notes, or external proof hints the author wants the drafting agent to use. Treating
those sources as plain text inside a prompt misses the editorial value: the agent
should inspect public material, reconcile it with the signal and author position, and
then decide what can safely support the post.

Good Glavred drafting is not `brief -> draft`. It is an editorial research loop:

- understand the approved fabula and signal;
- identify what claims need public support;
- search or read public sources;
- extract claims with provenance and allowed use;
- compare public evidence with the author's position;
- update the source ledger;
- only then write candidates.

## Decision

Glavred drafting will include an explicit public-evidence research layer before
validators and before final prose quality loops.

The target queued drafting chain becomes:

1. `DraftRunContext`
2. `SourceIntent`
3. seed `SourceLedger`
4. `ResearchPlan`
5. `PublicResearch`
6. `EvidenceExtraction`
7. enriched `SourceLedger`
8. `EvidenceSynthesis`
9. `FeasibilityGate`
10. `PostContract`
11. `RuleRegistrySnapshot` / `RulePack`
12. `MaterialPlan`
13. `DraftStrategy`
14. `RhetoricalPlans`
15. `DraftCandidates`
16. `DeterministicLinter`
17. `ValidatorReports`
18. `PairwiseRanking`
19. `DirectedRevision`
20. `RegressionReport`
21. `HumanDecision`

The `sources` field in the approved `PostBrief` is not just prompt text. It becomes
`SourceIntent`: URL seeds, named sources, human-language research requests, required
proof, exclusions, and framing-only sources. A plain request like "нужно мнение
лидеров мнений по этой теме" must become a research plan before any search adapter
sees it; it must not be sent directly as raw keywords.

Slice 2.12.3.1 clarifies where those sources start. `Fabula.researchStrategy` is the
editorial-model default policy: manual mode copies configured instructions into a
new work brief, and auto mode creates readable research prompts from the current
topic, fabula, candidate, signal, and proof requirements. `PostBrief.sources` remains
the approved runtime input and may override the fabula default for one post.

Public evidence enters drafting through typed artifacts:

- `ResearchPlan`: what to check, read, search, or verify.
- `PublicEvidenceItem`: extracted external claim, source, confidence, and allowed use.
- `EvidenceSynthesis`: what public material confirms, weakens, contradicts, or cannot
  support.
- enriched `SourceLedger`: internal and public claims in one provenance-aware ledger.

Slice 2.12.4 implements the first retrieval foundation. Exact URLs are read through
an infrastructure URL reader and become `PublicEvidenceItem` records in the
`publicEvidence` DraftRun step. Slice 2.12.4.1 adds an opt-in OpenRouter web-search
adapter: when `OPENROUTER_WEB_TOOLS_ENABLED=true`, general search and verification
tasks call the `openrouter:web_search` server tool, create child `AiRun` audit
records, and turn returned citations into `PublicEvidenceItem` candidates. Disabled,
unconfigured, or failed search attempts remain explicit trace records and must not be
treated as proof.

Slice 2.12.4.2 adds the query and relevance repair required before ledger merge:
search adapters receive a `builtQuery` created from the human research instruction and
post context, not a technical source-target id. Returned citations pass a conservative
deterministic relevance guard before they can become `PublicEvidenceItem` candidates.
Rejected citations stay visible in trace as `search-result-drift` and must not be
merged as proof.

External web/retrieval adapters belong in infrastructure. Application services own the
research orchestration and evidence reconciliation. Domain DTOs remain provider-free.

## Consequences

- Source intent, research planning, exact-URL public evidence retrieval, optional
  OpenRouter web search, relevance filtering, source-ledger merge, and evidence
  synthesis are now implemented public-evidence layers. Validator work must consume
  those enriched artifacts, not raw search snippets.
- `FeasibilityGate`, `PostContract`, validators, ranking, and directed revision must
  consume the enriched ledger when public evidence exists.
- The main editor UI can stay compact. Full research artifacts belong in `/ai-runs`
  DraftRun trace.
- Early slices may use deterministic or manually supplied URL placeholders, but they
  must preserve the real artifact boundaries so live search/read adapters can replace
  placeholders later.
- Public research must not silently invent proof. Every usable public claim needs
  source provenance, confidence, allowed-use policy, and forbidden-inference handling.
- Material planning must not silently ignore enriched evidence. If `SourceLedger`
  contains usable claims, `MaterialPlan` must select them or record concrete rejection
  reasons before fallback is allowed.

## Alternatives considered

- **Put sources into the draft prompt.** Rejected. This keeps research opaque and makes
  it unclear which public fact was read, extracted, or allowed.
- **Wait until validators to check evidence.** Rejected. Validators cannot rescue a
  draft that was written before the agent had public grounding.
- **Move all public research into Signals.** Deferred. Signals should eventually carry
  stronger source evidence, but approved fabulas can still request extra public proof
  at drafting time.
- **Make the main editor show every research artifact.** Rejected. The workbench needs
  a compact report; full inspection belongs in `/ai-runs`.
