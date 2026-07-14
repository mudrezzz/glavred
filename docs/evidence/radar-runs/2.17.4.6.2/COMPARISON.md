# RadarRun 2.17.4.6.2 Live Comparison

This report contains trace-safe evidence only. Full live payloads stay in ignored
`var/evidence/radar-triage-2.17.4.6.2/` and are not committed.

## Runs

| Proof | Started UTC | Completed UTC | Runtime |
| --- | --- | --- | ---: |
| Before triage v2 | 2026-07-13 16:46:20 | 2026-07-13 16:49:39 | about 199 s |
| Final after triage v2 | 2026-07-13 17:36:18 | 2026-07-13 17:39:26 | about 188 s |

Both calls used the same golden project/radar workspace. The ephemeral scenario starts
with no stored run history, so both payloads use the compatible id
`radar-run-ai-pattern-radar-industrial-cases-1`; timestamps and evidence-file names
identify the executions.

## Result

| Metric | Before | After |
| --- | ---: | ---: |
| Raw results | 55 | 52 |
| Explicit terminal decisions | not available | 52 of 52 |
| Duplicate groups | not available | 35 |
| Selected reads | 2 | 2 |
| Readable materials without warnings | 1 | 2 |
| Accepted metadata-only materials | 1 incorrectly treated as found | 0 |
| Distinct selected domains | 2 | 2 |
| Accepted known noise | 0 | 0 |
| Trace complete | yes | yes |
| Benchmark verdict | `warning` | `warning` |

The pre-change run selected a DOI result whose page returned HTTP 403. The old path
kept it as a normal `found` material with `url-read-failed` and `search-result-only`
warnings. The final run selected two readable HTML cases: EmbedCrest industrial
predictive maintenance and Andersen asset reliability. Both have resolvable discovery
handles and no read warnings.

The benchmark remains `warning` for the existing campaign-budget reason: only three
query families execute, while required `limitationCritique` is skipped by
`maxExternalQueries`. Triage v2 did not worsen planned or executed coverage.

## Budget Proof

- Three `openWebQuery` operations were directly budgeted.
- Serialized messages totalled 1,185 characters; each operation used 395 characters.
- Local approximate input was 297 tokens in total.
- There were no `payloadTooLarge`, `contextOverBudget`, missing-direct-budget, or
  nested-budget incidents.
- OpenRouter reported 76,112 total tokens and 11 internal web-search requests. This
  includes provider-owned web-tool context, not the 1,185 characters sent by Glavred.
  The local context boundary is proven; provider-side search cost needs separate
  production controls in Slice `2.17.4.6.6`.

## Verdict

The slice improved both correctness and inspectability. Selection is stable and
coverage-aware, every raw result has one decision, duplicates remain traceable, read
failures can no longer masquerade as readable materials, and provider input is
directly bounded. The remaining `warning` is campaign coverage debt, not a triage
regression.
