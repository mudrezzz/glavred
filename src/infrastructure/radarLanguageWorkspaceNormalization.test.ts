import { describe, expect, it } from 'vitest';
import { createDemoWorkspace } from '../fixtures/demoWorkspace';
import { LocalWorkspaceStore, normalizeWorkspace } from './localWorkspaceStore';

const STORAGE_KEY = 'glavred.workspace.v1';

function createMemoryStorage(): Storage {
  const values = new Map<string, string>();
  return {
    get length() {
      return values.size;
    },
    clear: () => values.clear(),
    getItem: (key: string) => values.get(key) ?? null,
    key: (index: number) => Array.from(values.keys())[index] ?? null,
    removeItem: (key: string) => {
      values.delete(key);
    },
    setItem: (key: string, value: string) => {
      values.set(key, value);
    }
  };
}

describe('radar language workspace normalization', () => {
  it('keeps new backend extraction signals unscored and makes radar policies explicit', () => {
    const storage = createMemoryStorage();
    const workspace = createDemoWorkspace();
    const backendSignal = {
      ...workspace.sourceSignals[0],
      id: 'signal-backend-unscored',
      radarId: workspace.radars[0].id,
      radarRunId: 'radar-run-live-1',
      reviewStatus: 'candidate' as const,
      editorialLanguage: 'ru',
      localizationStatus: 'localized' as const,
      evidenceRefs: [{ materialId: 'material-1', fragmentId: 'fragment-1', quote: 'Original quote' }],
      filterEvaluations: undefined,
      filterStatus: undefined
    };
    storage.setItem(STORAGE_KEY, JSON.stringify({ ...workspace, sourceSignals: [backendSignal] }));

    const loaded = new LocalWorkspaceStore(storage).load();

    expect(loaded.sourceSignals[0].reviewStatus).toBe('candidate');
    expect(loaded.sourceSignals[0].filterStatus).toBeUndefined();
    expect(loaded.sourceSignals[0].filterEvaluations).toBeUndefined();
    expect(loaded.radars.every((radar) => radar.sourceLanguagePolicy)).toBe(true);
  });

  it('localizes the known legacy industrial radar without changing arbitrary radars', () => {
    const workspace = createDemoWorkspace();
    const legacyRadar = {
      ...workspace.radars[0],
      id: 'ai-pattern-radar-industrial-cases',
      title: 'Industrial AI cases',
      scope: 'Public industrial AI cases.',
      filters: [{
        id: 'ai-pattern-radar-industrial-cases-filter-industrial',
        dimension: 'topics' as const,
        enabled: true,
        mode: 'mustMatch' as const,
        instruction: 'Signal must be useful for industrial AI patterns.'
      }]
    };
    const customRadar = { ...workspace.radars[1], title: 'Custom English radar' };

    const normalized = normalizeWorkspace({ ...workspace, radars: [legacyRadar, customRadar] });

    expect(normalized.radars[0].title).toBe('Промышленные AI-кейсы');
    expect(normalized.radars[0].scope).toMatch(/^Публичные кейсы/u);
    expect(normalized.radars[0].filters?.[0].instruction).toMatch(/^Сигнал должен/u);
    expect(normalized.radars[1].title).toBe('Custom English radar');
  });
});
