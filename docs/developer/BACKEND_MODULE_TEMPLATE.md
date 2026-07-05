# Backend Module Template

Use this checklist before adding or moving backend code. It is enforced by
`npm run test:architecture` for bounded-context packages.

## Ownership Header

Every non-`__init__.py` module under `backend/app/drafting`, `backend/app/upstream`,
or `backend/app/shared` starts with this header:

```python
"""Owner: drafting.application.validation

Used by: DraftRun validation orchestration.
Does not own: API request parsing, SQLite persistence, provider transport, or UI trace layout.
Architecture doc: docs/architecture/BACKEND_ARCHITECTURE_TARGET.md
"""
```

## Role Templates

Service modules own one use case or orchestration boundary. They may coordinate
policies/components/adapters, but they do not own route parsing or provider SDK calls.

Policy modules own deterministic decisions: fallback, ranking, budget, gate,
acceptance, or safety rules. They should be provider-free and easy to unit test.

Component modules own builders, parsers, mappers, compilers, evaluators, and trace
payload collaborators. They should not become hidden orchestration services.

DTO modules own provider-free values, result contracts, and small factory surfaces.
They must not import infrastructure, provider adapters, queues, or FastAPI.

Compatibility shims are import/re-export only. They may preserve old import paths,
but must not contain local `def`, `class`, `.complete_json(`, fallback logic, or trace
mutation.

## Placement Rules

- New DraftRun code goes under `backend/app/drafting`.
- New upstream radar/search/signal code goes under `backend/app/upstream`.
- Cross-context LLM/provider-neutral contracts go under `backend/app/shared` only
  when at least two bounded contexts need them.
- Do not add new flat `backend/app/application/draft_*.py`,
  `backend/app/domain/draft_*.py`, or `backend/app/application/upstream_radar_*.py`
  files unless a roadmap slice records a temporary debt exception.

## Provider-Heavy Review Checklist

Provider-heavy services must prove:

- no raw provider `.complete_json(` calls in bounded-context application modules;
- shared `LlmOperationEnvelope` or explicit inventory debt entry;
- `LlmOperationIncident` metadata for fallback, backup-accepted, not-run, failed,
  timeout, cancelled, and stale outcomes;
- safe errors only, no raw provider objects, headers, secrets, or token payloads;
- named payload budget policy for DraftRun provider inputs, or explicit
  `payloadBudgetStatus=debtAllowlisted`;
- timeout/runtime-budget handling for operations that can leave a DraftRun running;
- trace-safe child `AiRun.requestPayload`, attempts, `operationEnvelope`,
  `payloadBudget`, and `runtimeBudget` payloads where applicable.

## Review Commands

```powershell
npm run test:architecture
python -m pytest backend/tests/test_drafting_package_shims.py backend/tests/test_drafting_legacy_surface_inventory.py
python -m backend.app.roadmap check
git diff --check
```
