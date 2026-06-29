import { useEffect, useState, type Dispatch, type SetStateAction } from 'react';
import {
  getAccessibleProjects,
  getActiveProject,
  getActiveUser,
  getActiveWorkspace,
  selectPortfolioProject,
  selectPortfolioUser,
  updateActiveProjectWorkspace
} from '../application/portfolioService';
import {
  createAuthorMemoryEvent,
  inferAuthorPositionAssertions
} from '../application/editorialServices';
import {
  createEditorialValidationRun,
  type AuthorNote,
  type WorkspaceState
} from '../domain/editorialWorkspace';
import { LocalPortfolioStore } from '../infrastructure/localPortfolioStore';

const store = new LocalPortfolioStore();

export type WorkspacePatch = (patch: Partial<WorkspaceState>, message?: string) => void;
export type WorkspaceSetter = Dispatch<SetStateAction<WorkspaceState>>;

export function useWorkspacePersistence() {
  const [portfolio, setPortfolio] = useState(() => store.load());
  const [toast, setToast] = useState('');
  const activeUser = getActiveUser(portfolio);
  const activeProject = getActiveProject(portfolio);
  const accessibleProjects = getAccessibleProjects(portfolio);
  const workspace = getActiveWorkspace(portfolio);

  useEffect(() => {
    store.save(portfolio);
  }, [portfolio]);

  useEffect(() => {
    if (!toast) return undefined;

    const timeoutId = window.setTimeout(() => setToast(''), 2800);
    return () => window.clearTimeout(timeoutId);
  }, [toast]);

  const setWorkspace: WorkspaceSetter = (next) => {
    setPortfolio((current) =>
      updateActiveProjectWorkspace(current, (currentWorkspace) => {
        const nextWorkspace = typeof next === 'function' ? next(currentWorkspace) : next;
        return { ...nextWorkspace, updatedAt: nextWorkspace.updatedAt ?? new Date().toISOString() };
      })
    );
  };

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
    setPortfolio(store.reset());
    setToast('Демо-портфель восстановлен');
  }

  function selectUser(userId: string) {
    setPortfolio((current) => selectPortfolioUser(current, userId));
    setToast('Пользователь выбран');
  }

  function selectProject(projectId: string) {
    setPortfolio((current) => selectPortfolioProject(current, projectId));
    setToast('Блог выбран');
  }

  return {
    accessibleProjects,
    activeProject,
    activeUser,
    changeAuthorNotes,
    patchEditorialSetup,
    patchWorkspace,
    portfolio,
    resetWorkspace,
    runEditorialValidation,
    selectProject,
    selectUser,
    setToast,
    setWorkspace,
    toast,
    workspace
  };
}
