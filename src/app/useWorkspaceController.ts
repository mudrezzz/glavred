import { useState } from 'react';
import type { WorkspaceSection } from '../domain/editorialWorkspace';
import type { MemoryInternalTab } from '../features/author-memory/types';
import type { EditorialModelTab } from '../features/editorial-model/types';
import { useContextChatController } from './useContextChatController';
import { usePostCandidateWorkspaceActions } from './usePostCandidateWorkspaceActions';
import { useProductionFlowActions } from './useProductionFlowActions';
import { useSignalsWorkspaceActions } from './useSignalsWorkspaceActions';
import { useWorkspacePersistence } from './useWorkspacePersistence';

export function useWorkspaceController() {
  const {
    accessibleProjects,
    activeProject,
    activeUser,
    archivedProjects,
    authError,
    archiveProject,
    backendStatus,
    changeAuthorNotes,
    createProject,
    integrityError,
    login: backendLogin,
    logout: backendLogout,
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
  } = useWorkspacePersistence();
  const [portfolioMode, setPortfolioMode] = useState<'projectDashboard' | 'projectCabinet'>('projectDashboard');
  const [memoryTab, setMemoryTab] = useState<MemoryInternalTab>('feed');
  const [editorialModelTab, setEditorialModelTab] = useState<EditorialModelTab>('publisher');
  const active = workspace.activeSection;

  const contextChatController = useContextChatController({
    active,
    editorialModelTab,
    memoryTab,
    setEditorialModelTab,
    setToast,
    setWorkspace,
    workspace
  });
  const signalsActions = useSignalsWorkspaceActions({ activeProject, setToast, setWorkspace, workspace });
  const postCandidateActions = usePostCandidateWorkspaceActions({ setToast, setWorkspace });
  const productionActions = useProductionFlowActions({ patchWorkspace, workspace });

  function go(section: WorkspaceSection) {
    patchWorkspace({ activeSection: section });
  }

  function resetDemo() {
    resetWorkspace();
    setPortfolioMode('projectDashboard');
    setMemoryTab('feed');
    setEditorialModelTab('publisher');
    contextChatController.resetContextChat();
  }

  function openProject(projectId: string) {
    if (activeProject.id !== projectId) selectProject(projectId);
    setPortfolioMode('projectCabinet');
  }

  function goProjectDashboard() {
    setPortfolioMode('projectDashboard');
  }

  async function login(email: string, password: string) {
    setPortfolioMode('projectDashboard');
    await backendLogin(email, password);
  }

  async function logout() {
    setPortfolioMode('projectDashboard');
    await backendLogout();
  }

  return {
    accessibleProjects,
    active,
    activeProject,
    activeUser,
    archivedProjects,
    archiveProject,
    authError,
    backendStatus,
    createProject,
    integrityError,
    editorialModelTab,
    memoryTab,
    portfolio,
    toast,
    workspace,
    ...contextChatController,
    ...signalsActions,
    ...postCandidateActions,
    ...productionActions,
    changeAuthorNotes,
    go,
    login,
    logout,
    patchEditorialSetup,
    patchWorkspace,
    resetDemo,
    renameProject,
    runEditorialValidation,
    openProject,
    selectProject,
    selectUser,
    goProjectDashboard,
    portfolioMode,
    setEditorialModelTab,
    setMemoryTab
  };
}
