import { useRef, useState } from 'react';
import { generateBackendDraft } from '../infrastructure/backendDraftClient';
import type { WorkspacePatch } from './useWorkspacePersistence';
import type { DraftGenerationUiState, WorkspaceState } from '../domain/editorialWorkspace';
import {
  buildApproveBriefWithGeneratedDraftPatch,
  buildApproveBriefWithLocalFallbackDraftPatch
} from './productionDraftActions';

export function useDraftGenerationController({
  patchWorkspace,
  workspace
}: {
  patchWorkspace: WorkspacePatch;
  workspace: WorkspaceState;
}) {
  const [state, setState] = useState<DraftGenerationUiState>({ status: 'idle' });
  const workspaceRef = useRef(workspace);
  workspaceRef.current = workspace;

  async function approveCurrentBrief() {
    const requestWorkspace = workspaceRef.current;
    if (!requestWorkspace.postBrief || state.status === 'generating') return;
    setState({ status: 'generating', startedAt: new Date().toISOString() });
    try {
      const result = await generateBackendDraft(requestWorkspace.postBrief, requestWorkspace.editorialModel);
      const currentWorkspace = workspaceRef.current.postBrief
        ? workspaceRef.current
        : requestWorkspace;
      patchWorkspace(
        buildApproveBriefWithGeneratedDraftPatch(currentWorkspace, result.draft),
        result.aiRun.fallbackUsed
          ? 'Фабула утверждена, драфт подготовлен backend fallback'
          : 'Фабула утверждена, драфт подготовлен через OpenRouter'
      );
      setState({ status: 'idle' });
    } catch (error) {
      const message = error instanceof Error ? error.message : 'Backend draft generation failed';
      const currentWorkspace = workspaceRef.current.postBrief
        ? workspaceRef.current
        : requestWorkspace;
      patchWorkspace(
        buildApproveBriefWithLocalFallbackDraftPatch(currentWorkspace, message),
        'Фабула утверждена, backend недоступен: использован локальный fallback'
      );
      setState({ status: 'failed', error: message, fallbackUsed: true });
    }
  }

  return {
    approveCurrentBrief,
    draftGenerationState: state
  };
}
