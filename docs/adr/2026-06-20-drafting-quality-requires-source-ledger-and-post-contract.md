# ADR: Drafting quality requires source ledger and post contract

## Status

Accepted

## Context

The queued `DraftRun` architecture already separates context, rule pack, material
planning, strategy, draft candidates, and trace inspection. That is the right
execution model, but the next quality risk is not only "add validators".

High-quality Glavred drafting needs two stronger boundaries before a validator and
revision loop can be meaningful:

- a source ledger that says which claims are grounded, allowed, risky, or forbidden;
- a post contract that locks the approved editorial intent before prose is written.

Without those artifacts, validators can only judge the shape of text after the fact.
They cannot reliably detect when the draft overstates a weak source, invents a claim,
breaks the approved fabula, or silently ignores the author's publishing rules.

The user-facing workflow remains HITL-separated:

`Signals -> Candidates -> Plan slot approval -> Editorial work item -> Fabula approval -> DraftRun -> Draft -> Visual`

The drafting agent must respect those gates instead of trying to re-decide the whole
post from scratch.

## Decision

Glavred drafting quality will be built as typed DraftRun artifacts, not as one larger
prompt and not as a validator-only loop.

The target drafting pipeline is:

1. `DraftRunContext`: selected work item, slot, candidate, signal, topic, fabula,
   publisher rules, author-position evidence, and approved brief.
2. `RuleRegistrySnapshot`: selected machine-readable rules with ids, scope,
   priority, severity, observable criteria, validator type, examples, and repair
   policy.
3. `SourceLedger`: atomic source/candidate/brief claims, provenance, confidence,
   allowed use, risks, forbidden inferences, and author corrections.
4. `FeasibilityGate`: `feasible`, `feasible_with_constraints`, `needs_research`,
   `needs_human_decision`, or `infeasible`.
5. `PostContract`: locked thesis, audience value, CTA, allowed claims, forbidden
   moves, platform constraints, and fabula obligations.
6. `RulePack`: compact execution rules derived from the registry, contract, source
   ledger, topic, fabula, and publisher constraints.
7. `MaterialPlan`: what evidence is available, missing, risky, and how the draft will
   stay grounded.
8. `RhetoricalPlans` / `DraftStrategy`: several possible editorial routes for the same
   contract.
9. `DraftCandidates`: several generated texts with rationale, used evidence, risks,
   weaknesses, and child `AiRun` ids.
10. `DeterministicLinter`: fast hard-rule checks before expensive LLM judging.
11. `ValidatorReports`: source grounding, publisher/voice, topic/fabula, coherence,
   compression, and audience-value checks.
12. `PairwiseRanking`: compare candidates and keep a traceable scorecard.
13. `DirectedRevision`: one targeted repair of the selected candidate against concrete
   findings while preserving the post contract.
14. `RegressionReport`: re-run checks after the revision and keep the best attempt if
   the revision made the text worse.
15. `HumanDecision`: editor approval, manual edits, unresolved risks, and learning
   signals for later rule and prompt improvement.

Future drafting slices must advance this chain in order unless a roadmap entry
explicitly explains why a later stage can be implemented safely earlier.

## Consequences

- The next backend drafting slice is `Source Ledger Foundation`, not the validator
  loop.
- A validator/revision loop must consume `SourceLedger` and `PostContract`; it must not
  infer claim provenance only from the final draft text.
- `PostBrief` remains the approved fabula artifact. It must not absorb source ledger,
  slot, candidate, topic, fabula, or rule-registry fields.
- `DraftRunStep.artifactPayload` remains the durable inspection surface for these
  artifacts. New artifacts should not require SQL columns unless there is a clear
  persistence/query need.
- API handlers and Celery task bodies remain thin. Application services own stage
  orchestration, domain modules define provider-free DTOs, and infrastructure owns
  OpenRouter/queue/persistence adapters.
- The main editor UI should show compact status, chosen draft, rationale, risks, and
  claim provenance. Full machine detail belongs in `/ai-runs` and DraftRun trace.
- `langgraph-document-ai-platform` or a LangGraph-style runner can be introduced only
  after these typed contracts are stable; it should orchestrate the pipeline, not hide
  the business rules.

## Alternatives considered

- **Add validators immediately after multi-candidate generation.** Rejected because
  validators without a source ledger and post contract would not know which claims and
  invariants are actually allowed.
- **Use a larger prompt that includes every rule, source, topic, fabula, and brief
  field.** Rejected because it creates an opaque, brittle request and makes quality
  failures hard to diagnose.
- **Move all source ledger work upstream into Signals or Candidates before drafting.**
  Deferred. Eventually source ledger data should start earlier, but the next useful
  slice can create a DraftRun-local ledger from the approved post context.
- **Expose every machine artifact in the main editorial workbench.** Rejected. The
  main workbench needs a compact editorial report; the full trace belongs to the debug
  surface.
