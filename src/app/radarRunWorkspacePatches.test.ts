import { describe, expect, it } from 'vitest';
import type { WorkspaceState } from '../domain/editorialWorkspace';
import { applyRadarRunWorkspaceResult } from './radarRunWorkspacePatches';

describe('applyRadarRunWorkspaceResult', () => {
  it('replaces the signal revision for one run without touching other runs', () => {
    const workspace = {
      radars: [],
      radarRuns: [{ id: 'run-1' }, { id: 'run-2' }],
      foundMaterials: [],
      sourceSignals: [
        { id: 'old-signal', radarRunId: 'run-1' },
        { id: 'other-signal', radarRunId: 'run-2' }
      ]
    } as unknown as WorkspaceState;

    const updated = applyRadarRunWorkspaceResult(workspace, {
      run: { id: 'run-1' } as WorkspaceState['radarRuns'][number],
      sourceSignals: [{ id: 'new-signal', radarRunId: 'run-1' } as WorkspaceState['sourceSignals'][number]]
    });

    expect(updated.sourceSignals.map((signal) => signal.id)).toEqual(['new-signal', 'other-signal']);
  });
});
