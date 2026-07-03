import { afterEach, describe, expect, it, vi } from 'vitest';
import { createDemoWorkspace } from '../fixtures/demoWorkspace';
import { runExternalRadar, setRadarRunFetchForTests } from './radarRunClient';

describe('radar run client', () => {
  afterEach(() => setRadarRunFetchForTests(null));

  it('posts workspace and radar id to the backend external radar runner', async () => {
    const workspace = createDemoWorkspace({ includeSeededHitlLearning: false });
    const fetcher = vi.fn(async (_input: RequestInfo | URL, init?: RequestInit) => {
      return new Response(JSON.stringify({
        radar: workspace.radars[0],
        run: { id: 'run-1', radarId: workspace.radars[0].id, status: 'succeeded', startedAt: 'now', budget: {}, operations: [], foundMaterialIds: [], skippedReasons: [], warnings: [], errors: [] },
        foundMaterials: []
      }), { status: 200, headers: { 'Content-Type': 'application/json' } });
    });
    setRadarRunFetchForTests(fetcher as unknown as typeof fetch);

    await runExternalRadar(workspace, workspace.radars[0].id);

    expect(fetcher).toHaveBeenCalledWith(expect.stringContaining('/api/radar-runs/external'), expect.objectContaining({
      method: 'POST',
      credentials: 'include'
    }));
    const sent = JSON.parse(String(fetcher.mock.calls[0][1]?.body));
    expect(sent.radarId).toBe(workspace.radars[0].id);
    expect(sent.workspace.radars.length).toBeGreaterThan(0);
  });
});
