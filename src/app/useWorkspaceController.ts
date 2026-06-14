import { useEffect, useMemo, useState } from 'react';
import {
  createAuthorMemoryEvent,
  createBroadcastPlan,
  createEditorNotes,
  createEditorialLearningNote,
  createInsightCard,
  createPostBrief,
  createPostDraft,
  createReleasePackage,
  inferAuthorPositionAssertions,
  runEditorialChecks
} from '../application/editorialServices';
import {
  createContextChatReply,
  createContextChatSuggestions,
  createInitialContextChatMessages,
  type AddEditorialRulePayload,
  type AddFabulaPayload,
  type AddTopicPayload,
  type ContextChatMessage,
  type ContextChatSuggestion
} from '../application/contextChat';
import {
  approveContentPlanSlot,
  approveFinalText,
  approvePostBrief,
  approveSignal,
  addRadar,
  applyPlanWarnings,
  archiveSignal,
  correctSignal,
  createEditorialValidationRun,
  deleteRadar,
  detectBroadcastPlanConflicts,
  evaluateSignalAgainstRadarFilters,
  markLearningNoteCaptured,
  markReleaseExported,
  markReleaseReady,
  rejectSignal,
  reviseDraft,
  toggleRadarStatus,
  toggleReleaseChecklistItem,
  updateContentPlanItem,
  updateRadar,
  type AuthorNote,
  type ContentPlanItem,
  type EditorialLearningNote,
  type PostBrief,
  type RadarDefinition,
  type ReleasePackage,
  type SourceSignal,
  type WorkspaceSection,
  type WorkspaceState
} from '../domain/editorialWorkspace';
import { LocalWorkspaceStore } from '../infrastructure/localWorkspaceStore';
import {
  getContextChatScope,
  type ContextChatIntent,
  type ContextChatTab,
  type EditorialModelTab,
  type MemoryInternalTab
} from './contextChatScope';

const store = new LocalWorkspaceStore();

export function useWorkspaceController() {
  const [workspace, setWorkspace] = useState<WorkspaceState>(() => store.load());
  const [toast, setToast] = useState('');
  const [memoryTab, setMemoryTab] = useState<MemoryInternalTab>('feed');
  const [editorialModelTab, setEditorialModelTab] = useState<EditorialModelTab>('publisher');
  const [contextChatOpen, setContextChatOpen] = useState(false);
  const [contextChatTab, setContextChatTab] = useState<ContextChatTab>('chat');
  const [contextChatMessages, setContextChatMessages] = useState<ContextChatMessage[]>(() =>
    createInitialContextChatMessages('memory')
  );
  const [contextChatIntent, setContextChatIntent] = useState<ContextChatIntent | null>(null);
  const [dismissedContextSuggestionIds, setDismissedContextSuggestionIds] = useState<string[]>([]);

  const active = workspace.activeSection;

  useEffect(() => {
    store.save({ ...workspace, updatedAt: new Date().toISOString() });
  }, [workspace]);

  useEffect(() => {
    if (!toast) return undefined;

    const timeoutId = window.setTimeout(() => setToast(''), 2800);
    return () => window.clearTimeout(timeoutId);
  }, [toast]);

  const contextChatScope = getContextChatScope(active, memoryTab, editorialModelTab);
  const contextChatSuggestions = useMemo(
    () => createContextChatSuggestions(workspace, contextChatScope),
    [workspace, contextChatScope]
  );
  const visibleContextChatSuggestions = useMemo(
    () => contextChatSuggestions.filter((suggestion) => !dismissedContextSuggestionIds.includes(suggestion.id)),
    [contextChatSuggestions, dismissedContextSuggestionIds]
  );

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

  function go(section: WorkspaceSection) {
    patchWorkspace({ activeSection: section });
  }

  function applySignalUpdate(nextSignal: SourceSignal, message: string, selectAsCurrent = false) {
    setWorkspace((current) => {
      const sourceSignals = current.sourceSignals.map((signal) =>
        signal.id === nextSignal.id ? nextSignal : signal
      );
      return {
        ...current,
        sourceSignal: selectAsCurrent ? nextSignal : current.sourceSignal,
        sourceSignals,
        updatedAt: new Date().toISOString()
      };
    });
    setToast(message);
  }

  function approveSourceSignal(signal: SourceSignal) {
    applySignalUpdate(approveSignal(signal), 'Сигнал утвержден и выбран для production-flow', true);
  }

  function rejectSourceSignal(signal: SourceSignal) {
    applySignalUpdate(rejectSignal(signal), 'Сигнал отклонен');
  }

  function archiveSourceSignal(signal: SourceSignal) {
    applySignalUpdate(archiveSignal(signal), 'Сигнал отправлен в архив');
  }

  function saveRadar(nextRadar: RadarDefinition, isNew: boolean) {
    setWorkspace((current) => {
      const radars = isNew ? addRadar(current.radars, nextRadar) : updateRadar(current.radars, nextRadar);
      const sourceSignals = current.sourceSignals.map((signal) =>
        signal.radarId === nextRadar.id ? evaluateSignalAgainstRadarFilters(signal, nextRadar, { ...current, radars }) : signal
      );
      const sourceSignal =
        current.sourceSignal.radarId === nextRadar.id
          ? sourceSignals.find((signal) => signal.id === current.sourceSignal.id) ?? current.sourceSignal
          : current.sourceSignal;

      return {
        ...current,
        radars,
        sourceSignal,
        sourceSignals,
        updatedAt: new Date().toISOString()
      };
    });
    setToast(isNew ? 'Радар добавлен' : 'Радар сохранен');
  }

  function removeRadar(radar: RadarDefinition) {
    setWorkspace((current) => ({
      ...current,
      radars: deleteRadar(current.radars, radar.id),
      updatedAt: new Date().toISOString()
    }));
    setToast('Радар удален. Сигналы остаются в истории разбора.');
  }

  function switchRadarStatus(radar: RadarDefinition) {
    const nextRadar = toggleRadarStatus(radar);
    setWorkspace((current) => ({
      ...current,
      radars: updateRadar(current.radars, nextRadar),
      updatedAt: new Date().toISOString()
    }));
    setToast(nextRadar.status === 'paused' ? 'Радар остановлен' : 'Радар запущен');
  }

  function correctSourceSignal(signal: SourceSignal, patch: Partial<SourceSignal>) {
    const nextSignal = correctSignal(signal, patch);
    setWorkspace((current) => {
      const correctionNote: AuthorNote = {
        id: `note-signal-correction-${signal.id}-${Date.now()}`,
        type: 'manualCorrection',
        title: `Правка сигнала: ${signal.title}`,
        body:
          nextSignal.authorCorrection ||
          'Автор уточнил, как этот сигнал связан с темой, фабулой или ценностью.',
        sourceUrl: '',
        tags: ['signal-correction'],
        attachments: [],
        capturedAt: new Date().toISOString(),
        targetType: 'evidence',
        targetId: signal.id,
        targetTitle: signal.title
      };
      const authorNotes = [correctionNote, ...current.authorNotes];
      const authorMemoryEvents = authorNotes.map(createAuthorMemoryEvent);
      return {
        ...current,
        sourceSignals: current.sourceSignals.map((candidate) =>
          candidate.id === nextSignal.id ? nextSignal : candidate
        ),
        sourceSignal: current.sourceSignal.id === nextSignal.id ? nextSignal : current.sourceSignal,
        authorNotes,
        authorMemoryEvents,
        authorPositionAssertions: inferAuthorPositionAssertions(authorNotes, authorMemoryEvents),
        updatedAt: new Date().toISOString()
      };
    });
    setToast('Правка сигнала добавлена в память автора');
  }

  function resetDemo() {
    setWorkspace(store.reset());
    setMemoryTab('feed');
    setEditorialModelTab('publisher');
    setContextChatOpen(false);
    setContextChatTab('chat');
    setContextChatMessages(createInitialContextChatMessages('memory'));
    setContextChatIntent(null);
    setDismissedContextSuggestionIds([]);
    setToast('Демо-сценарий восстановлен');
  }

  function openContextChat(tab: ContextChatTab = 'chat') {
    setContextChatTab(tab);
    setContextChatOpen(true);
  }

  function sendContextChatMessage(text: string) {
    const createdAt = new Date().toISOString();
    const reply = createContextChatReply(workspace, contextChatScope, text);
    setContextChatMessages((messages) => [
      ...messages,
      { id: `ctx-author-free-${createdAt}`, role: 'author', text, createdAt },
      {
        id: `ctx-assistant-free-${createdAt}`,
        role: 'assistant',
        text: reply.text,
        createdAt,
        suggestion: reply.suggestion
      }
    ]);
  }

  function dismissContextChatSuggestion(suggestionId: string) {
    setDismissedContextSuggestionIds((ids) => (ids.includes(suggestionId) ? ids : [...ids, suggestionId]));
  }

  function acceptContextChatSuggestion(suggestion: ContextChatSuggestion) {
    const createdAt = new Date().toISOString();
    setContextChatMessages((messages) => [
      ...messages,
      {
        id: `ctx-author-${suggestion.id}-${createdAt}`,
        role: 'author',
        text: `Принять: ${suggestion.title}`,
        createdAt,
        suggestionId: suggestion.id
      }
    ]);

    if (suggestion.actionType === 'runValidation') {
      setWorkspace((current) => {
        const checkedAt = new Date().toISOString();
        return {
          ...current,
          activeSection: 'editorialModel',
          editorialValidationRun: createEditorialValidationRun(current, checkedAt),
          updatedAt: checkedAt
        };
      });
      setToast('Редакционная модель проверена');
      return;
    }

    if (suggestion.actionType === 'addEditorialRule' && suggestion.payload) {
      setWorkspace((current) => ({ ...current, activeSection: 'editorialModel' }));
      setEditorialModelTab('publisher');
      setContextChatIntent({
        id: `${suggestion.id}-${createdAt}`,
        actionType: 'addEditorialRule',
        payload: suggestion.payload as AddEditorialRulePayload
      });
      return;
    }

    if (suggestion.actionType === 'addTopic' && suggestion.payload) {
      setWorkspace((current) => ({ ...current, activeSection: 'editorialModel' }));
      setEditorialModelTab('topics');
      setContextChatIntent({
        id: `${suggestion.id}-${createdAt}`,
        actionType: 'addTopic',
        payload: suggestion.payload as AddTopicPayload
      });
      return;
    }

    if (suggestion.actionType === 'addFabula' && suggestion.payload) {
      setWorkspace((current) => ({ ...current, activeSection: 'editorialModel' }));
      setEditorialModelTab('fabulas');
      setContextChatIntent({
        id: `${suggestion.id}-${createdAt}`,
        actionType: 'addFabula',
        payload: suggestion.payload as AddFabulaPayload
      });
      return;
    }

    setContextChatMessages((messages) => [
      ...messages,
      {
        id: `ctx-assistant-${suggestion.id}-${createdAt}`,
        role: 'assistant',
        text: 'Эта подсказка пока только для чтения. В следующих слайсах я смогу переводить больше рекомендаций в структурные изменения.',
        createdAt,
        suggestionId: suggestion.id
      }
    ]);
  }

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
        releasePackage: markReleaseExported(markManualExportDone(workspace.releasePackage)),
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
        releasePackage: markReleaseExported(markManualExportDone(workspace.releasePackage)),
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
    active,
    contextChatIntent,
    contextChatMessages,
    contextChatOpen,
    contextChatScope,
    contextChatTab,
    editorialModelTab,
    memoryTab,
    toast,
    visibleContextChatSuggestions,
    workspace,
    acceptContextChatSuggestion,
    addInsightToPlan,
    approveCurrentBrief,
    approveCurrentFinalText,
    approvePlanSlot,
    approveSourceSignal,
    archiveSourceSignal,
    captureLearningNote,
    changeAuthorNotes,
    correctSourceSignal,
    copyCurrentFinalText,
    createDraftFromBrief,
    createInsightFromCurrentSignal,
    createLearningNote,
    createReleaseFromFinalText,
    dismissContextChatSuggestion,
    downloadCurrentRelease,
    generateBroadcastPlan,
    go,
    markCurrentReleaseReady,
    openContextChat,
    patchEditorialSetup,
    patchWorkspace,
    prepareBrief,
    rejectSourceSignal,
    removeRadar,
    resetDemo,
    runEditorialValidation,
    saveRadar,
    sendContextChatMessage,
    setContextChatIntent,
    setContextChatOpen,
    setContextChatTab,
    setEditorialModelTab,
    setMemoryTab,
    switchRadarStatus,
    toggleReleaseChecklist,
    updateCurrentLearningNote,
    updateDraftBody,
    updatePlanItemAndWarnings
  };
}

function markManualExportDone(releasePackage: ReleasePackage): ReleasePackage {
  return {
    ...releasePackage,
    checklist: releasePackage.checklist.map((item) =>
      item.id === 'manual-exported' ? { ...item, done: true } : item
    )
  };
}

async function copyToClipboard(value: string): Promise<void> {
  if (navigator.clipboard?.writeText) {
    try {
      await navigator.clipboard.writeText(value);
    } catch {
      // Markdown preview stays visible for manual copy when clipboard access is unavailable.
    }
  }
}

function downloadMarkdown(releasePackage: ReleasePackage): void {
  if (!window.URL?.createObjectURL) return;

  const blob = new Blob([releasePackage.markdown], { type: 'text/markdown;charset=utf-8' });
  const url = window.URL.createObjectURL(blob);
  const link = document.createElement('a');
  link.href = url;
  link.download = `${releasePackage.id}.md`;
  link.click();
  window.URL.revokeObjectURL(url);
}
