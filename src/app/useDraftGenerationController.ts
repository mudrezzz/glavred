import { useRef, useState } from 'react';
import { buildDraftRunContext } from '../application/draftRunContext';
import type { DraftGenerationUiState, WorkspaceState } from '../domain/editorialWorkspace';
import { generateBackendDraft } from '../infrastructure/backendDraftClient';
import { blockedInfoFromCompletedRun } from '../infrastructure/draftRunBlocked';
import {
  currentDraftRunStep,
  draftFromCompletedRun,
  startDraftRun,
  waitForDraftRun
} from '../infrastructure/draftRunClient';
import {
  buildApproveBriefWithGeneratedDraftPatch,
  buildApproveBriefWithLocalFallbackDraftPatch
} from './productionDraftActions';
import type { WorkspacePatch } from './useWorkspacePersistence';

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
      const createdRun = await startDraftRun(
        requestWorkspace.postBrief,
        requestWorkspace.editorialModel,
        buildDraftRunContext(requestWorkspace)
      );
      setState({
        status: 'generating',
        startedAt: new Date().toISOString(),
        runId: createdRun.runId
      });
      const completedRun = await waitForDraftRun(createdRun.runId, (run) => {
        const step = currentDraftRunStep(run);
        setState({
          status: 'generating',
          startedAt: new Date().toISOString(),
          runId: run.id,
          step: step?.key ?? null,
          stepLabel: step?.title ?? null
        });
      });
      if (completedRun.status !== 'succeeded') {
        throw new Error(completedRun.error ?? 'DraftRun failed');
      }
      const blockedInfo = blockedInfoFromCompletedRun(completedRun);
      if (blockedInfo) {
        setState({ status: 'blocked', ...blockedInfo });
        return;
      }
      applyGeneratedDraft(
        requestWorkspace,
        draftFromCompletedRun(completedRun),
        'Фабула утверждена, драфт подготовлен через DraftRun'
      );
      setState({ status: 'idle' });
    } catch (error) {
      const message = error instanceof Error ? error.message : 'DraftRun failed';
      if (await tryCompatibilityDraft(requestWorkspace)) return;
      applyLocalFallback(requestWorkspace, message);
    }
  }

  async function tryCompatibilityDraft(requestWorkspace: WorkspaceState) {
    if (!requestWorkspace.postBrief) return false;
    try {
      const result = await generateBackendDraft(
        requestWorkspace.postBrief,
        requestWorkspace.editorialModel
      );
      applyGeneratedDraft(
        requestWorkspace,
        result.draft,
        result.aiRun.fallbackUsed
          ? 'DraftRun недоступен, драфт подготовлен backend fallback'
          : 'DraftRun недоступен, драфт подготовлен compatibility endpoint'
      );
      setState({ status: 'idle' });
      return true;
    } catch {
      return false;
    }
  }

  function applyGeneratedDraft(
    requestWorkspace: WorkspaceState,
    draft: WorkspaceState['postDraft'],
    message: string
  ) {
    if (!draft) return;
    const currentWorkspace = workspaceRef.current.postBrief ? workspaceRef.current : requestWorkspace;
    patchWorkspace(buildApproveBriefWithGeneratedDraftPatch(currentWorkspace, draft), message);
  }

  function applyLocalFallback(requestWorkspace: WorkspaceState, message: string) {
    const currentWorkspace = workspaceRef.current.postBrief ? workspaceRef.current : requestWorkspace;
    patchWorkspace(
      buildApproveBriefWithLocalFallbackDraftPatch(currentWorkspace, message),
      'Фабула утверждена, backend run недоступен: использован локальный fallback'
    );
    setState({ status: 'failed', error: message, fallbackUsed: true });
  }

  return {
    approveCurrentBrief,
    draftGenerationState: state
  };
}
