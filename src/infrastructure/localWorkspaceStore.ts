import { createDemoWorkspace } from '../fixtures/demoWorkspace';
import type { WorkspaceState, WorkspaceStore } from '../domain/editorialWorkspace';

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

  return {
    ...demo,
    ...saved,
    authorNotes: saved.authorNotes ?? demo.authorNotes,
    authorMemoryEvents: saved.authorMemoryEvents ?? demo.authorMemoryEvents,
    authorPositionAssertions: saved.authorPositionAssertions ?? demo.authorPositionAssertions,
    editorialModel: saved.editorialModel ?? demo.editorialModel,
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
    activeSection: saved.activeSection ?? demo.activeSection,
    updatedAt: saved.updatedAt ?? demo.updatedAt
  };
}
