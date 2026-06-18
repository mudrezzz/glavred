import type { PostVisualEditPatch, WorkspaceState } from '../domain/editorialWorkspace';
import {
  buildApproveVisualPatch,
  buildPrepareMemeReferencesPatch,
  buildPrepareMemeRemixVariantsPatch,
  buildPrepareVisualVariantsPatch,
  buildSaveVisualDraftPatch,
  buildSelectMemeReferencePatch,
  buildSelectVisualVariantPatch
} from './editorialWorkQueueActions';
import type { WorkspacePatch } from './useWorkspacePersistence';

type ProductionVisualActionsParams = {
  patchWorkspace: WorkspacePatch;
  workspace: WorkspaceState;
};

export function createProductionVisualActions({ patchWorkspace, workspace }: ProductionVisualActionsParams) {
  function saveCurrentVisualDraft(patch: PostVisualEditPatch) {
    patchWorkspace(buildSaveVisualDraftPatch(workspace, patch), 'Визуал сохранен');
  }

  function approveCurrentVisual(patch: PostVisualEditPatch) {
    patchWorkspace(buildApproveVisualPatch(workspace, patch), 'Визуал утвержден');
  }

  function prepareCurrentVisualVariants(patch: PostVisualEditPatch) {
    patchWorkspace(buildPrepareVisualVariantsPatch(workspace, patch), 'Варианты визуала подготовлены');
  }

  function prepareCurrentMemeReferences(patch: PostVisualEditPatch) {
    patchWorkspace(buildPrepareMemeReferencesPatch(workspace, patch), 'Мемы для ремикса подготовлены');
  }

  function selectCurrentMemeReference(referenceId: string) {
    patchWorkspace(buildSelectMemeReferencePatch(workspace, referenceId), 'Мем для ремикса выбран');
  }

  function prepareCurrentMemeRemixVariants() {
    patchWorkspace(buildPrepareMemeRemixVariantsPatch(workspace), 'Кастом-варианты подготовлены');
  }

  function selectCurrentVisualVariant(variantId: string) {
    patchWorkspace(buildSelectVisualVariantPatch(workspace, variantId), 'Вариант визуала выбран');
  }

  return {
    approveCurrentVisual,
    prepareCurrentMemeReferences,
    prepareCurrentMemeRemixVariants,
    prepareCurrentVisualVariants,
    saveCurrentVisualDraft,
    selectCurrentMemeReference,
    selectCurrentVisualVariant
  };
}
