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
    changeAuthorNotes,
    patchEditorialSetup,
    patchWorkspace,
    resetWorkspace,
    runEditorialValidation,
    setToast,
    setWorkspace,
    toast,
    workspace
  } = useWorkspacePersistence();
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
  const signalsActions = useSignalsWorkspaceActions({ setToast, setWorkspace });
  const postCandidateActions = usePostCandidateWorkspaceActions({ setToast, setWorkspace });
  const productionActions = useProductionFlowActions({ patchWorkspace, workspace });

  function go(section: WorkspaceSection) {
    patchWorkspace({ activeSection: section });
  }

  function resetDemo() {
    resetWorkspace();
    setMemoryTab('feed');
    setEditorialModelTab('publisher');
    contextChatController.resetContextChat();
  }

  return {
    active,
    editorialModelTab,
    memoryTab,
    toast,
    workspace,
    ...contextChatController,
    ...signalsActions,
    ...postCandidateActions,
    ...productionActions,
    changeAuthorNotes,
    go,
    patchEditorialSetup,
    patchWorkspace,
    resetDemo,
    runEditorialValidation,
    setEditorialModelTab,
    setMemoryTab
  };
}
