import {
  createEditorNotes,
  createEditorialLearningNote,
  createWorkspaceInsightCard,
  createPostDraft,
  createReleasePackage,
  runEditorialChecks
} from '../application/editorialServices';
import {
  approveFinalText,
  approvePostBrief,
  markLearningNoteCaptured,
  markReleaseReady,
  reviseDraft,
  toggleReleaseChecklistItem,
  type ContentPlanSettings,
  type ContentPlanItem,
  type EditorialLearningNote,
  type WorkspaceState
} from '../domain/editorialWorkspace';
import { buildApprovePlanSlotPatch, buildReturnEditorialWorkItemToCandidatesPatch, buildSelectEditorialWorkItemPatch, withEditorialWorkItemSync } from './editorialWorkQueueActions';
import { buildAddInsightToPlanPatch, buildGenerateBroadcastPlanPatch, buildSaveContentPlanSettingsPatch, buildUpdatePlanItemPatch } from './productionPlanActions';
import { copyToClipboard, downloadMarkdown, markReleaseManuallyExported } from './releaseExport';
import type { WorkspacePatch } from './useWorkspacePersistence';

type ProductionFlowActionsParams = {
  patchWorkspace: WorkspacePatch;
  workspace: WorkspaceState;
};

export function useProductionFlowActions({ patchWorkspace, workspace }: ProductionFlowActionsParams) {
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
      withEditorialWorkItemSync(workspace, { postBrief: approvePostBrief(workspace.postBrief) }),
      'Фабула утверждена'
    );
  }

  function createDraftFromBrief() {
    if (!workspace.postBrief || workspace.postBrief.approvalStatus !== 'approved') return;
    const postDraft = createPostDraft(workspace.postBrief, workspace.editorialModel);
    const editorialChecks = runEditorialChecks(postDraft, workspace.postBrief, workspace.editorialModel);
    const editorNotes = createEditorNotes(editorialChecks);
    patchWorkspace(
      withEditorialWorkItemSync(workspace, { postDraft, editorialChecks, editorNotes, finalText: null }),
      'Драфт подготовлен для редакторских проверок'
    );
  }

  function updateDraftBody(body: string) {
    if (!workspace.postDraft || !workspace.postBrief) return;
    const postDraft = reviseDraft(workspace.postDraft, body);
    const editorialChecks = runEditorialChecks(postDraft, workspace.postBrief, workspace.editorialModel);
    const editorNotes = createEditorNotes(editorialChecks);
    patchWorkspace(withEditorialWorkItemSync(workspace, {
      postDraft,
      editorialChecks,
      editorNotes,
      finalText: null,
      releasePackage: null,
      editorialLearningNote: null
    }));
  }

  function approveCurrentFinalText() {
    if (!workspace.postDraft) return;
    const finalText = approveFinalText(workspace.postDraft);
    patchWorkspace(
      withEditorialWorkItemSync(workspace, { finalText, releasePackage: null, editorialLearningNote: null }),
      'Финальный текст утвержден'
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
    createDraftFromBrief,
    createInsightFromCurrentSignal,
    createLearningNote,
    createReleaseFromFinalText,
    downloadCurrentRelease,
    generateBroadcastPlan,
    markCurrentReleaseReady,
    returnEditorialWorkItemToCandidates,
    saveContentPlanSettings,
    selectEditorialWorkItem,
    toggleReleaseChecklist,
    updateCurrentLearningNote,
    updateDraftBody,
    updatePlanItemAndWarnings
  };
}
