import { describe, expect, it } from 'vitest';
import { runLocalRadar } from './upstreamRadarRunService';
import { createDemoWorkspace } from '../fixtures/demoWorkspace';

describe('upstream radar run service', () => {
  it('creates a deterministic RadarRun and FoundMaterial without creating downstream signals or candidates', () => {
    const workspace = createDemoWorkspace({ includeSeededHitlLearning: false });
    const radar = workspace.radars[0];
    const sourceSignalCount = workspace.sourceSignals.length;
    const postCandidateCount = workspace.postCandidates.length;

    const next = runLocalRadar(workspace, radar.id, '2026-07-03T10:00:00.000Z');
    const latestRun = next.radarRuns.find((run) => run.radarId === radar.id && run.startedAt === '2026-07-03T10:00:00.000Z');

    expect(latestRun).toBeDefined();
    expect(latestRun?.operations.length).toBeGreaterThan(0);
    expect(latestRun?.foundMaterialIds.length).toBeGreaterThan(0);
    expect(next.foundMaterials.some((material) => material.radarRunId === latestRun?.id)).toBe(true);
    expect(next.sourceSignals).toHaveLength(sourceSignalCount);
    expect(next.postCandidates).toHaveLength(postCandidateCount);
  });

  it('records provider-backed handles as explicit skipped operations in contract mode', () => {
    const workspace = createDemoWorkspace({ includeSeededHitlLearning: false });
    const radar = workspace.radars.find((item) => item.sourceHandleIds?.some((id) => id.includes('openweb') || id.includes('open-web'))) ?? workspace.radars[0];

    const next = runLocalRadar(workspace, radar.id, '2026-07-03T11:00:00.000Z');
    const latestRun = next.radarRuns.find((run) => run.radarId === radar.id && run.startedAt === '2026-07-03T11:00:00.000Z');

    expect(latestRun?.operations.some((operation) => operation.status === 'skipped')).toBe(true);
    expect(latestRun?.skippedReasons.length).toBeGreaterThan(0);
    expect(latestRun?.skippedReasons).toEqual(expect.arrayContaining(['provider-not-implemented']));
  });
});
