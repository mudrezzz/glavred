import { describe, expect, it } from 'vitest';
import { LocalWorkspaceStore } from './localWorkspaceStore';
import { createDemoWorkspace } from '../fixtures/demoWorkspace';
import { approvePostBrief } from '../domain/editorialWorkspace';
import {
  createContentPlanItem,
  createInsightCard,
  createPostBrief
} from '../application/editorialServices';

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

describe('LocalWorkspaceStore', () => {
  it('loads the demo workspace when nothing is saved', () => {
    const store = new LocalWorkspaceStore(createMemoryStorage());

    expect(store.load().sourceSignal.title).toContain('Провалы AI-пилотов');
  });

  it('saves and loads an approved post brief', () => {
    const store = new LocalWorkspaceStore(createMemoryStorage());
    const workspace = createDemoWorkspace();
    const insight = createInsightCard(workspace.sourceSignal, workspace.editorialModel);
    const planItem = createContentPlanItem(insight);
    const brief = approvePostBrief(createPostBrief(planItem, insight, workspace.editorialModel));

    store.save({ ...workspace, insightCard: insight, contentPlanItem: planItem, postBrief: brief });

    expect(store.load().postBrief?.approvalStatus).toBe('approved');
  });

  it('resets back to the demo workspace', () => {
    const store = new LocalWorkspaceStore(createMemoryStorage());
    const changed = { ...createDemoWorkspace(), activeSection: 'brief' as const };
    store.save(changed);

    expect(store.reset().activeSection).toBe('radar');
    expect(store.load().activeSection).toBe('radar');
  });
});

