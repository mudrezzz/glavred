import { useEffect, useState, type Dispatch, type SetStateAction } from 'react';
import {
  createAuthorMemoryEvent,
  inferAuthorPositionAssertions
} from '../application/editorialServices';
import {
  createEditorialValidationRun,
  type AuthorNote,
  type WorkspaceState
} from '../domain/editorialWorkspace';
import { LocalWorkspaceStore } from '../infrastructure/localWorkspaceStore';

const store = new LocalWorkspaceStore();

export type WorkspacePatch = (patch: Partial<WorkspaceState>, message?: string) => void;
export type WorkspaceSetter = Dispatch<SetStateAction<WorkspaceState>>;

export function useWorkspacePersistence() {
  const [workspace, setWorkspace] = useState<WorkspaceState>(() => store.load());
  const [toast, setToast] = useState('');

  useEffect(() => {
    store.save({ ...workspace, updatedAt: new Date().toISOString() });
  }, [workspace]);

  useEffect(() => {
    if (!toast) return undefined;

    const timeoutId = window.setTimeout(() => setToast(''), 2800);
    return () => window.clearTimeout(timeoutId);
  }, [toast]);

  function patchWorkspace(patch: Partial<WorkspaceState>, message?: string) {
    setWorkspace((current) => ({ ...current, ...patch, updatedAt: new Date().toISOString() }));
    if (message) setToast(message);
  }

  function patchEditorialSetup(patch: Partial<WorkspaceState>, message?: string) {
    setWorkspace((current) => ({
      ...current,
      ...patch,
      editorialSetupRevision: (current.editorialSetupRevision ?? 0) + 1,
      updatedAt: new Date().toISOString()
    }));
    if (message) setToast(message);
  }

  function changeAuthorNotes(authorNotes: AuthorNote[], message?: string) {
    const authorMemoryEvents = authorNotes.map(createAuthorMemoryEvent);
    const authorPositionAssertions = inferAuthorPositionAssertions(authorNotes, authorMemoryEvents);
    patchWorkspace({ authorNotes, authorMemoryEvents, authorPositionAssertions }, message);
  }

  function runEditorialValidation() {
    setWorkspace((current) => {
      const checkedAt = new Date().toISOString();
      return {
        ...current,
        editorialValidationRun: createEditorialValidationRun(current, checkedAt),
        updatedAt: checkedAt
      };
    });
    setToast('Редакционная модель проверена');
  }

  function resetWorkspace() {
    setWorkspace(store.reset());
    setToast('Демо-сценарий восстановлен');
  }

  return {
    changeAuthorNotes,
    patchEditorialSetup,
    patchWorkspace,
    resetWorkspace,
    runEditorialValidation,
    setToast,
    setWorkspace,
    toast,
    workspace
  };
}
