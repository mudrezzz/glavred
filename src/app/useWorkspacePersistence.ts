import { useEffect, useState, type Dispatch, type SetStateAction } from 'react';
import {
  getAccessibleProjects,
  getArchivedProjects,
  getActiveProject,
  getActiveUser,
  getActiveWorkspace,
  selectPortfolioProject,
  selectPortfolioUser,
  updateActiveProjectWorkspace
} from '../application/portfolioService';
import {
  createProjectInPortfolio,
  updateProjectInPortfolio,
  type ProjectLifecycleInput
} from '../application/portfolioLifecycleService';
import { createAuthorMemoryEvent, inferAuthorPositionAssertions } from '../application/editorialServices';
import {
  createEditorialValidationRun,
  type AuthorNote,
  type WorkspaceState
} from '../domain/editorialWorkspace';
import { createDemoWorkspace } from '../fixtures/demoWorkspace';
import { LocalPortfolioStore } from '../infrastructure/localPortfolioStore';
import { useBackendPortfolioBridge } from './useBackendPortfolioBridge';

const store = new LocalPortfolioStore();

export type WorkspacePatch = (patch: Partial<WorkspaceState>, message?: string) => void;
export type WorkspaceSetter = Dispatch<SetStateAction<WorkspaceState>>;

export function useWorkspacePersistence() {
  const [portfolio, setPortfolio] = useState(() => store.load());
  const [toast, setToast] = useState('');
  const backend = useBackendPortfolioBridge({ localStore: store, portfolio, setPortfolio, setToast });
  const activeUser = getActiveUser(portfolio);
  const activeProject = getActiveProject(portfolio);
  const accessibleProjects = getAccessibleProjects(portfolio);
  const archivedProjects = getArchivedProjects(portfolio);
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
    if (backend.reloadBackendPortfolio()) return;
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

  async function createProject(input: ProjectLifecycleInput) {
    if (await backend.createProject(input)) return;
    setPortfolio((current) => createProjectInPortfolio(current, input, createDemoWorkspace()));
    setToast('Проект создан локально');
  }

  async function renameProject(projectId: string, title: string, description: string) {
    const patch = { title, description };
    if (await backend.updateProject(projectId, patch)) return;
    setPortfolio((current) => updateProjectInPortfolio(current, projectId, patch));
    setToast('Проект обновлен локально');
  }

  async function archiveProject(projectId: string) {
    if (await backend.updateProject(projectId, { status: 'archived' })) return;
    setPortfolio((current) => updateProjectInPortfolio(current, projectId, { status: 'archived' }));
    setToast('Проект отправлен в архив локально');
  }

  return {
    accessibleProjects,
    activeProject,
    activeUser,
    archivedProjects,
    authError: backend.authError,
    archiveProject,
    backendStatus: backend.backendStatus,
    changeAuthorNotes,
    createProject,
    login: backend.login,
    logout: backend.logout,
    patchEditorialSetup,
    patchWorkspace,
    portfolio,
    renameProject,
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
