import {
  createBroadcastPlan,
  createEditorNotes,
  createEditorialLearningNote,
  createInsightCard,
  createPostBrief,
  createPostDraft,
  createReleasePackage,
  runEditorialChecks
} from '../application/editorialServices';
import {
  approveContentPlanSlot,
  approveFinalText,
  approvePostBrief,
  applyPlanWarnings,
  detectBroadcastPlanConflicts,
  markLearningNoteCaptured,
  markReleaseReady,
  reviseDraft,
  toggleReleaseChecklistItem,
  updateContentPlanItem,
  type ContentPlanItem,
  type EditorialLearningNote,
  type WorkspaceState
} from '../domain/editorialWorkspace';
import {
  copyToClipboard,
  downloadMarkdown,
  markReleaseManuallyExported
} from './releaseExport';
import type { WorkspacePatch } from './useWorkspacePersistence';

type ProductionFlowActionsParams = {
  patchWorkspace: WorkspacePatch;
  workspace: WorkspaceState;
};

export function useProductionFlowActions({ patchWorkspace, workspace }: ProductionFlowActionsParams) {
  function createInsightFromCurrentSignal() {
    const insightCard = createInsightCard(
      workspace.sourceSignal,
      workspace.editorialModel,
      workspace.topics,
      workspace.fabulas,
      workspace.topicFabulaMatrix
    );
    patchWorkspace({ insightCard }, 'Карточка инсайта собрана');
  }

  function addInsightToPlan() {
    const insightCard =
      workspace.insightCard ??
      createInsightCard(
        workspace.sourceSignal,
        workspace.editorialModel,
        workspace.topics,
        workspace.fabulas,
        workspace.topicFabulaMatrix
      );
    const nextWorkspace = { ...workspace, insightCard };
    const generatedItems = createBroadcastPlan(nextWorkspace);
    const planWeightWarnings = detectBroadcastPlanConflicts(nextWorkspace, generatedItems);
    const contentPlanItems = applyPlanWarnings(generatedItems, planWeightWarnings);
    patchWorkspace(
      { insightCard, contentPlanItems, planWeightWarnings, contentPlanItem: null, activeSection: 'plan' },
      'Инсайт добавлен в план'
    );
  }

  function generateBroadcastPlan() {
    const insightCard =
      workspace.insightCard ??
      createInsightCard(
        workspace.sourceSignal,
        workspace.editorialModel,
        workspace.topics,
        workspace.fabulas,
        workspace.topicFabulaMatrix
      );
    const nextWorkspace = { ...workspace, insightCard };
    const generatedItems = createBroadcastPlan(nextWorkspace);
    const planWeightWarnings = detectBroadcastPlanConflicts(nextWorkspace, generatedItems);
    const contentPlanItems = applyPlanWarnings(generatedItems, planWeightWarnings);
    patchWorkspace(
      { insightCard, contentPlanItems, planWeightWarnings, contentPlanItem: null },
      'Сетка вещания собрана'
    );
  }

  function updatePlanItemAndWarnings(item: ContentPlanItem) {
    const updatedItems = updateContentPlanItem(workspace.contentPlanItems, item);
    const planWeightWarnings = detectBroadcastPlanConflicts(workspace, updatedItems);
    const contentPlanItems = applyPlanWarnings(updatedItems, planWeightWarnings);
    patchWorkspace({ contentPlanItems, planWeightWarnings });
  }

  function approvePlanSlot(itemId: string) {
    const approvedItems = approveContentPlanSlot(workspace.contentPlanItems, itemId);
    const planWeightWarnings = detectBroadcastPlanConflicts(workspace, approvedItems);
    const contentPlanItems = applyPlanWarnings(approvedItems, planWeightWarnings);
    const contentPlanItem = contentPlanItems.find((item) => item.id === itemId) ?? null;
    patchWorkspace({ contentPlanItems, contentPlanItem, planWeightWarnings }, 'Слот сетки утвержден');
  }

  function prepareBrief(item: ContentPlanItem) {
    const insightCard =
      workspace.insightCard ??
      createInsightCard(
        workspace.sourceSignal,
        workspace.editorialModel,
        workspace.topics,
        workspace.fabulas,
        workspace.topicFabulaMatrix
      );
    const postBrief = createPostBrief(
      item,
      insightCard,
      workspace.editorialModel,
      workspace.topics,
      workspace.fabulas,
      workspace.topicFabulaMatrix
    );
    patchWorkspace({ insightCard, contentPlanItem: item, postBrief, activeSection: 'brief' }, 'Фабула поста подготовлена');
  }

  function approveCurrentBrief() {
    if (!workspace.postBrief) return;
    patchWorkspace({ postBrief: approvePostBrief(workspace.postBrief) }, 'Фабула утверждена');
  }

  function createDraftFromBrief() {
    if (!workspace.postBrief || workspace.postBrief.approvalStatus !== 'approved') return;
    const postDraft = createPostDraft(workspace.postBrief, workspace.editorialModel);
    const editorialChecks = runEditorialChecks(postDraft, workspace.postBrief, workspace.editorialModel);
    const editorNotes = createEditorNotes(editorialChecks);
    patchWorkspace({ postDraft, editorialChecks, editorNotes, finalText: null }, 'Драфт подготовлен для редакторских проверок');
  }

  function updateDraftBody(body: string) {
    if (!workspace.postDraft || !workspace.postBrief) return;
    const postDraft = reviseDraft(workspace.postDraft, body);
    const editorialChecks = runEditorialChecks(postDraft, workspace.postBrief, workspace.editorialModel);
    const editorNotes = createEditorNotes(editorialChecks);
    patchWorkspace({
      postDraft,
      editorialChecks,
      editorNotes,
      finalText: null,
      releasePackage: null,
      editorialLearningNote: null
    });
  }

  function approveCurrentFinalText() {
    if (!workspace.postDraft) return;
    const finalText = approveFinalText(workspace.postDraft);
    patchWorkspace({ finalText, releasePackage: null, editorialLearningNote: null }, 'Финальный текст утвержден');
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
    prepareBrief,
    toggleReleaseChecklist,
    updateCurrentLearningNote,
    updateDraftBody,
    updatePlanItemAndWarnings
  };
}
