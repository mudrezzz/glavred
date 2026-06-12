import { describe, expect, it } from 'vitest';
import { LocalWorkspaceStore } from './localWorkspaceStore';
import { createDemoWorkspace } from '../fixtures/demoWorkspace';
import {
  approveFinalText,
  approvePostBrief,
  createEditorialValidationRun,
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
    expect(store.load().topics).toHaveLength(5);
    expect(store.load().fabulas).toHaveLength(5);
    expect(store.load().topicFabulaMatrix).toHaveLength(25);
    expect(store.load().projectProfile.name).toBe('TG-блог AI Product Manager');
    expect(store.load().editorialRules.length).toBeGreaterThan(10);
    expect(store.load().editorialSetupRevision).toBe(0);
    expect(store.load().editorialValidationRun).toBeNull();
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

  it('loads an old workspace without topic and fabula entities', () => {
    const storage = createMemoryStorage();
    const workspace = createDemoWorkspace();
    const oldWorkspace = { ...workspace } as Partial<typeof workspace>;
    delete oldWorkspace.topics;
    delete oldWorkspace.fabulas;
    delete oldWorkspace.topicFabulaMatrix;
    storage.setItem(STORAGE_KEY, JSON.stringify(oldWorkspace));
    const store = new LocalWorkspaceStore(storage);
    const loaded = store.load();

    expect(loaded.topics).toHaveLength(5);
    expect(loaded.fabulas).toHaveLength(5);
    expect(loaded.topicFabulaMatrix).toHaveLength(25);
  });

  it('loads an old workspace without project profile and editorial rules', () => {
    const storage = createMemoryStorage();
    const workspace = createDemoWorkspace();
    const oldWorkspace = { ...workspace } as Partial<typeof workspace>;
    delete oldWorkspace.projectProfile;
    delete oldWorkspace.editorialRules;
    delete oldWorkspace.editorialSetupRevision;
    delete oldWorkspace.editorialValidationRun;
    storage.setItem(STORAGE_KEY, JSON.stringify(oldWorkspace));
    const store = new LocalWorkspaceStore(storage);
    const loaded = store.load();

    expect(loaded.projectProfile.name).toBe('TG-блог AI Product Manager');
    expect(loaded.editorialRules.length).toBeGreaterThan(10);
    expect(loaded.editorialSetupRevision).toBe(0);
    expect(loaded.editorialValidationRun).toBeNull();
  });

  it('loads an old editorial validation snapshot without validator results', () => {
    const storage = createMemoryStorage();
    const workspace = createDemoWorkspace();
    const oldWorkspace = {
      ...workspace,
      editorialValidationRun: {
        id: 'old-validation-summary',
        revision: 0,
        checkedAt: '2026-06-10T10:00:00.000Z',
        summary: {
          status: 'yellow' as const,
          title: 'Old validation summary',
          summary: 'Legacy summary without ValidatorRun results.',
          items: []
        }
      }
    };
    storage.setItem(STORAGE_KEY, JSON.stringify(oldWorkspace));
    const store = new LocalWorkspaceStore(storage);
    const loaded = store.load();

    expect(loaded.editorialValidationRun?.id).toBe('old-validation-summary');
    expect(loaded.editorialValidationRun?.results).toEqual([]);
    expect(loaded.editorialValidationRun?.aggregateStatus).toBe('yellow');
  });

  it('normalizes old author notes without attachments', () => {
    const storage = createMemoryStorage();
    const workspace = createDemoWorkspace();
    const oldWorkspace = {
      ...workspace,
      authorNotes: workspace.authorNotes.map(({ attachments: _attachments, ...note }) => note)
    };
    storage.setItem(STORAGE_KEY, JSON.stringify(oldWorkspace));
    const store = new LocalWorkspaceStore(storage);

    expect(store.load().authorNotes.every((note) => Array.isArray(note.attachments))).toBe(true);
  });

  it('saves and loads author memory state', () => {
    const store = new LocalWorkspaceStore(createMemoryStorage());
    const workspace = createDemoWorkspace();
    const changed = {
      ...workspace,
      authorNotes: [
        {
          id: 'note-test',
          type: 'manualCorrection' as const,
          title: '',
          body: 'Не согласен: вывод про образ нужно привязать к adoption, а не к модели.',
          sourceUrl: '',
          tags: ['manual-correction'],
          attachments: [],
          capturedAt: '2026-06-10T12:00:00.000Z',
          targetType: 'assertion' as const,
          targetId: 'assertion-persona-ai-product-manager',
          targetTitle: 'AI Product Manager с исследовательской оптикой'
        },
        ...workspace.authorNotes
      ]
    };

    store.save(changed);

    expect(store.load().authorNotes[0].targetId).toBe('assertion-persona-ai-product-manager');
    expect(store.load().authorNotes[0].title).toBe('');
  });

  it('saves and loads edited topic, fabula, and matrix state', () => {
    const store = new LocalWorkspaceStore(createMemoryStorage());
    const workspace = createDemoWorkspace();
    const changed = {
      ...workspace,
      topics: [
        {
          ...workspace.topics[0],
          title: 'AI workflow discovery',
          weightRange: { min: 12, max: 34 }
        },
        ...workspace.topics.slice(1)
      ],
      fabulas: [
        {
          ...workspace.fabulas[0],
          title: 'Исследовательская записка'
        },
        ...workspace.fabulas.slice(1)
      ],
      topicFabulaMatrix: workspace.topicFabulaMatrix.map((entry, index) =>
        index === 0 ? { ...entry, enabled: false } : entry
      )
    };

    store.save(changed);

    expect(store.load().topics[0].title).toBe('AI workflow discovery');
    expect(store.load().topics[0].weightRange).toEqual({ min: 12, max: 34 });
    expect(store.load().fabulas[0].title).toBe('Исследовательская записка');
    expect(store.load().topicFabulaMatrix[0].enabled).toBe(false);
  });

  it('saves and loads project profile and editorial rules', () => {
    const store = new LocalWorkspaceStore(createMemoryStorage());
    const workspace = createDemoWorkspace();
    const changed = {
      ...workspace,
      projectProfile: {
        ...workspace.projectProfile,
        name: 'AI Product Studio Notes'
      },
      editorialRules: [
        {
          ...workspace.editorialRules[0],
          title: 'Обновленный образ автора'
        },
        ...workspace.editorialRules.slice(1)
      ],
      editorialSetupRevision: 3,
      editorialValidationRun: {
        ...createEditorialValidationRun(workspace, '2026-06-11T10:00:00.000Z'),
        id: 'validation-test',
        revision: 3
      }
    };

    store.save(changed);

    expect(store.load().projectProfile.name).toBe('AI Product Studio Notes');
    expect(store.load().editorialRules[0].title).toBe('Обновленный образ автора');
    expect(store.load().editorialSetupRevision).toBe(3);
    expect(store.load().editorialValidationRun?.id).toBe('validation-test');
    expect(store.load().editorialValidationRun?.results.length).toBe(5);
  });

  it('saves and loads author note attachments', () => {
    const store = new LocalWorkspaceStore(createMemoryStorage());
    const workspace = createDemoWorkspace();
    const changed = {
      ...workspace,
      authorNotes: [
        {
          ...workspace.authorNotes[0],
          id: 'note-with-attachment',
          attachments: [
            {
              id: 'attachment-roundtrip',
              fileName: 'roundtrip.txt',
              mimeType: 'text/plain',
              sizeBytes: 42,
              dataUrl: 'data:text/plain;base64,cm91bmR0cmlw',
              createdAt: '2026-06-10T12:00:00.000Z',
              localOnly: true
            }
          ]
        },
        ...workspace.authorNotes.slice(1)
      ]
    };

    store.save(changed);

    expect(store.load().authorNotes[0].attachments[0].fileName).toBe('roundtrip.txt');
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

  it('loads an old workspace without external import fields', () => {
    const storage = createMemoryStorage();
    const workspace = createDemoWorkspace();
    const oldWorkspace = { ...workspace } as Partial<typeof workspace>;
    delete oldWorkspace.externalSources;
    delete oldWorkspace.importCandidates;
    delete oldWorkspace.archiveRecords;
    delete oldWorkspace.bulkImportActions;
    storage.setItem(STORAGE_KEY, JSON.stringify(oldWorkspace));
    const store = new LocalWorkspaceStore(storage);

    const loaded = store.load();

    expect(loaded.externalSources).toHaveLength(5);
    expect(loaded.importCandidates.length).toBeGreaterThan(10);
    expect(loaded.archiveRecords.length).toBeGreaterThan(0);
    expect(loaded.bulkImportActions).toEqual([]);
  });

  it('saves and loads external sources, candidates, archive records, and bulk action state', () => {
    const store = new LocalWorkspaceStore(createMemoryStorage());
    const workspace = createDemoWorkspace();
    const changed = {
      ...workspace,
      importCandidates: [
        {
          ...workspace.importCandidates[0],
          reviewStatus: 'bulkAcceptedToArchive' as const,
          evidencePolicy: 'archiveOnly' as const
        },
        ...workspace.importCandidates.slice(1)
      ],
      archiveRecords: [
        {
          id: 'archive-test-roundtrip',
          sourceId: workspace.externalSources[0].id,
          title: 'Roundtrip archive',
          bodyExcerpt: 'Archive record roundtrip',
          originalUrl: '',
          publishedAt: '2026-06-11',
          acceptedAt: '2026-06-11T10:00:00.000Z',
          acceptanceMode: 'bulk' as const,
          evidencePolicy: 'archiveOnly' as const
        },
        ...workspace.archiveRecords
      ],
      bulkImportActions: [
        {
          id: 'bulk-roundtrip',
          action: 'bulkAcceptToArchive' as const,
          candidateIds: [workspace.importCandidates[0].id],
          previousStatuses: { [workspace.importCandidates[0].id]: 'new' as const },
          createdAt: '2026-06-11T10:00:00.000Z',
          canUndo: true,
          createdArchiveRecordIds: ['archive-test-roundtrip']
        }
      ]
    };

    store.save(changed);

    expect(store.load().importCandidates[0].reviewStatus).toBe('bulkAcceptedToArchive');
    expect(store.load().archiveRecords[0].id).toBe('archive-test-roundtrip');
    expect(store.load().bulkImportActions[0].canUndo).toBe(true);
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
    expect(store.load().externalSources).toHaveLength(5);
    expect(store.load().importCandidates.length).toBeGreaterThan(10);
    expect(store.load().archiveRecords.length).toBeGreaterThan(0);
    expect(store.load().bulkImportActions).toEqual([]);
  });
});
