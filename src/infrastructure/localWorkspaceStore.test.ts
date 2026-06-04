import { describe, expect, it } from 'vitest';
import { LocalWorkspaceStore } from './localWorkspaceStore';
import { createDemoWorkspace } from '../fixtures/demoWorkspace';
import { approveFinalText, approvePostBrief } from '../domain/editorialWorkspace';
import {
  createContentPlanItem,
  createInsightCard,
  createPostBrief,
  createPostDraft
} from '../application/editorialServices';

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

  it('loads a Slice 0.4 workspace without draft fields', () => {
    const storage = createMemoryStorage();
    const workspace = createDemoWorkspace();
    const oldWorkspace = { ...workspace } as Partial<typeof workspace>;
    delete oldWorkspace.postDraft;
    delete oldWorkspace.editorialChecks;
    delete oldWorkspace.editorNotes;
    delete oldWorkspace.finalText;
    storage.setItem(STORAGE_KEY, JSON.stringify(oldWorkspace));
    const store = new LocalWorkspaceStore(storage);

    const loaded = store.load();

    expect(loaded.postDraft).toBeNull();
    expect(loaded.editorialChecks).toEqual([]);
    expect(loaded.editorNotes).toEqual([]);
    expect(loaded.finalText).toBeNull();
  });

  it('saves and loads an approved final text', () => {
    const store = new LocalWorkspaceStore(createMemoryStorage());
    const workspace = createDemoWorkspace();
    const insight = createInsightCard(workspace.sourceSignal, workspace.editorialModel);
    const planItem = createContentPlanItem(insight);
    const brief = approvePostBrief(createPostBrief(planItem, insight, workspace.editorialModel));
    const draft = createPostDraft(brief, workspace.editorialModel);
    const finalText = approveFinalText(draft);

    store.save({
      ...workspace,
      insightCard: insight,
      contentPlanItem: planItem,
      postBrief: brief,
      postDraft: draft,
      finalText
    });

    expect(store.load().finalText?.approvalStatus).toBe('approved');
  });

  it('resets back to the demo workspace', () => {
    const store = new LocalWorkspaceStore(createMemoryStorage());
    const changed = { ...createDemoWorkspace(), activeSection: 'brief' as const };
    store.save(changed);

    expect(store.reset().activeSection).toBe('radar');
    expect(store.load().activeSection).toBe('radar');
    expect(store.load().postDraft).toBeNull();
    expect(store.load().editorialChecks).toEqual([]);
    expect(store.load().finalText).toBeNull();
  });
});
