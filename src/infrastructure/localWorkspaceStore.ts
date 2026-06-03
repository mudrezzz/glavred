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
      return JSON.parse(raw) as WorkspaceState;
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

