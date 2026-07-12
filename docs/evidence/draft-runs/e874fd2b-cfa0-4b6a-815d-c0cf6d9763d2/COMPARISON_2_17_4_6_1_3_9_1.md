# Slice 2.17.4.6.1.3.9.1 live comparison

## Verdict

`alternativeAngleRoute` is repaired and live-proven. The accepted run is
`92532cb9-e83b-4bb1-ab2b-7d7a46d279b5`.

- actual serialized messages: `16321/22000`;
- budget incident: none;
- all provider-input audit findings: `20 directlyBudgeted`, zero over-budget;
- challenger generated, validated, ranked, and used as the base of the final revised winner;
- evidence: `sufficient`;
- editorial status: `publishable`;
- open critical/warning: `0/0`.

## Budget comparison

| Metric | Before `7bf3...` | After `92532...` | Change |
| --- | ---: | ---: | ---: |
| Route input / actual messages | 34589 | 16321 | -52.8% |
| Provider-input projection | not recorded separately | 14371 | direct proof added |
| Prompt cost | 0.01192375 | 0.005405 | -54.7% |
| Total route-call cost | 0.02604625 | 0.01945625 | -25.3% |
| Budget incident | `payloadTooLarge` | none | repaired |

The final-message measurement includes prompt instructions and the bounded repair
context. The gate therefore cannot report a clean dossier while sending oversized
messages outside the measured payload.

## Semantic proof

The compact route retained three symmetric candidates, candidate-scoped critique
signals, validation issues, rejected moves, PostContract constraints, evidence and
rule identifiers. There were no missing required inputs, forbidden fields, or
unresolved handles.

The accepted route changed the editorial frame from an architectural/function list
to one maintenance-decision scene: diagnostics, work order and RCA disagree, the
workbench exposes uncertainty, and the engineer remains the decision owner. The
route therefore is not a paraphrase of the incumbent. Its challenger passed the
remaining pipeline and the final winner id is derived from that challenger.

## Quality comparison

The earlier `7bf3...` text remains stronger in one respect: its failure-first opening
with a concrete confidence conflict is sharper. The new text is shorter (`5574`
body characters and 11 paragraphs versus `8938` and 18), more compact, and remains
within the same evidence/contract boundaries. It still contains the industrial
maintenance situation, conflicting sources, uncertainty boundary, and engineer
ownership.

There is no structured evidence that dossier trimming caused a quality regression:
the route consumed the intended critique signals, produced a different challenger,
and the challenger survived validation, ranking, revision, and final quality. The
quality verdict is `recoveredSuccess`, rather than a completely clean provider path,
because evidence interpretation recovered from provider timeouts; this is separate
from the route budget repair.

## Inconclusive attempt

Run `d08b26c7-2b5d-436a-8d03-5f4def3b3991` failed during validation with a transient
SQLite `disk I/O error` before `alternativeAngleRoute` was executed. Both SQLite
databases returned `integrity_check=ok` afterward. It is retained as operational
evidence but is not used as route acceptance proof.
