import { afterEach, describe, expect, it } from 'vitest';
import { fetchRadarRunTrace, setRadarRunTracePortfolioLoadersForTests } from './radarRunTraceClient';
import { createRadarTracePortfolio } from '../features/signals/radarRunTraceTestFixtures';

describe('radarRunTraceClient', () => {
  afterEach(() => setRadarRunTracePortfolioLoadersForTests(null, null));

  it('falls back to a local RadarRun when the backend portfolio is unavailable', async () => {
    setRadarRunTracePortfolioLoadersForTests(() => createRadarTracePortfolio(), () => {
      throw new Error('backend unavailable');
    });

    const trace = await fetchRadarRunTrace('radar-run-industrial-1');

    expect(trace.source).toBe('local');
    expect(trace.run.id).toBe('radar-run-industrial-1');
    expect(trace.radar.id).toBe('ai-pattern-radar-industrial-cases');
    expect(trace.sourceHandles.map((handle) => handle.id)).toEqual(['source-open-web']);
    expect(trace.foundMaterials.map((material) => material.id)).toEqual(['material-case']);
  });

  it('prefers the authenticated backend trace over a stale local copy', async () => {
    setRadarRunTracePortfolioLoadersForTests(
      () => createRadarTracePortfolio({ status: 'partial' }),
      () => createRadarTracePortfolio()
    );

    const trace = await fetchRadarRunTrace('radar-run-industrial-1');

    expect(trace.source).toBe('backend');
    expect(trace.run.id).toBe('radar-run-industrial-1');
    expect(trace.run.status).not.toBe('partial');
  });

  it('reports missing and blank run ids with readable errors', async () => {
    setRadarRunTracePortfolioLoadersForTests(() => createRadarTracePortfolio(), () => createRadarTracePortfolio());

    await expect(fetchRadarRunTrace('')).rejects.toThrow(/required/i);
    await expect(fetchRadarRunTrace('missing-run')).rejects.toThrow(/not found/i);
  });
});
