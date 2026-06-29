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
  buildApproveDraftTextPatch,
  buildAddHumanCommentRevisionPatch,
  buildApprovePlanSlotPatch,
  buildEditCurrentBriefPatch,
  buildReturnEditorialWorkItemToCandidatesPatch,
  buildSaveDraftTextPatch,
  buildSelectDraftVersionPatch,
  buildSelectEditorialWorkItemPatch,
} from './editorialWorkQueueActions';
import { buildAddInsightToPlanPatch, buildGenerateBroadcastPlanPatch, buildSaveContentPlanSettingsPatch, buildUpdatePlanItemPatch } from './productionPlanActions';
import { createProductionVisualActions } from './productionVisualActions';
import { copyToClipboard, downloadMarkdown, markReleaseManuallyExported } from './releaseExport';
import type { WorkspacePatch } from './useWorkspacePersistence';
import { useDraftGenerationController } from './useDraftGenerationController';
import { reviseDraftWithEditorComment } from '../infrastructure/draftCommentRevisionClient';
import { loadEditorDecisionTraceSummary } from '../infrastructure/editorDecisionTraceClient';

type ProductionFlowActionsParams = {
  patchWorkspace: WorkspacePatch;
  workspace: WorkspaceState;
};

export function useProductionFlowActions({ patchWorkspace, workspace }: ProductionFlowActionsParams) {
  const visualActions = createProductionVisualActions({ patchWorkspace, workspace });
  const draftGeneration = useDraftGenerationController({ patchWorkspace, workspace });

  function createInsightFromCurrentSignal() {
    const insightCard = createWorkspaceInsightCard(workspace);
    patchWorkspace({ insightCard }, 'РљР°СЂС‚РѕС‡РєР° РёРЅСЃР°Р№С‚Р° СЃРѕР±СЂР°РЅР°');
  }

  function addInsightToPlan() {
    patchWorkspace(
      buildAddInsightToPlanPatch(workspace),
      'РРЅСЃР°Р№С‚ РґРѕР±Р°РІР»РµРЅ РІ РїР»Р°РЅ'
    );
  }

  function generateBroadcastPlan() {
    patchWorkspace(
      buildGenerateBroadcastPlanPatch(workspace),
      'РЎРµС‚РєР° РІРµС‰Р°РЅРёСЏ СЃРѕР±СЂР°РЅР°'
    );
  }

  function saveContentPlanSettings(contentPlanSettings: ContentPlanSettings) {
    patchWorkspace(
      buildSaveContentPlanSettingsPatch(workspace, contentPlanSettings),
      'РќР°СЃС‚СЂРѕР№РєР° СЃРµС‚РєРё СЃРѕС…СЂР°РЅРµРЅР°, РїР»Р°РЅ РЅСѓР¶РЅРѕ РїРµСЂРµСЃРѕР±СЂР°С‚СЊ'
    );
  }

  function updatePlanItemAndWarnings(item: ContentPlanItem) {
    patchWorkspace(buildUpdatePlanItemPatch(workspace, item));
  }

  function approvePlanSlot(itemId: string) {
    patchWorkspace(buildApprovePlanSlotPatch(workspace, itemId), 'РЎР»РѕС‚ СЃРµС‚РєРё СѓС‚РІРµСЂР¶РґРµРЅ');
  }

  function selectEditorialWorkItem(workItemId: string) {
    patchWorkspace(buildSelectEditorialWorkItemPatch(workspace, workItemId));
  }

  function returnEditorialWorkItemToCandidates(workItemId: string) {
    patchWorkspace(
      buildReturnEditorialWorkItemToCandidatesPatch(workspace, workItemId),
      'РџРѕСЃС‚ РІРѕР·РІСЂР°С‰РµРЅ РІ РєР°РЅРґРёРґР°С‚С‹'
    );
  }

  function editCurrentBrief(patch: PostBriefEditPatch) {
    patchWorkspace(
      buildEditCurrentBriefPatch(workspace, patch),
      'Р¤Р°Р±СѓР»Р° РѕР±РЅРѕРІР»РµРЅР°, РґСЂР°С„С‚ РЅСѓР¶РЅРѕ РїРµСЂРµСЃРѕР±СЂР°С‚СЊ'
    );
  }

  function updateDraftBody(body: string) {
    patchWorkspace(buildSaveDraftTextPatch(workspace, body), 'Правка сохранена как новая версия');
  }

  function selectDraftVersion(versionId: string) {
    patchWorkspace(buildSelectDraftVersionPatch(workspace, versionId));
  }

  async function reviseCurrentDraftWithComment(editorComment: string) {
    if (!workspace.postDraft) return;
    try {
      const revision = await reviseDraftWithEditorComment(workspace.postDraft, editorComment);
      patchWorkspace(
        buildAddHumanCommentRevisionPatch(workspace, {
          title: revision.title,
          body: revision.body,
          editorComment,
          revisionSummary: revision.revisionSummary,
          aiRunId: revision.aiRunId
        }),
        'Новая версия создана по комментарию редактора'
      );
    } catch (error) {
      patchWorkspace({}, error instanceof Error ? error.message : 'Не удалось создать новую версию');
      throw error;
    }
  }

  async function approveCurrentFinalText(versionId?: string) {
    const machineTrace = workspace.postDraft
      ? await loadEditorDecisionTraceSummary(workspace.postDraft)
      : undefined;
    patchWorkspace(
      buildApproveDraftTextPatch(workspace, versionId, machineTrace),
      'РўРµРєСЃС‚ СѓС‚РІРµСЂР¶РґРµРЅ В· СЃР»РµРґСѓСЋС‰РёР№ С€Р°Рі: Р’РёР·СѓР°Р»'
    );
  }

  function createReleaseFromFinalText() {
    if (!workspace.finalText || workspace.finalText.approvalStatus !== 'approved') return;
    const releasePackage = createReleasePackage(workspace.finalText, workspace.contentPlanItem);
    patchWorkspace({ releasePackage, editorialLearningNote: null }, 'РџР°РєРµС‚ СЂСѓС‡РЅРѕРіРѕ РІС‹РїСѓСЃРєР° РїРѕРґРіРѕС‚РѕРІР»РµРЅ');
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
      releasePackage.status === 'ready' ? 'Р’С‹РїСѓСЃРє РіРѕС‚РѕРІ' : 'Р—Р°РєСЂРѕР№С‚Рµ С‡РµРєР»РёСЃС‚ РІС‹РїСѓСЃРєР°'
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
      'РўРµРєСЃС‚ СЃРєРѕРїРёСЂРѕРІР°РЅ РґР»СЏ СЂСѓС‡РЅРѕРіРѕ РІС‹РїСѓСЃРєР°'
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
      'Markdown СЃРєР°С‡Р°РЅ РґР»СЏ СЂСѓС‡РЅРѕРіРѕ РІС‹РїСѓСЃРєР°'
    );
  }

  function createLearningNote() {
    if (!workspace.releasePackage || !workspace.finalText) return;
    const editorialLearningNote = createEditorialLearningNote(
      workspace.releasePackage,
      workspace.finalText,
      workspace.contentPlanItem
    );
    patchWorkspace({ editorialLearningNote }, 'РђРЅР°Р»РёС‚РёРєР° РїРѕРґРіРѕС‚РѕРІР»РµРЅР°');
  }

  function updateCurrentLearningNote(editorialLearningNote: EditorialLearningNote) {
    patchWorkspace({ editorialLearningNote });
  }

  function captureLearningNote() {
    if (!workspace.editorialLearningNote) return;
    patchWorkspace(
      { editorialLearningNote: markLearningNoteCaptured(workspace.editorialLearningNote) },
      'Р РµРґР°РєС†РёРѕРЅРЅС‹Рµ РІС‹РІРѕРґС‹ Р·Р°С„РёРєСЃРёСЂРѕРІР°РЅС‹'
    );
  }

  return {
    addInsightToPlan,
    approveCurrentBrief: draftGeneration.approveCurrentBrief,
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
    selectDraftVersion,
    selectEditorialWorkItem,
    toggleReleaseChecklist,
    updateCurrentLearningNote,
    updateDraftBody,
    reviseCurrentDraftWithComment,
    updatePlanItemAndWarnings,
    draftGenerationState: draftGeneration.draftGenerationState,
    ...visualActions
  };
}
