import {
  createEditorialLearningNote,
  createWorkspaceInsightCard,
  createReleasePackage
} from '../application/editorialServices';
import {
  markLearningNoteCaptured,
  markReleaseReady,
  toggleReleaseChecklistItem,
  type ContentPlanSettings,
  type ContentPlanItem,
  type EditorialLearningNote,
  type PostBriefEditPatch,
  type WorkspaceState
} from '../domain/editorialWorkspace';
import {
  buildApproveBriefAndCreateDraftPatch,
  buildApproveDraftTextPatch,
  buildApprovePlanSlotPatch,
  buildEditCurrentBriefPatch,
  buildReturnEditorialWorkItemToCandidatesPatch,
  buildSaveDraftTextPatch,
  buildSelectEditorialWorkItemPatch,
} from './editorialWorkQueueActions';
import { buildAddInsightToPlanPatch, buildGenerateBroadcastPlanPatch, buildSaveContentPlanSettingsPatch, buildUpdatePlanItemPatch } from './productionPlanActions';
import { createProductionVisualActions } from './productionVisualActions';
import { copyToClipboard, downloadMarkdown, markReleaseManuallyExported } from './releaseExport';
import type { WorkspacePatch } from './useWorkspacePersistence';

type ProductionFlowActionsParams = {
  patchWorkspace: WorkspacePatch;
  workspace: WorkspaceState;
};

export function useProductionFlowActions({ patchWorkspace, workspace }: ProductionFlowActionsParams) {
  const visualActions = createProductionVisualActions({ patchWorkspace, workspace });

  function createInsightFromCurrentSignal() {
    const insightCard = createWorkspaceInsightCard(workspace);
    patchWorkspace({ insightCard }, 'Карточка инсайта собрана');
  }

  function addInsightToPlan() {
    patchWorkspace(
      buildAddInsightToPlanPatch(workspace),
      'Инсайт добавлен в план'
    );
  }

  function generateBroadcastPlan() {
    patchWorkspace(
      buildGenerateBroadcastPlanPatch(workspace),
      'Сетка вещания собрана'
    );
  }

  function saveContentPlanSettings(contentPlanSettings: ContentPlanSettings) {
    patchWorkspace(
      buildSaveContentPlanSettingsPatch(workspace, contentPlanSettings),
      'Настройка сетки сохранена, план нужно пересобрать'
    );
  }

  function updatePlanItemAndWarnings(item: ContentPlanItem) {
    patchWorkspace(buildUpdatePlanItemPatch(workspace, item));
  }

  function approvePlanSlot(itemId: string) {
    patchWorkspace(buildApprovePlanSlotPatch(workspace, itemId), 'Слот сетки утвержден');
  }

  function selectEditorialWorkItem(workItemId: string) {
    patchWorkspace(buildSelectEditorialWorkItemPatch(workspace, workItemId));
  }

  function returnEditorialWorkItemToCandidates(workItemId: string) {
    patchWorkspace(
      buildReturnEditorialWorkItemToCandidatesPatch(workspace, workItemId),
      'Пост возвращен в кандидаты'
    );
  }

  function approveCurrentBrief() {
    if (!workspace.postBrief) return;
    patchWorkspace(
      buildApproveBriefAndCreateDraftPatch(workspace),
      'Фабула утверждена, драфт подготовлен'
    );
  }

  function editCurrentBrief(patch: PostBriefEditPatch) {
    patchWorkspace(
      buildEditCurrentBriefPatch(workspace, patch),
      'Фабула обновлена, драфт нужно пересобрать'
    );
  }

  function updateDraftBody(body: string) {
    patchWorkspace(buildSaveDraftTextPatch(workspace, body));
  }

  function approveCurrentFinalText(body?: string) {
    patchWorkspace(
      buildApproveDraftTextPatch(workspace, body),
      'Текст утвержден · следующий шаг: Визуал'
    );
  }

  function createReleaseFromFinalText() {
    if (!workspace.finalText || workspace.finalText.approvalStatus !== 'approved') return;
    const releasePackage = createReleasePackage(workspace.finalText, workspace.contentPlanItem);
    patchWorkspace({ releasePackage, editorialLearningNote: null }, 'Пакет ручного выпуска подготовлен');
  }

  function toggleReleaseChecklist(itemId: string) {
    if (!workspace.releasePackage) return;
    patchWorkspace({
      releasePackage: toggleReleaseChecklistItem(workspace.releasePackage, itemId),
      editorialLearningNote: null
    });
  }

  function markCurrentReleaseReady() {
    if (!workspace.releasePackage) return;
    const releasePackage = markReleaseReady(workspace.releasePackage);
    patchWorkspace(
      { releasePackage, editorialLearningNote: null },
      releasePackage.status === 'ready' ? 'Выпуск готов' : 'Закройте чеклист выпуска'
    );
  }

  async function copyCurrentFinalText() {
    if (!workspace.releasePackage || !workspace.finalText) return;
    await copyToClipboard(workspace.finalText.body);
    patchWorkspace(
      {
        releasePackage: markReleaseManuallyExported(workspace.releasePackage),
        editorialLearningNote: null
      },
      'Текст скопирован для ручного выпуска'
    );
  }

  function downloadCurrentRelease() {
    if (!workspace.releasePackage) return;
    downloadMarkdown(workspace.releasePackage);
    patchWorkspace(
      {
        releasePackage: markReleaseManuallyExported(workspace.releasePackage),
        editorialLearningNote: null
      },
      'Markdown скачан для ручного выпуска'
    );
  }

  function createLearningNote() {
    if (!workspace.releasePackage || !workspace.finalText) return;
    const editorialLearningNote = createEditorialLearningNote(
      workspace.releasePackage,
      workspace.finalText,
      workspace.contentPlanItem
    );
    patchWorkspace({ editorialLearningNote }, 'Аналитика подготовлена');
  }

  function updateCurrentLearningNote(editorialLearningNote: EditorialLearningNote) {
    patchWorkspace({ editorialLearningNote });
  }

  function captureLearningNote() {
    if (!workspace.editorialLearningNote) return;
    patchWorkspace(
      { editorialLearningNote: markLearningNoteCaptured(workspace.editorialLearningNote) },
      'Редакционные выводы зафиксированы'
    );
  }

  return {
    addInsightToPlan,
    approveCurrentBrief,
    approveCurrentFinalText,
    approvePlanSlot,
    captureLearningNote,
    copyCurrentFinalText,
    createInsightFromCurrentSignal,
    createLearningNote,
    createReleaseFromFinalText,
    downloadCurrentRelease,
    editCurrentBrief,
    generateBroadcastPlan,
    markCurrentReleaseReady,
    returnEditorialWorkItemToCandidates,
    saveContentPlanSettings,
    selectEditorialWorkItem,
    toggleReleaseChecklist,
    updateCurrentLearningNote,
    updateDraftBody,
    updatePlanItemAndWarnings,
    ...visualActions
  };
}
