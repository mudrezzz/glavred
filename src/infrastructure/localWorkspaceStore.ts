import { createDemoWorkspace } from '../fixtures/demoWorkspace';
import {
  completeTopicFabulaMatrix,
  normalizeWeightRange,
  type WorkspaceState,
  type WorkspaceStore
} from '../domain/editorialWorkspace';

const STORAGE_KEY = 'glavred.workspace.v1';

export class LocalWorkspaceStore implements WorkspaceStore {
  constructor(private readonly storage: Storage = window.localStorage) {}

  load(): WorkspaceState {
    const raw = this.storage.getItem(STORAGE_KEY);

    if (!raw) {
      return createDemoWorkspace();
    }

    try {
      return normalizeWorkspace(JSON.parse(raw) as Partial<WorkspaceState>);
    } catch {
      return createDemoWorkspace();
    }
  }

  save(workspace: WorkspaceState): void {
    this.storage.setItem(STORAGE_KEY, JSON.stringify(workspace));
  }

  reset(): WorkspaceState {
    const workspace = createDemoWorkspace();
    this.save(workspace);
    return workspace;
  }
}

export function normalizeWorkspace(saved: Partial<WorkspaceState>): WorkspaceState {
  const demo = createDemoWorkspace();
  const topics = (saved.topics ?? demo.topics).map((topic) => ({
    ...topic,
    weightRange: normalizeWeightRange(topic.weightRange)
  }));
  const fabulas = (saved.fabulas ?? demo.fabulas).map((fabula) => ({
    ...fabula,
    weightRange: normalizeWeightRange(fabula.weightRange)
  }));

  return {
    ...demo,
    ...saved,
    authorNotes: (saved.authorNotes ?? demo.authorNotes).map((note) => ({
      ...note,
      attachments: note.attachments ?? []
    })),
    authorMemoryEvents: saved.authorMemoryEvents ?? demo.authorMemoryEvents,
    authorPositionAssertions: saved.authorPositionAssertions ?? demo.authorPositionAssertions,
    editorialModel: saved.editorialModel ?? demo.editorialModel,
    projectProfile: saved.projectProfile ?? demo.projectProfile,
    editorialRules: saved.editorialRules ?? demo.editorialRules,
    editorialSetupRevision: saved.editorialSetupRevision ?? demo.editorialSetupRevision,
    editorialValidationRun: saved.editorialValidationRun ?? null,
    topics,
    fabulas,
    topicFabulaMatrix: completeTopicFabulaMatrix(topics, fabulas, saved.topicFabulaMatrix ?? demo.topicFabulaMatrix),
    sourceSignal: saved.sourceSignal ?? demo.sourceSignal,
    insightCard: saved.insightCard ?? null,
    contentPlanItem: saved.contentPlanItem ?? null,
    postBrief: saved.postBrief ?? null,
    postDraft: saved.postDraft ?? null,
    editorialChecks: saved.editorialChecks ?? [],
    editorNotes: saved.editorNotes ?? [],
    finalText: saved.finalText ?? null,
    releasePackage: saved.releasePackage ?? null,
    editorialLearningNote: saved.editorialLearningNote ?? null,
    externalSources: saved.externalSources ?? demo.externalSources,
    importCandidates: saved.importCandidates ?? demo.importCandidates,
    archiveRecords: saved.archiveRecords ?? demo.archiveRecords,
    bulkImportActions: saved.bulkImportActions ?? [],
    activeSection: saved.activeSection ?? demo.activeSection,
    updatedAt: saved.updatedAt ?? demo.updatedAt
  };
}
