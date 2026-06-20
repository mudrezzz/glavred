import { describe, expect, it, vi } from 'vitest';
import { fetchRunTrace } from './runTraceClient';

describe('runTraceClient', () => {
  it('loads a DraftRun and its child AI runs', async () => {
    const fetchMock = vi.fn()
      .mockResolvedValueOnce({
        ok: true,
        json: async () => makeDraftRun({ aiRunIds: ['ai-1', 'ai-2'] })
      })
      .mockResolvedValueOnce({ ok: true, json: async () => makeAiRun('ai-1') })
      .mockResolvedValueOnce({ ok: true, json: async () => makeAiRun('ai-2') });
    vi.stubGlobal('fetch', fetchMock);

    const trace = await fetchRunTrace('draft-1');

    expect(trace.kind).toBe('draftRun');
    if (trace.kind === 'draftRun') {
      expect(trace.childAiRuns.map((run) => run.id)).toEqual(['ai-1', 'ai-2']);
      expect(trace.missingAiRunIds).toEqual([]);
    }
    expect(fetchMock).toHaveBeenNthCalledWith(1, 'http://localhost:8000/api/draft-runs/draft-1');
    expect(fetchMock).toHaveBeenNthCalledWith(2, 'http://localhost:8000/api/ai-runs/ai-1');
    vi.unstubAllGlobals();
  });

  it('falls back to a single AiRun only after DraftRun 404', async () => {
    const fetchMock = vi.fn()
      .mockResolvedValueOnce({ ok: false, status: 404 })
      .mockResolvedValueOnce({ ok: true, json: async () => makeAiRun('ai-only') });
    vi.stubGlobal('fetch', fetchMock);

    const trace = await fetchRunTrace('ai-only');

    expect(trace.kind).toBe('aiRun');
    expect(trace.kind === 'aiRun' ? trace.aiRun.id : '').toBe('ai-only');
    expect(fetchMock).toHaveBeenNthCalledWith(2, 'http://localhost:8000/api/ai-runs/ai-only');
    vi.unstubAllGlobals();
  });

  it('does not mask DraftRun backend errors as AiRun lookups', async () => {
    const fetchMock = vi.fn().mockResolvedValueOnce({ ok: false, status: 500 });
    vi.stubGlobal('fetch', fetchMock);

    await expect(fetchRunTrace('broken')).rejects.toThrow(/DraftRun request failed/i);
    expect(fetchMock).toHaveBeenCalledTimes(1);
    vi.unstubAllGlobals();
  });

  it('reports missing child AI runs without failing the parent trace', async () => {
    const fetchMock = vi.fn()
      .mockResolvedValueOnce({
        ok: true,
        json: async () => makeDraftRun({ aiRunIds: ['ai-1', 'missing-ai'] })
      })
      .mockResolvedValueOnce({ ok: true, json: async () => makeAiRun('ai-1') })
      .mockResolvedValueOnce({ ok: false, status: 404 });
    vi.stubGlobal('fetch', fetchMock);

    const trace = await fetchRunTrace('draft-1');

    expect(trace.kind).toBe('draftRun');
    if (trace.kind === 'draftRun') {
      expect(trace.childAiRuns.map((run) => run.id)).toEqual(['ai-1']);
      expect(trace.missingAiRunIds).toEqual(['missing-ai']);
    }
    vi.unstubAllGlobals();
  });
});

type DraftRunFixture = {
  id: string;
  status: string;
  inputSummary: Record<string, unknown>;
  steps: Array<Record<string, unknown>>;
  finalDraft: Record<string, unknown> | null;
  error: string | null;
  aiRunIds: string[];
  createdAt: string;
  updatedAt: string;
};

function makeDraftRun(overrides: Partial<DraftRunFixture> = {}): DraftRunFixture {
  return {
    id: 'draft-1',
    status: 'succeeded',
    inputSummary: { title: 'Input' },
    steps: [
      {
        key: 'context',
        status: 'succeeded',
        title: 'Context',
        artifactPayload: { workItem: { title: 'Post' } },
        error: null,
        startedAt: '2026-06-19T00:00:00+00:00',
        completedAt: '2026-06-19T00:00:01+00:00'
      }
    ],
    finalDraft: { title: 'Draft', body: 'Body' },
    error: null,
    aiRunIds: [],
    createdAt: '2026-06-19T00:00:00+00:00',
    updatedAt: '2026-06-19T00:00:01+00:00',
    ...overrides
  };
}

function makeAiRun(id: string) {
  return {
    id,
    capability: 'draftGeneration',
    status: 'succeeded',
    provider: 'openrouter',
    model: 'deepseek/deepseek-v3.2',
    requestPayload: { draftRunStep: 'materialPlan' },
    resultPayload: { result: { availableEvidence: ['signal'] } },
    error: null,
    fallbackUsed: false,
    createdAt: '2026-06-19T00:00:00+00:00',
    updatedAt: '2026-06-19T00:00:01+00:00'
  };
}
