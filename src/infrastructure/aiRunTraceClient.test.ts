import { describe, expect, it, vi } from 'vitest';
import { fetchAiRunTrace } from './aiRunTraceClient';

describe('aiRunTraceClient', () => {
  it('loads one AI run trace by id', async () => {
    const fetchMock = vi.fn().mockResolvedValue({
      ok: true,
      json: async () => ({
        id: 'run-42',
        capability: 'draftGeneration',
        status: 'succeeded',
        provider: 'openrouter',
        model: 'openai/gpt-4.1-mini',
        requestPayload: { promptMessages: [{ role: 'user', content: 'brief' }] },
        resultPayload: { draft: { title: 'Draft title', body: 'Draft body' } },
        error: null,
        fallbackUsed: false,
        createdAt: '2026-06-18T00:00:00+00:00',
        updatedAt: '2026-06-18T00:00:01+00:00'
      })
    });
    vi.stubGlobal('fetch', fetchMock);

    const trace = await fetchAiRunTrace('run-42');

    expect(fetchMock).toHaveBeenCalledWith('http://localhost:8000/api/ai-runs/run-42');
    expect(trace.resultPayload?.draft).toEqual({ title: 'Draft title', body: 'Draft body' });
    vi.unstubAllGlobals();
  });

  it('throws readable errors for missing runs', async () => {
    vi.stubGlobal('fetch', vi.fn().mockResolvedValue({ ok: false, status: 404 }));

    await expect(fetchAiRunTrace('missing')).rejects.toThrow(/not found/i);
    vi.unstubAllGlobals();
  });
});
