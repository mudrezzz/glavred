import { describe, expect, it } from 'vitest';
import { createDemoWorkspace } from '../fixtures/demoWorkspace';
import { LocalWorkspaceStore } from './localWorkspaceStore';

function createMemoryStorage(): Storage {
  const values = new Map<string, string>();
  return {
    get length() { return values.size; },
    clear: () => values.clear(),
    getItem: (key) => values.get(key) ?? null,
    key: (index) => Array.from(values.keys())[index] ?? null,
    removeItem: (key) => { values.delete(key); },
    setItem: (key, value) => { values.set(key, value); }
  };
}

describe('LocalWorkspaceStore signal integrity', () => {
  it('preserves extraction and scoring operations without source handles', () => {
    const store = new LocalWorkspaceStore(createMemoryStorage());
    const workspace = createDemoWorkspace();
    const run = {
      ...workspace.radarRuns[0],
      operations: [
        ...workspace.radarRuns[0].operations,
        { id: 'extract', runId: workspace.radarRuns[0].id, sourceHandleId: '', kind: 'signalExtraction' as const, label: 'Extraction', status: 'succeeded' as const, startedAt: workspace.updatedAt, foundMaterialIds: [] },
        { id: 'score', runId: workspace.radarRuns[0].id, sourceHandleId: '', kind: 'signalScoring' as const, label: 'Scoring', status: 'succeeded' as const, startedAt: workspace.updatedAt, foundMaterialIds: [] }
      ]
    };
    store.save({ ...workspace, radarRuns: [run] });

    expect(store.load().radarRuns[0].operations.map((item) => item.kind)).toEqual(
      expect.arrayContaining(['signalExtraction', 'signalScoring'])
    );
  });

  it('does not inherit the selected signal run and utility contract into legacy signals', () => {
    const store = new LocalWorkspaceStore(createMemoryStorage());
    const workspace = createDemoWorkspace();
    const run = {
      ...workspace.radarRuns[0],
      id: 'run-current-signal',
      radarId: workspace.radars[0].id
    };
    const utilityReport = {
      version: 1,
      revision: 2,
      status: 'complete' as const,
      recommendation: 'recommended' as const,
      dimensions: [],
      blockingReasons: [],
      warnings: []
    };
    const currentSignal = {
      ...workspace.sourceSignals[0],
      id: 'signal-current',
      radarId: workspace.radars[0].id,
      radarRunId: run.id,
      editorialLanguage: 'ru',
      localizationStatus: 'original' as const,
      utilityReport,
      utilityRevision: 2,
      legacyIntegrityStatus: 'current' as const
    };
    const legacySignal = {
      ...workspace.sourceSignals[1],
      radarId: workspace.radars[1].id,
      radarRunId: run.id,
      editorialLanguage: 'ru',
      localizationStatus: 'original' as const,
      utilityReport,
      utilityRevision: 2,
      legacyIntegrityStatus: 'needsReExtraction' as const
    };
    store.save({
      ...workspace,
      sourceSignal: currentSignal,
      sourceSignals: [currentSignal, legacySignal],
      radarRuns: [run, ...workspace.radarRuns]
    });

    const loaded = store.load();
    const loadedLegacy = loaded.sourceSignals.find((signal) => signal.id === legacySignal.id);

    expect(loadedLegacy?.radarRunId).toBeUndefined();
    expect(loadedLegacy?.utilityReport).toBeUndefined();
    expect(loadedLegacy?.utilityRevision).toBeUndefined();
    expect(loadedLegacy?.legacyIntegrityStatus).toBe('needsReExtraction');
    expect(loaded.sourceSignal.id).toBe(currentSignal.id);
    expect(loaded.sourceSignal.utilityReport?.recommendation).toBe('recommended');
  });
});
