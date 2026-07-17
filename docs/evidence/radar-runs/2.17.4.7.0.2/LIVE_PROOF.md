# Live proof: 2.17.4.7.0.2

## Accepted run

- RadarRun: `radar-run-ai-pattern-radar-industrial-cases-3`
- Project: `project-ai-design-patterns`
- Retrieval: `succeeded`
- Benchmark: `warning` because the existing three-query budget did not execute the required `limitationCritique` family; this is an existing executed-coverage gap, not a language regression.
- Extraction revision: `4`, started from the saved readable materials through the authorized trace UI without repeating search or URL reads.
- Extraction: `succeeded`; one material was signal-producing and one was honestly classified as insufficient.

## Language and evidence proof

- `BlogProject.language=ru` became `editorialLanguage=ru`.
- The radar used `sourceLanguagePolicy=editorialAndEnglish`.
- The three existing search operations remained bounded: `broadDiscovery=ru`, `caseExample=en`, `benchmarkPaper=en`; no extra provider call was added.
- Two readable materials were retained: one confidently Russian and one confidently English.
- The English Siemens source produced three Russian signal candidates with `sourceLanguage=en`, `editorialLanguage=ru`, and `localizationStatus=localized`.
- Original English source title and accepted quotes were preserved. All material and fragment handles resolved. The primary attempt contained one inexact quote and was rejected; the accepted repair has no grounding violation.
- Each signal stayed `reviewStatus=candidate` with no `filterStatus`; the UI displayed `На проверке` and `Редакционная полезность не оценена`.
- The authorized UI opened the original source URL and the `signal-extraction` detail of the correct RadarRun trace.

## Recovery and budget proof

The final accepted retry demonstrated the intended recovery path:

| Attempt | Result | Provider input | Serialized messages | Repair context | Tokens |
|---|---|---:|---:|---:|---:|
| primary | rejected by grounding validation | 10,636 | 11,972 | 0 | 4,172 |
| repair | accepted | 10,973 | 12,337 | 304 | 4,195 |

The unchanged standard limits are 12,000 provider-input characters, 16,000 serialized-message characters, and approximately 4,000 input tokens per attempt. Both attempts had direct current-call proof, actual OpenRouter usage, and no budget incidents. Total actual usage was 6,427 input, 1,940 output, and 8,367 tokens.

## Bugs found and repaired during live proof

1. The original dossier consumed nearly the full input cap, so repair context could be blocked. The dossier now reserves bounded repair capacity inside the same cap.
2. Repair errors were too opaque and the backup did not receive correction context. Repair and backup now receive bounded structured corrections without weakening grounding or language validation.
3. The trace page preferred a stale local portfolio over the authenticated backend, so a successful retry could disappear after navigation. Backend is now preferred when available; local data is fallback only.
4. The persisted demo radar still contained legacy English presentation fields. A stable-id migration localizes only the known industrial demo radar and preserves arbitrary user radars.

## Visual proof

Runtime screenshots and the machine-readable report are generated under ignored local state:

- `var/visual-proof/2.17.4.7.0.2/live-retry/signal-card-after-retry.png`
- `var/visual-proof/2.17.4.7.0.2/live-retry/trace-after-retry.png`
- `var/visual-proof/2.17.4.7.0.2/live-retry/live-retry-report.json`

No secret, full provider payload, full page text, or authentication value is committed.
