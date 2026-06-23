import { afterEach, describe, expect, it, vi } from 'vitest';
import {
  type DraftRunResponse,
  setDraftRunFetchForTests,
  setDraftRunPollingForTests,
  waitForDraftRun
} from './draftRunClient';

describe('draftRunClient polling discipline', () => {
  afterEach(() => {
    setDraftRunFetchForTests(null);
    setDraftRunPollingForTests({ intervalMs: 1600, timeoutMs: 120000 });
  });

  it('keeps polling a live DraftRun after the timeout window', async () => {
    let call = 0;
    const fetcher = vi.fn().mockImplementation(async () => {
      call += 1;
      return {
        ok: true,
        json: async () => call < 4
          ? makeRun('running', { isStale: call > 2 })
          : makeRun('succeeded')
      };
    }) as unknown as typeof fetch;
    setDraftRunFetchForTests(fetcher);
    setDraftRunPollingForTests({ intervalMs: 1, timeoutMs: 2 });

    const run = await waitForDraftRun('draft-run-long');

    expect(run.status).toBe('succeeded');
    expect(fetcher).toHaveBeenCalledTimes(4);
  });

  it('passes stale running state through progress callbacks', async () => {
    const progress: DraftRunResponse[] = [];
    const fetcher = vi.fn().mockResolvedValueOnce({
      ok: true,
      json: async () => makeRun('running', {
        isStale: true,
        staleReason: 'No DraftRun progress for more than 5 minutes.'
      })
    }).mockResolvedValueOnce({
      ok: true,
      json: async () => makeRun('succeeded')
    }) as unknown as typeof fetch;
    setDraftRunFetchForTests(fetcher);
    setDraftRunPollingForTests({ intervalMs: 1, timeoutMs: 1000 });

    await waitForDraftRun('draft-run-stale', (run) => progress.push(run));

    expect(progress[0].isStale).toBe(true);
    expect(progress[0].staleReason).toContain('No DraftRun progress');
  });
});

function makeRun(status: 'running' | 'succeeded', overrides: Partial<DraftRunResponse> = {}): DraftRunResponse {
  return {
    id: 'draft-run-long',
    status,
    steps: [
      step('context', 'succeeded'),
      step('rhetoricalPlans', status === 'running' ? 'running' : 'succeeded')
    ],
    finalDraft: status === 'succeeded'
      ? { id: 'draft-1', briefId: 'brief-1', title: 'title', body: 'body', version: 1, status: 'draft', updatedAt: '2026-06-23T00:00:00.000Z' }
      : null,
    error: null,
    isStale: false,
    staleReason: null,
    lastProgressAt: '2026-06-23T00:00:00.000Z',
    createdAt: '2026-06-23T00:00:00.000Z',
    updatedAt: '2026-06-23T00:00:00.000Z',
    ...overrides
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
