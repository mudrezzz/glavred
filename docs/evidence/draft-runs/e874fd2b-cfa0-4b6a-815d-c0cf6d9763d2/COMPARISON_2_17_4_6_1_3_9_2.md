# Slice 2.17.4.6.1.3.9.2 live comparison

## Verdict

Pairwise identity and final-message budgeting are live-proven by DraftRun
`480be950-4538-4077-bccb-330b732ff26a`.

- terminal status: `succeeded`;
- initial four-candidate ranking: `6/6` expected pairs;
- two revision rankings: `1/1` pair each;
- missing, duplicate and invalid pairs: `0`;
- all seven editorial dimensions are present exactly once in every accepted ranking;
- actual message sizes: `20269`, `12223`, `12227` against `22000`;
- provider-input sizes: `16964`, `10119`, `10121`;
- ranking repair or fallback: none;
- evidence coverage: `sufficient`;
- open critical: `0`;
- editorial status: `publishable`;
- open warning: `0`.

## Historical replay

The audit deliberately does not repair historical data. Run `92532...` contained six
useful comparison decisions and seven dimensions, but all six rows had blank
`leftCandidateId` and `rightCandidateId`; it is `incomplete`. Run `7bf3...` had the
same blank identity and only three rows for a four-candidate pool; it is also
`incomplete`.

This distinction is important: the old editorial decisions remain useful evidence,
but they cannot prove which pair each decision describes. The new contract rejects
that ambiguity before a provider response is accepted.

## Quality boundary

The slice did not change the ranking formula. The live initial winner was
`candidate-contrast-brief-control-workflow-20260703211313`; the delivered text is its
bounded revised candidate. Provider recovery used backup models in evidence
interpretation and editorial critique, so the overall verdict is
`recoveredSuccess`, but evidence is sufficient and the final editorial result is
trusted/publishable with no open critical or warning findings.

Run `b9dfe586-60f5-4a70-8ab5-cc64417d3bdb` is retained as storage-inconclusive
evidence. Its initial `6/6` matrix was complete, but a host-side replay audit was
incorrectly run while Docker worker was writing the Windows bind-mounted SQLite;
the run later ended with controlled `disk I/O error`. Both databases passed
integrity checks. The accepted run was observed through HTTP only until terminal
status.

## Reproduction

```bash
python scripts/audit_pairwise_comparison_identity.py --run-id 480be950-4538-4077-bccb-330b732ff26a --fail-on-incomplete
python scripts/audit_draft_run_provider_inputs.py --run-id 480be950-4538-4077-bccb-330b732ff26a --format json
python scripts/check_sqlite_integrity.py
```
