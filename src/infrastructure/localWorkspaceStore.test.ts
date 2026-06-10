import { describe, expect, it } from 'vitest';
import { LocalWorkspaceStore } from './localWorkspaceStore';
import { createDemoWorkspace } from '../fixtures/demoWorkspace';
import {
  approveFinalText,
  approvePostBrief,
  markLearningNoteCaptured,
  markReleaseExported,
  markReleaseReady,
  toggleReleaseChecklistItem
} from '../domain/editorialWorkspace';
import {
  createContentPlanItem,
  createEditorialLearningNote,
  createInsightCard,
  createPostBrief,
  createPostDraft,
  createReleasePackage
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
  it('loads the AI Product Manager demo workspace when nothing is saved', () => {
    const store = new LocalWorkspaceStore(createMemoryStorage());

    expect(store.load().activeSection).toBe('memory');
    expect(store.load().editorialModel.author).toContain('AI Product Manager');
    expect(store.load().authorNotes).toHaveLength(6);
  });

  it('loads an old workspace without author memory fields', () => {
    const storage = createMemoryStorage();
    const workspace = createDemoWorkspace();
    const oldWorkspace = { ...workspace } as Partial<typeof workspace>;
    delete oldWorkspace.authorNotes;
    delete oldWorkspace.authorMemoryEvents;
    delete oldWorkspace.authorPositionAssertions;
    storage.setItem(STORAGE_KEY, JSON.stringify(oldWorkspace));
    const store = new LocalWorkspaceStore(storage);

    const loaded = store.load();

    expect(loaded.authorNotes).toHaveLength(6);
    expect(loaded.authorMemoryEvents.length).toBeGreaterThan(0);
    expect(loaded.authorPositionAssertions).toHaveLength(5);
  });

  it('saves and loads author memory state', () => {
    const store = new LocalWorkspaceStore(createMemoryStorage());
    const workspace = createDemoWorkspace();
    const changed = {
      ...workspace,
      authorNotes: [
        {
          id: 'note-test',
          type: 'thought' as const,
          title: 'Новая мысль',
          body: 'AI feature должен объяснять confidence.',
          sourceUrl: '',
          tags: ['confidence'],
          capturedAt: '2026-06-10T12:00:00.000Z'
        },
        ...workspace.authorNotes
      ]
    };

    store.save(changed);

    expect(store.load().authorNotes[0].title).toBe('Новая мысль');
  });

  it('loads a Slice 0.4 workspace without draft/release/analytics fields', () => {
    const storage = createMemoryStorage();
    const workspace = createDemoWorkspace();
    const oldWorkspace = { ...workspace } as Partial<typeof workspace>;
    delete oldWorkspace.postDraft;
    delete oldWorkspace.editorialChecks;
    delete oldWorkspace.editorNotes;
    delete oldWorkspace.finalText;
    delete oldWorkspace.releasePackage;
    delete oldWorkspace.editorialLearningNote;
    storage.setItem(STORAGE_KEY, JSON.stringify(oldWorkspace));
    const store = new LocalWorkspaceStore(storage);

    const loaded = store.load();

    expect(loaded.postDraft).toBeNull();
    expect(loaded.editorialChecks).toEqual([]);
    expect(loaded.editorNotes).toEqual([]);
    expect(loaded.finalText).toBeNull();
    expect(loaded.releasePackage).toBeNull();
    expect(loaded.editorialLearningNote).toBeNull();
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

  it('saves and loads a ready release package', () => {
    const store = new LocalWorkspaceStore(createMemoryStorage());
    const workspace = createDemoWorkspace();
    const insight = createInsightCard(workspace.sourceSignal, workspace.editorialModel);
    const planItem = createContentPlanItem(insight);
    const brief = approvePostBrief(createPostBrief(planItem, insight, workspace.editorialModel));
    const draft = createPostDraft(brief, workspace.editorialModel);
    const finalText = approveFinalText(draft);
    const releasePackage = createReleasePackage(finalText, planItem);
    const completed = releasePackage.checklist.reduce(
      (current, item) => (item.done ? current : toggleReleaseChecklistItem(current, item.id)),
      releasePackage
    );

    store.save({
      ...workspace,
      insightCard: insight,
      contentPlanItem: planItem,
      postBrief: brief,
      postDraft: draft,
      finalText,
      releasePackage: markReleaseReady(completed)
    });

    expect(store.load().releasePackage?.status).toBe('ready');
  });

  it('saves and loads a captured editorial learning note', () => {
    const store = new LocalWorkspaceStore(createMemoryStorage());
    const workspace = createDemoWorkspace();
    const insight = createInsightCard(workspace.sourceSignal, workspace.editorialModel);
    const planItem = createContentPlanItem(insight);
    const brief = approvePostBrief(createPostBrief(planItem, insight, workspace.editorialModel));
    const draft = createPostDraft(brief, workspace.editorialModel);
    const finalText = approveFinalText(draft);
    const releasePackage = markReleaseExported(createReleasePackage(finalText, planItem));
    const editorialLearningNote = markLearningNoteCaptured(
      createEditorialLearningNote(releasePackage, finalText, planItem)
    );

    store.save({
      ...workspace,
      insightCard: insight,
      contentPlanItem: planItem,
      postBrief: brief,
      postDraft: draft,
      finalText,
      releasePackage,
      editorialLearningNote
    });

    expect(store.load().editorialLearningNote?.status).toBe('captured');
  });

  it('resets back to the demo workspace', () => {
    const store = new LocalWorkspaceStore(createMemoryStorage());
    const changed = { ...createDemoWorkspace(), activeSection: 'brief' as const, authorNotes: [] };
    store.save(changed);

    expect(store.reset().activeSection).toBe('memory');
    expect(store.load().activeSection).toBe('memory');
    expect(store.load().authorNotes).toHaveLength(6);
    expect(store.load().postDraft).toBeNull();
    expect(store.load().editorialChecks).toEqual([]);
    expect(store.load().finalText).toBeNull();
    expect(store.load().releasePackage).toBeNull();
    expect(store.load().editorialLearningNote).toBeNull();
  });
});
