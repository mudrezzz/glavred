import { afterEach, describe, expect, it, vi } from 'vitest';
import {
  currentDraftRunStep,
  type DraftRunResponse,
  draftFromCompletedRun,
  fetchDraftRun,
  setDraftRunFetchForTests,
  startDraftRun
} from './draftRunClient';
import type { EditorialModel, PostBrief } from '../domain/editorialWorkspace';

describe('draftRunClient', () => {
  afterEach(() => {
    setDraftRunFetchForTests(null);
  });

  it('starts a draft run with brief and editorial model payload', async () => {
    const fetcher = vi.fn().mockResolvedValue({
      ok: true,
      json: async () => ({ runId: 'draft-run-1', status: 'queued' })
    }) as unknown as typeof fetch;
    setDraftRunFetchForTests(fetcher);

    const response = await startDraftRun(makeBrief(), makeEditorialModel());

    expect(response).toEqual({ runId: 'draft-run-1', status: 'queued' });
    expect(fetcher).toHaveBeenCalledWith(
      expect.stringContaining('/api/draft-runs'),
      expect.objectContaining({ method: 'POST' })
    );
  });

  it('loads a draft run and maps the final draft generation trace', async () => {
    const run = makeRun('succeeded');
    const fetcher = vi.fn().mockResolvedValue({ ok: true, json: async () => run }) as unknown as typeof fetch;
    setDraftRunFetchForTests(fetcher);

    const loaded = await fetchDraftRun('draft-run-1');
    const draft = draftFromCompletedRun(loaded);

    expect(draft.generation?.source).toBe('draftRun');
    expect(draft.generation?.draftRunId).toBe('draft-run-1');
    expect(draft.body).toBe('body');
  });

  it('returns the running step before completed steps', () => {
    const run = makeRun('running');

    expect(currentDraftRunStep(run)?.key).toBe('draft');
  });

  it('throws on failed HTTP polling', async () => {
    const fetcher = vi.fn().mockResolvedValue({ ok: false, status: 500 }) as unknown as typeof fetch;
    setDraftRunFetchForTests(fetcher);

    await expect(fetchDraftRun('draft-run-1')).rejects.toThrow('HTTP 500');
  });
});

function makeRun(status: 'running' | 'succeeded'): DraftRunResponse {
  return {
    id: 'draft-run-1',
    status,
    steps: [
      step('context', 'succeeded'),
      step('draft', status === 'running' ? 'running' : 'succeeded')
    ],
    finalDraft: {
      id: 'draft-1',
      briefId: 'brief-1',
      title: 'title',
      body: 'body',
      version: 1,
      status: 'draft',
      updatedAt: '2026-06-19T00:00:00.000Z'
    },
    error: null,
    createdAt: '2026-06-19T00:00:00.000Z',
    updatedAt: '2026-06-19T00:00:00.000Z'
  };
}

function step(key: string, status: 'pending' | 'running' | 'succeeded' | 'failed') {
  return {
    key,
    status,
    title: key,
    artifactPayload: {},
    error: null,
    startedAt: null,
    completedAt: null
  };
}

function makeBrief(): PostBrief {
  return {
    id: 'brief-1',
    planItemId: 'plan-1',
    title: 'AI-B2B demo еще не продукт',
    rubric: 'AI product discovery',
    audience: 'AI PM',
    thesis: 'Demo magic не равно adoption.',
    conflict: 'Demo красиво, rollout слабый.',
    authorPosition: 'Сначала workflow, потом модель.',
    evidence: ['usage после пилота не растет'],
    examples: ['нет evals'],
    structure: ['конфликт'],
    cta: 'Проверьте продуктовую петлю.',
    risks: ['не звучать против прототипов'],
    sources: ['author note'],
    approvalStatus: 'approved'
  };
}

function makeEditorialModel(): EditorialModel {
  return {
    author: 'Glavred',
    audience: 'AI Product Manager',
    positioning: 'Pragmatic',
    fabula: 'Research note',
    rubrics: ['AI product discovery'],
    styleRules: ['исследовательский тон'],
    forbiddenTopics: ['generic AI hype'],
    goals: ['объяснить adoption gap']
  };
}
