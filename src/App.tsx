import { useEffect, useMemo, useState, type FormEvent } from 'react';
import {
  createAuthorMemoryEvent,
  createBroadcastPlan,
  createContentPlanItem,
  createEditorNotes,
  createEditorialLearningNote,
  createInsightCard,
  createPostBrief,
  createPostDraft,
  createReleasePackage,
  inferAuthorPositionAssertions,
  runEditorialChecks
} from './application/editorialServices';
import {
  createContextChatReply,
  createContextChatSuggestions,
  createInitialContextChatMessages,
  mapWorkspaceSectionToProductionScope,
  type AddEditorialRulePayload,
  type AddFabulaPayload,
  type AddTopicPayload,
  type ContextChatActionType,
  type ContextChatMessage,
  type ContextChatScope,
  type ContextChatSuggestion
} from './application/contextChat';
import {
  approveFinalText,
  approveContentPlanSlot,
  approvePlanItem,
  approvePostBrief,
  applyPlanWarnings,
  approveSignal,
  acceptCandidateToArchive,
  acceptCandidateToMemory,
  addFabula,
  addTopic,
  archiveSignal,
  bulkAcceptCandidatesToArchive,
  bulkRejectCandidates,
  completeTopicFabulaMatrix,
  createEditorialRule,
  createEditorialValidationRun,
  createFabulaDraft,
  createTopicDraft,
  correctSignal,
  deleteFabula,
  deleteEditorialRule,
  deleteTopic,
  detectBroadcastPlanConflicts,
  filterImportCandidates,
  getTopicFabulaWarnings,
  groupImportCandidates,
  ignoreCandidateForEvidence,
  markCandidateAcceptedToArchive,
  markCandidateAcceptedToMemory,
  markLearningNoteCaptured,
  markReleaseExported,
  markReleaseReady,
  normalizeWeightRange,
  rejectSignal,
  rejectCandidate,
  reviseDraft,
  toggleReleaseChecklistItem,
  undoLastBulkImportAction,
  updateEditorialRule,
  updateContentPlanItem,
  updateLearningNote,
  validatorDefinitionTitle,
  type ArchiveRecord,
  type AuthorExternalSource,
  type AuthorAttachment,
  type AuthorNote,
  type AuthorNoteType,
  type AuthorPositionAssertion,
  type BulkImportAction,
  type ContentPlanItem,
  type EditorialCheck,
  type EditorialLearningNote,
  type EditorialModel,
  type EditorialRule,
  type EditorialRuleGroup,
  type EditorialValidationRun,
  type EvidencePolicy,
  type Fabula,
  type FinalText,
  type ImportedMemoryCandidate,
  type ImportCandidateFilters,
  type ImportCandidateGroupType,
  type ImportReviewStatus,
  type ImportRiskLevel,
  type ManualMetricSnapshot,
  type PostBrief,
  type PostDraft,
  type ProjectProfile,
  type RadarDefinition,
  type ReleasePackage,
  type SignalReviewStatus,
  type SourceSignal,
  type Topic,
  type TopicFabulaMatrixEntry,
  type ValidatorResult,
  type WeightRange,
  type WorkspaceSection,
  type WorkspaceState
} from './domain/editorialWorkspace';
import { LocalWorkspaceStore } from './infrastructure/localWorkspaceStore';

const store = new LocalWorkspaceStore();

type ContextChatIntent =
  | { id: string; actionType: 'addEditorialRule'; payload: AddEditorialRulePayload }
  | { id: string; actionType: 'addTopic'; payload: AddTopicPayload }
  | { id: string; actionType: 'addFabula'; payload: AddFabulaPayload };
type ContextChatTab = 'chat' | 'suggestions';

const NAV: Array<{ id: WorkspaceSection; icon: string; label: string; count?: string; disabled?: boolean }> = [
  { id: 'memory', icon: 'memory', label: 'Память автора' },
  { id: 'editorialModel', icon: 'model', label: 'Редакционная модель' },
  { id: 'signals', icon: 'radar', label: 'Сигналы' },
  { id: 'plan', icon: 'plan', label: 'План', count: '1' },
  { id: 'edit', icon: 'edit', label: 'Редактура' },
  { id: 'release', icon: 'release', label: 'Выпуск' },
  { id: 'analytics', icon: 'analytics', label: 'Аналитика' }
];

const TITLES: Record<WorkspaceSection, [string, string]> = {
  memory: ['Память автора', 'Заметки -> позиция автора'],
  editorialModel: ['Редакционная модель', 'Правила и контекст блога'],
  signals: ['Сигналы', 'Радары -> сигналы -> кандидаты'],
  plan: ['План', 'HITL · Gate 1'],
  brief: ['Фабула поста', 'HITL · Gate 2'],
  edit: ['Редактура', 'HITL · Gate 3'],
  release: ['Выпуск', 'Manual export'],
  analytics: ['Аналитика', 'Редакционные выводы']
};

function Icon({ name, size = 18 }: { name: string; size?: number }) {
  const paths: Record<string, string> = {
    memory:
      '<path d="M15 18h-5"/><path d="M18 14h-8"/><path d="M14 10h-4"/><path d="M20 6.5V20a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h8.5z"/><path d="M14 2v5h5"/>',
    model:
      '<path d="M12 7v14"/><path d="M3 18a1 1 0 0 1-1-1V4a1 1 0 0 1 1-1h5a4 4 0 0 1 4 4 4 4 0 0 1 4-4h5a1 1 0 0 1 1 1v13a1 1 0 0 1-1 1h-6a3 3 0 0 0-3 3 3 3 0 0 0-3-3z"/>',
    radar:
      '<path d="M19.07 4.93A10 10 0 0 0 6.99 3.34"/><path d="M4 6h.01"/><path d="M2.29 9.62A10 10 0 1 0 21.31 8.35"/><path d="M16.24 7.76A6 6 0 1 0 8.23 16.67"/><circle cx="12" cy="12" r="2"/><path d="m13.41 10.59 5.66-5.66"/>',
    plan:
      '<path d="M8 2v4"/><path d="M16 2v4"/><rect width="18" height="18" x="3" y="4" rx="2"/><path d="M3 10h18"/><path d="M8 14h.01"/><path d="M12 14h.01"/><path d="M16 14h.01"/>',
    brief:
      '<path d="M15 14c.2-1 .7-1.7 1.5-2.5 1-.9 1.5-2.2 1.5-3.5A6 6 0 0 0 6 8c0 1 .2 2.2 1.5 3.5.7.7 1.3 1.5 1.5 2.5"/><path d="M9 18h6"/><path d="M10 22h4"/>',
    edit:
      '<path d="M12.5 22H18a2 2 0 0 0 2-2V7l-5-5H6a2 2 0 0 0-2 2v9.5"/><path d="M14 2v4a2 2 0 0 0 2 2h4"/><path d="M13.4 15.6a1 1 0 1 0-3-3l-5 5a2 2 0 0 0-.5.9l-.8 2.9a.5.5 0 0 0 .6.6l2.9-.8a2 2 0 0 0 .9-.5z"/>',
    release:
      '<path d="M14.5 21.7a.5.5 0 0 0 .9 0l6.5-19a.5.5 0 0 0-.6-.6l-19 6.5a.5.5 0 0 0 0 .9l7.9 3.2a2 2 0 0 1 1.1 1.1z"/><path d="m21.9 2.1-10.9 11"/>',
    analytics: '<path d="M16 7h6v6"/><path d="m22 7-8.5 8.5-5-5L2 17"/>',
    search: '<circle cx="11" cy="11" r="8"/><path d="m21 21-4.3-4.3"/>',
    bell:
      '<path d="M10.3 21a2 2 0 0 0 3.4 0"/><path d="M3.3 15.3A1 1 0 0 0 4 17h16a1 1 0 0 0 .7-1.7C19.4 14 18 12.5 18 8A6 6 0 0 0 6 8c0 4.5-1.4 6-2.7 7.3"/>',
    check: '<path d="M20 6 9 17l-5-5"/>',
    plus: '<path d="M5 12h14"/><path d="M12 5v14"/>',
    minus: '<path d="M5 12h14"/>',
    mic:
      '<path d="M12 2a3 3 0 0 0-3 3v7a3 3 0 0 0 6 0V5a3 3 0 0 0-3-3Z"/><path d="M19 10v2a7 7 0 0 1-14 0v-2"/><path d="M12 19v3"/>',
    reset: '<path d="M3 12a9 9 0 1 0 3-6.7"/><path d="M3 3v6h6"/>',
    spark: '<path d="m12 3 1.8 5.2L19 10l-5.2 1.8L12 17l-1.8-5.2L5 10l5.2-1.8Z"/><path d="M19 16v4"/><path d="M21 18h-4"/>',
    close: '<path d="M18 6 6 18"/><path d="m6 6 12 12"/>',
    caret: '<path d="M4 16 L12 7 L20 16"/>'
  };

  return (
    <svg
      width={size}
      height={size}
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="2"
      strokeLinecap="round"
      strokeLinejoin="round"
      dangerouslySetInnerHTML={{ __html: paths[name] ?? '' }}
    />
  );
}

export function App() {
  const [workspace, setWorkspace] = useState<WorkspaceState>(() => store.load());
  const active = workspace.activeSection;
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
    if (message) {
      setToast(message);
    }
  }

  function patchEditorialSetup(patch: Partial<WorkspaceState>, message?: string) {
    setWorkspace((current) => ({
      ...current,
      ...patch,
      editorialSetupRevision: (current.editorialSetupRevision ?? 0) + 1,
      updatedAt: new Date().toISOString()
    }));
    if (message) {
      setToast(message);
    }
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
      {
        id: `ctx-author-free-${createdAt}`,
        role: 'author',
        text,
        createdAt
      },
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
      setEditorialModelTab(editorialModelTab === 'publisher' ? 'publisher' : editorialModelTab);
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

  return (
    <div className="app">
      <Sidebar active={active} onNav={go} workspace={workspace} />
      <main className="main">
        <Topbar
          active={active}
          chatOpen={contextChatOpen}
          suggestionCount={visibleContextChatSuggestions.length}
          onOpenChat={() => openContextChat('chat')}
          onReset={resetDemo}
        />
        <div className="scroll">
          {active === 'memory' && (
            <AuthorMemoryView
              activeTab={memoryTab}
              workspace={workspace}
              onChangeTab={setMemoryTab}
              onPatchWorkspace={patchWorkspace}
              onChangeNotes={(authorNotes, message) => {
                const authorMemoryEvents = authorNotes.map(createAuthorMemoryEvent);
                const authorPositionAssertions = inferAuthorPositionAssertions(authorNotes, authorMemoryEvents);
                patchWorkspace(
                  { authorNotes, authorMemoryEvents, authorPositionAssertions },
                  message
                );
              }}
            />
          )}
          {active === 'editorialModel' && (
            <EditorialModelView
              activeTab={editorialModelTab}
              chatIntent={contextChatIntent}
              workspace={workspace}
              model={workspace.editorialModel}
              projectProfile={workspace.projectProfile}
              editorialRules={workspace.editorialRules}
              topics={workspace.topics}
              fabulas={workspace.fabulas}
              matrix={workspace.topicFabulaMatrix}
              onModelChange={(editorialModel) => patchEditorialSetup({ editorialModel })}
              onProjectProfileChange={(projectProfile) => patchEditorialSetup({ projectProfile })}
              onEditorialRulesChange={(editorialRules) => patchEditorialSetup({ editorialRules })}
              onTopicsChange={(topics) => patchEditorialSetup({ topics })}
              onFabulasChange={(fabulas) => patchEditorialSetup({ fabulas })}
              onMatrixChange={(topicFabulaMatrix) => patchEditorialSetup({ topicFabulaMatrix })}
              onTopicsAndMatrixChange={(topics, topicFabulaMatrix) =>
                patchEditorialSetup({ topics, topicFabulaMatrix })
              }
              onFabulasAndMatrixChange={(fabulas, topicFabulaMatrix) =>
                patchEditorialSetup({ fabulas, topicFabulaMatrix })
              }
              onChangeTab={setEditorialModelTab}
              onChatIntentConsumed={() => setContextChatIntent(null)}
              onRunValidation={runEditorialValidation}
            />
          )}
          {active === 'signals' && (
            <SignalsView
              workspace={workspace}
              onApproveSignal={approveSourceSignal}
              onRejectSignal={rejectSourceSignal}
              onArchiveSignal={archiveSourceSignal}
              onCorrectSignal={correctSourceSignal}
              onCreateInsight={() => {
                const insightCard = createInsightCard(
                  workspace.sourceSignal,
                  workspace.editorialModel,
                  workspace.topics,
                  workspace.fabulas,
                  workspace.topicFabulaMatrix
                );
                patchWorkspace({ insightCard }, 'Карточка инсайта собрана');
              }}
              onPlan={() => {
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
              }}
            />
          )}
          {active === 'plan' && (
            <PlanView
              workspace={workspace}
              onGenerate={() => {
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
              }}
              onItemChange={(item) => {
                const updatedItems = updateContentPlanItem(workspace.contentPlanItems, item);
                const planWeightWarnings = detectBroadcastPlanConflicts(workspace, updatedItems);
                const contentPlanItems = applyPlanWarnings(updatedItems, planWeightWarnings);
                patchWorkspace({ contentPlanItems, planWeightWarnings });
              }}
              onApprove={(itemId) => {
                const approvedItems = approveContentPlanSlot(workspace.contentPlanItems, itemId);
                const planWeightWarnings = detectBroadcastPlanConflicts(workspace, approvedItems);
                const contentPlanItems = applyPlanWarnings(approvedItems, planWeightWarnings);
                const contentPlanItem = contentPlanItems.find((item) => item.id === itemId) ?? null;
                patchWorkspace(
                  { contentPlanItems, contentPlanItem, planWeightWarnings },
                  'Слот сетки утвержден'
                );
              }}
              onBrief={(item) => {
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
              }}
            />
          )}
          {active === 'brief' && (
            <BriefView
              workspace={workspace}
              onBriefChange={(postBrief) => patchWorkspace({ postBrief })}
              onBackToPlan={() => go('plan')}
              onApprove={() => {
                if (!workspace.postBrief) return;
                patchWorkspace({ postBrief: approvePostBrief(workspace.postBrief) }, 'Фабула утверждена');
              }}
            />
          )}
          {active === 'edit' && (
            <EditView
              workspace={workspace}
              onGoBrief={() => go('brief')}
              onCreateDraft={() => {
                if (!workspace.postBrief || workspace.postBrief.approvalStatus !== 'approved') return;
                const postDraft = createPostDraft(workspace.postBrief, workspace.editorialModel);
                const editorialChecks = runEditorialChecks(postDraft, workspace.postBrief, workspace.editorialModel);
                const editorNotes = createEditorNotes(editorialChecks);
                patchWorkspace(
                  { postDraft, editorialChecks, editorNotes, finalText: null },
                  'Драфт подготовлен для редакторских проверок'
                );
              }}
              onDraftChange={(body) => {
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
              }}
              onApproveFinal={() => {
                if (!workspace.postDraft) return;
                const finalText = approveFinalText(workspace.postDraft);
                patchWorkspace(
                  { finalText, releasePackage: null, editorialLearningNote: null },
                  'Финальный текст утвержден'
                );
              }}
            />
          )}
          {active === 'release' && (
            <ReleaseView
              workspace={workspace}
              onGoEdit={() => go('edit')}
              onCreatePackage={() => {
                if (!workspace.finalText || workspace.finalText.approvalStatus !== 'approved') return;
                const releasePackage = createReleasePackage(workspace.finalText, workspace.contentPlanItem);
                patchWorkspace(
                  { releasePackage, editorialLearningNote: null },
                  'Пакет ручного выпуска подготовлен'
                );
              }}
              onToggleChecklist={(itemId) => {
                if (!workspace.releasePackage) return;
                patchWorkspace({
                  releasePackage: toggleReleaseChecklistItem(workspace.releasePackage, itemId),
                  editorialLearningNote: null
                });
              }}
              onMarkReady={() => {
                if (!workspace.releasePackage) return;
                const releasePackage = markReleaseReady(workspace.releasePackage);
                patchWorkspace(
                  { releasePackage, editorialLearningNote: null },
                  releasePackage.status === 'ready' ? 'Выпуск готов' : 'Закройте чеклист выпуска'
                );
              }}
              onCopy={async () => {
                if (!workspace.releasePackage || !workspace.finalText) return;
                await copyToClipboard(workspace.finalText.body);
                patchWorkspace(
                  {
                    releasePackage: markReleaseExported(markManualExportDone(workspace.releasePackage)),
                    editorialLearningNote: null
                  },
                  'Текст скопирован для ручного выпуска'
                );
              }}
              onDownload={() => {
                if (!workspace.releasePackage) return;
                downloadMarkdown(workspace.releasePackage);
                patchWorkspace(
                  {
                    releasePackage: markReleaseExported(markManualExportDone(workspace.releasePackage)),
                    editorialLearningNote: null
                  },
                  'Markdown скачан для ручного выпуска'
                );
              }}
            />
          )}
          {active === 'analytics' && (
            <AnalyticsView
              workspace={workspace}
              onGoRelease={() => go('release')}
              onCreateNote={() => {
                if (!workspace.releasePackage || !workspace.finalText) return;
                const editorialLearningNote = createEditorialLearningNote(
                  workspace.releasePackage,
                  workspace.finalText,
                  workspace.contentPlanItem
                );
                patchWorkspace({ editorialLearningNote }, 'Аналитика подготовлена');
              }}
              onChangeNote={(editorialLearningNote) => patchWorkspace({ editorialLearningNote })}
              onCapture={() => {
                if (!workspace.editorialLearningNote) return;
                patchWorkspace(
                  { editorialLearningNote: markLearningNoteCaptured(workspace.editorialLearningNote) },
                  'Редакционные выводы зафиксированы'
                );
              }}
            />
          )}
        </div>
      </main>
      <ContextChatOverlay
        messages={contextChatMessages}
        open={contextChatOpen}
        scope={contextChatScope}
        activeTab={contextChatTab}
        suggestions={visibleContextChatSuggestions}
        onAcceptSuggestion={acceptContextChatSuggestion}
        onClose={() => setContextChatOpen(false)}
        onDismissSuggestion={dismissContextChatSuggestion}
        onSendMessage={sendContextChatMessage}
        onSwitchTab={setContextChatTab}
      />
      {toast ? (
        <div className="toast" role="status">
          <Icon name="check" size={17} />
          {toast}
        </div>
      ) : null}
    </div>
  );
}

function Sidebar({
  active,
  onNav,
  workspace
}: {
  active: WorkspaceSection;
  onNav: (section: WorkspaceSection) => void;
  workspace: WorkspaceState;
}) {
  return (
    <aside className="side">
      <div className="brand">
        <span className="brand-mark">Г</span>
        <span className="wm">Главред</span>
      </div>
      <div className="nav-label">Редакция</div>
      {NAV.map((item) => (
        <button
          key={item.id}
          className={`nav-item${active === item.id ? ' active' : ''}${item.disabled ? ' muted' : ''}`}
          onClick={() => onNav(item.id)}
          type="button"
        >
          <Icon name={item.icon} />
          <span>{item.label}</span>
          {item.id === 'memory' ? <span className="count">{workspace.authorNotes.length}</span> : null}
          {item.id === 'signals' ? <span className="count">{workspace.sourceSignals.length}</span> : null}
          {item.id === 'plan' ? <span className="count">{workspace.contentPlanItems.length}</span> : null}
          {item.id !== 'memory' && item.id !== 'signals' && item.id !== 'plan' && item.count ? <span className="count">{item.count}</span> : null}
        </button>
      ))}
      <div className="side-foot">
        <div className="author">
          <div className="ava">АК</div>
          <div>
            <b>{workspace.editorialModel.author.split(' — ')[0]}</b>
            <span>Главный редактор</span>
          </div>
        </div>
      </div>
    </aside>
  );
}

function Topbar({
  active,
  chatOpen,
  suggestionCount,
  onOpenChat,
  onReset
}: {
  active: WorkspaceSection;
  chatOpen: boolean;
  suggestionCount: number;
  onOpenChat: () => void;
  onReset: () => void;
}) {
  const [title, subtitle] = TITLES[active];

  return (
    <header className="topbar">
      <div className="crumb">
        {title}
        <small>{subtitle}</small>
      </div>
      <div className="spacer" />
      <div className="search">
        <Icon name="search" size={16} />
        <input aria-label="Поиск" placeholder="Поиск по темам, фабулам..." />
      </div>
      <button className="icon-btn" type="button" aria-label="Уведомления">
        <Icon name="bell" />
        <span className="dot" />
      </button>
      <button
        className={`btn btn-sec btn-sm assistant-topbar-btn${chatOpen ? ' active' : ''}`}
        data-testid="context-chat-topbar-trigger"
        type="button"
        aria-expanded={chatOpen}
        onClick={onOpenChat}
      >
        <Icon name="spark" size={14} />
        Помощник
        {suggestionCount > 0 ? <span className="assistant-count">{suggestionCount}</span> : null}
      </button>
      <button className="icon-btn" type="button" aria-label="Сбросить демо" onClick={onReset} title="Сбросить демо">
        <Icon name="reset" size={14} />
      </button>
    </header>
  );
}

function ContextChatOverlay({
  activeTab,
  messages,
  open,
  scope,
  suggestions,
  onAcceptSuggestion,
  onClose,
  onDismissSuggestion,
  onSendMessage,
  onSwitchTab
}: {
  activeTab: ContextChatTab;
  messages: ContextChatMessage[];
  open: boolean;
  scope: ContextChatScope;
  suggestions: ContextChatSuggestion[];
  onAcceptSuggestion: (suggestion: ContextChatSuggestion) => void;
  onClose: () => void;
  onDismissSuggestion: (suggestionId: string) => void;
  onSendMessage: (message: string) => void;
  onSwitchTab: (tab: ContextChatTab) => void;
}) {
  const [draft, setDraft] = useState('');

  if (!open) return null;

  function submitMessage(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const text = draft.trim();
    if (!text) return;
    onSendMessage(text);
    setDraft('');
  }

  return (
    <aside
      className={`context-chat-drawer scope-${scope}`}
      data-testid="context-chat-drawer"
      aria-label="Контекстный помощник"
    >
      <div className="context-chat-head">
        <div>
          <span className="mono-label">Context chat</span>
          <h3>Помощник раздела</h3>
          <p>{contextChatScopeLabel(scope)}</p>
        </div>
        <div className="context-chat-head-actions">
          <button className="icon-btn" type="button" aria-label="Закрыть помощника" onClick={onClose}>
            <Icon name="close" size={16} />
          </button>
        </div>
      </div>
      <div className="context-chat-tabs tabs" role="tablist" aria-label="Режим помощника">
        <button
          className={`tab${activeTab === 'chat' ? ' active' : ''}`}
          role="tab"
          type="button"
          aria-selected={activeTab === 'chat'}
          onClick={() => onSwitchTab('chat')}
        >
          Чат
        </button>
        <button
          className={`tab${activeTab === 'suggestions' ? ' active' : ''}`}
          role="tab"
          type="button"
          aria-selected={activeTab === 'suggestions'}
          onClick={() => onSwitchTab('suggestions')}
        >
          Подсказки
          <span className="assistant-count">{suggestions.length}</span>
        </button>
      </div>
      {activeTab === 'chat' ? (
        <div className="context-chat-mode">
          <div className="context-chat-thread">
            {messages.map((message) => (
              <article className={`context-message ${message.role}`} key={message.id}>
                <span>{contextChatRoleLabel(message.role)}</span>
                <p>{message.text}</p>
                {message.suggestion && message.suggestion.actionType !== 'readOnly' ? (
                  <button
                    className="btn btn-pri btn-sm"
                    type="button"
                    onClick={() => onAcceptSuggestion(message.suggestion as ContextChatSuggestion)}
                  >
                    {contextChatActionLabel(message.suggestion.actionType)}
                  </button>
                ) : null}
              </article>
            ))}
          </div>
          <form className="context-chat-input" onSubmit={submitMessage}>
            <textarea
              aria-label="Сообщение помощнику"
              value={draft}
              onChange={(event) => setDraft(event.target.value)}
              placeholder="Спросите по текущему разделу или попросите сгенерировать тему..."
              rows={3}
            />
            <button className="btn btn-pri btn-sm" type="submit" disabled={!draft.trim()}>
              Отправить
            </button>
          </form>
        </div>
      ) : (
        <div className="context-chat-suggestions">
          {suggestions.length === 0 ? (
            <p className="context-empty">Новых подсказок нет. Можно вернуться в чат и задать вопрос по разделу.</p>
          ) : null}
          {suggestions.map((suggestion) => (
            <article className="context-suggestion" key={suggestion.id}>
              <button
                className="context-suggestion-dismiss"
                type="button"
                aria-label={`Скрыть подсказку: ${suggestion.title}`}
                onClick={() => onDismissSuggestion(suggestion.id)}
              >
                <Icon name="close" size={14} />
              </button>
              <div>
                <h4>{suggestion.title}</h4>
                <p>{suggestion.body}</p>
              </div>
              {suggestion.actionType !== 'readOnly' ? (
                <button className="btn btn-pri btn-sm" type="button" onClick={() => onAcceptSuggestion(suggestion)}>
                  {contextChatActionLabel(suggestion.actionType)}
                </button>
              ) : null}
            </article>
          ))}
        </div>
      )}
    </aside>
  );
}

function getContextChatScope(
  active: WorkspaceSection,
  memoryTab: MemoryInternalTab,
  editorialTab: EditorialModelTab
): ContextChatScope {
  if (active === 'memory') {
    if (memoryTab === 'sources') return 'sources';
    if (memoryTab === 'queue') return 'importQueue';
    if (memoryTab === 'archive') return 'archive';
    return 'memory';
  }

  if (active === 'editorialModel') {
    if (editorialTab === 'topics') return 'topics';
    if (editorialTab === 'fabulas') return 'fabulas';
    if (editorialTab === 'matrix') return 'matrix';
    return 'editorialPublisher';
  }

  return mapWorkspaceSectionToProductionScope(active);
}

function contextChatScopeLabel(scope: ContextChatScope): string {
  const labels: Record<ContextChatScope, string> = {
    memory: 'Память автора · мысли и корректировки',
    sources: 'Память автора · источники',
    importQueue: 'Память автора · очередь разбора',
    archive: 'Память автора · архив',
    editorialPublisher: 'Редакционная модель · издательство',
    topics: 'Редакционная модель · темы',
    fabulas: 'Редакционная модель · фабулы',
    matrix: 'Редакционная модель · матрица',
    production: 'Производство поста · HITL flow',
    release: 'Выпуск · manual export',
    analytics: 'Аналитика · learning note'
  };
  return labels[scope];
}

function contextChatRoleLabel(role: ContextChatMessage['role']): string {
  if (role === 'author') return 'Вы';
  if (role === 'system') return 'Система';
  return 'Помощник';
}

function contextChatActionLabel(actionType: ContextChatActionType): string {
  const labels: Record<ContextChatActionType, string> = {
    addEditorialRule: 'Добавить правило',
    addTopic: 'Создать черновик темы',
    addFabula: 'Создать черновик фабулы',
    runValidation: 'Проверить',
    readOnly: 'Принять к сведению'
  };
  return labels[actionType];
}

type MemoryTypeFilter = AuthorNoteType | 'all';
type CorrectionTarget = {
  type: 'assertion' | 'evidence';
  id: string;
  title: string;
};
type PendingCorrectionConflict = {
  noteId: string;
  targetTitle: string;
};
type MemoryInternalTab = 'feed' | 'sources' | 'queue' | 'archive';
type ImportViewMode = 'list' | 'groups';
type PendingBulkAction = {
  action: 'archive' | 'reject';
  candidateIds: string[];
  destination: string;
};
type LinkPreview = {
  isValid: boolean;
  domain: string;
  normalizedUrl: string;
  title: string;
};
type SpeechRecognitionEventLike = {
  results: {
    [index: number]: {
      [index: number]: {
        transcript: string;
      };
    };
  };
};
type SpeechRecognitionLike = {
  lang: string;
  interimResults: boolean;
  onresult: ((event: SpeechRecognitionEventLike) => void) | null;
  start: () => void;
};
type SpeechRecognitionWindow = Window &
  typeof globalThis & {
    SpeechRecognition?: new () => SpeechRecognitionLike;
    webkitSpeechRecognition?: new () => SpeechRecognitionLike;
  };
const MAX_AUTHOR_ATTACHMENT_BYTES = 1024 * 1024;

function AuthorMemoryView({
  activeTab,
  workspace,
  onChangeTab,
  onPatchWorkspace,
  onChangeNotes
}: {
  activeTab: MemoryInternalTab;
  workspace: WorkspaceState;
  onChangeTab: (tab: MemoryInternalTab) => void;
  onPatchWorkspace: (patch: Partial<WorkspaceState>, message?: string) => void;
  onChangeNotes: (notes: AuthorNote[], message?: string) => void;
}) {
  const notes = workspace.authorNotes;
  const assertions = workspace.authorPositionAssertions;
  const externalSources = workspace.externalSources;
  const importCandidates = workspace.importCandidates;
  const archiveRecords = workspace.archiveRecords;
  const bulkImportActions = workspace.bulkImportActions;
  const tab = activeTab;
  const setTab = onChangeTab;
  const [type, setType] = useState<AuthorNoteType>('thought');
  const [showTitle, setShowTitle] = useState(false);
  const [showFile, setShowFile] = useState(false);
  const [title, setTitle] = useState('');
  const [body, setBody] = useState('');
  const [sourceUrl, setSourceUrl] = useState('');
  const [tags, setTags] = useState('');
  const [attachments, setAttachments] = useState<AuthorAttachment[]>([]);
  const [attachmentError, setAttachmentError] = useState('');
  const [correctionTarget, setCorrectionTarget] = useState<CorrectionTarget | null>(null);
  const [query, setQuery] = useState('');
  const [filter, setFilter] = useState<MemoryTypeFilter>('all');
  const [visibleCount, setVisibleCount] = useState(5);
  const [expandedNoteIds, setExpandedNoteIds] = useState<string[]>([]);
  const [editingId, setEditingId] = useState<string | null>(null);
  const [editTitle, setEditTitle] = useState('');
  const [editBody, setEditBody] = useState('');
  const [editSourceUrl, setEditSourceUrl] = useState('');
  const [editTags, setEditTags] = useState('');
  const [editAttachments, setEditAttachments] = useState<AuthorAttachment[]>([]);
  const [editAttachmentError, setEditAttachmentError] = useState('');
  const [pendingDeleteNote, setPendingDeleteNote] = useState<AuthorNote | null>(null);
  const [pendingConflict, setPendingConflict] = useState<PendingCorrectionConflict | null>(null);
  const [candidateFilters, setCandidateFilters] = useState<ImportCandidateFilters>({
    reviewStatus: 'new',
    sourceId: 'all',
    evidencePolicy: 'all',
    duplicateRisk: 'all',
    query: ''
  });
  const [importViewMode, setImportViewMode] = useState<ImportViewMode>('list');
  const [groupMode, setGroupMode] = useState<ImportCandidateGroupType>('source');
  const [selectedCandidateIds, setSelectedCandidateIds] = useState<string[]>([]);
  const [pendingBulkAction, setPendingBulkAction] = useState<PendingBulkAction | null>(null);
  const correctionTargets = useMemo(() => buildCorrectionTargets(assertions), [assertions]);
  const summary = useMemo(() => getMemorySummary(notes), [notes]);
  const filteredNotes = useMemo(() => filterAuthorNotes(notes, query, filter), [filter, notes, query]);
  const visibleNotes = filteredNotes.slice(0, visibleCount);
  const filteredCandidates = useMemo(
    () => filterImportCandidates(importCandidates, candidateFilters),
    [candidateFilters, importCandidates]
  );
  const importGroups = useMemo(
    () => groupImportCandidates(filteredCandidates, groupMode),
    [filteredCandidates, groupMode]
  );
  const importSummary = useMemo(
    () => getImportSummary(externalSources, importCandidates, archiveRecords, bulkImportActions),
    [archiveRecords, bulkImportActions, externalSources, importCandidates]
  );
  const linkPreview = buildLinkPreview(sourceUrl);
  const isManualCorrection = type === 'manualCorrection';
  const voiceRecognition = getSpeechRecognitionConstructor();
  const canUseVoice = Boolean(voiceRecognition);

  function submitNote() {
    const trimmedBody = body.trim();
    const selectedTarget = isManualCorrection ? correctionTarget : null;

    if (!trimmedBody) return;
    if (type === 'linkReaction' && !linkPreview.isValid) return;
    if (isManualCorrection && !selectedTarget) return;

    const note: AuthorNote = {
      id: `note-${Date.now()}`,
      type,
      title: showTitle ? title.trim() : '',
      body: trimmedBody,
      sourceUrl: type === 'linkReaction' ? linkPreview.normalizedUrl : '',
      tags: isManualCorrection ? ['manual-correction'] : splitTags(tags),
      attachments: isManualCorrection ? [] : attachments,
      capturedAt: new Date().toISOString(),
      targetType: selectedTarget?.type,
      targetId: selectedTarget?.id,
      targetTitle: selectedTarget?.title
    };

    onChangeNotes([note, ...notes], 'Память автора обновлена');

    if (isManualCorrection && selectedTarget && hasCorrectionConflict(trimmedBody)) {
      setPendingConflict({ noteId: note.id, targetTitle: selectedTarget.title });
    }

    resetComposer();
  }

  function changeNoteType(nextType: AuthorNoteType) {
    setType(nextType);
    if (nextType === 'manualCorrection') {
      setShowFile(false);
      setAttachments([]);
      setAttachmentError('');
      setSourceUrl('');
      setTags('');
    }
  }

  function resetComposer() {
    setShowTitle(false);
    setShowFile(false);
    setTitle('');
    setBody('');
    setSourceUrl('');
    setTags('');
    setAttachments([]);
    setAttachmentError('');
    setCorrectionTarget(null);
    setType('thought');
  }

  function beginCorrection(target: CorrectionTarget) {
    setType('manualCorrection');
    setCorrectionTarget(target);
    setShowTitle(false);
    setShowFile(false);
    setTitle('');
    setSourceUrl('');
    setTags('');
    setAttachments([]);
    setAttachmentError('');
    setBody('');
  }

  function beginEdit(note: AuthorNote) {
    setEditingId(note.id);
    setEditTitle(note.title);
    setEditBody(note.body);
    setEditSourceUrl(note.sourceUrl);
    setEditTags(note.tags.join(', '));
    setEditAttachments(note.attachments ?? []);
    setEditAttachmentError('');
  }

  function saveEdit(note: AuthorNote) {
    if (!editBody.trim()) return;

    onChangeNotes(
      notes.map((item) =>
        item.id === note.id
          ? {
              ...item,
              title: editTitle.trim(),
              body: editBody.trim(),
              sourceUrl: item.type === 'linkReaction' ? buildLinkPreview(editSourceUrl).normalizedUrl : '',
              tags: splitTags(editTags),
              attachments: item.type === 'manualCorrection' ? [] : editAttachments
            }
          : item
      ),
      'Заметка обновлена'
    );
    setEditingId(null);
  }

  function requestDelete(note: AuthorNote) {
    if (isEvidenceNote(note.id, assertions)) {
      setPendingDeleteNote(note);
      return;
    }

    deleteNote(note.id);
  }

  function deleteNote(noteId: string) {
    onChangeNotes(
      notes.filter((note) => note.id !== noteId),
      'Заметка удалена'
    );
    setPendingDeleteNote(null);
  }

  function resolveCorrectionConflict(mode: 'merge' | 'replace' | 'rollback') {
    if (!pendingConflict) return;

    if (mode === 'rollback') {
      onChangeNotes(
        notes.filter((note) => note.id !== pendingConflict.noteId),
        'Корректировка отменена'
      );
    }

    if (mode === 'replace') {
      onChangeNotes(
        notes.map((note) =>
          note.id === pendingConflict.noteId
            ? { ...note, tags: Array.from(new Set([...note.tags, 'replace-inference'])) }
            : note
        ),
        'Корректировка помечена как замена вывода'
      );
    }

    setPendingConflict(null);
  }

  function toggleExpanded(noteId: string) {
    setExpandedNoteIds((current) =>
      current.includes(noteId) ? current.filter((id) => id !== noteId) : [...current, noteId]
    );
  }

  function startVoiceInput() {
    if (!voiceRecognition) return;

    const recognition = new voiceRecognition();
    recognition.lang = 'ru-RU';
    recognition.interimResults = false;
    recognition.onresult = (event) => {
      const transcript = event.results[0]?.[0]?.transcript?.trim();
      if (!transcript) return;
      setBody((current) => `${current}${current ? '\n' : ''}${transcript}`);
    };
    recognition.start();
  }

  async function attachComposerFile(file: File | undefined) {
    const result = await createAuthorAttachment(file);
    if ('error' in result) {
      setAttachmentError(result.error);
      return;
    }

    setAttachments([result.attachment]);
    setAttachmentError('');
  }

  async function attachEditFile(file: File | undefined) {
    const result = await createAuthorAttachment(file);
    if ('error' in result) {
      setEditAttachmentError(result.error);
      return;
    }

    setEditAttachments([result.attachment]);
    setEditAttachmentError('');
  }

  function patchImportState(
    patch: Pick<Partial<WorkspaceState>, 'importCandidates' | 'archiveRecords' | 'bulkImportActions' | 'authorNotes' | 'authorMemoryEvents' | 'authorPositionAssertions'>,
    message: string
  ) {
    onPatchWorkspace(patch, message);
  }

  function replaceImportCandidate(candidate: ImportedMemoryCandidate, message: string) {
    patchImportState(
      {
        importCandidates: importCandidates.map((item) => (item.id === candidate.id ? candidate : item))
      },
      message
    );
  }

  function addArchiveRecord(
    candidate: ImportedMemoryCandidate,
    record: ArchiveRecord,
    message: string
  ) {
    patchImportState(
      {
        importCandidates: importCandidates.map((item) =>
          item.id === candidate.id ? markCandidateAcceptedToArchive(item) : item
        ),
        archiveRecords: [record, ...archiveRecords.filter((item) => item.id !== record.id)]
      },
      message
    );
  }

  function findSource(candidate: ImportedMemoryCandidate): AuthorExternalSource {
    return externalSources.find((source) => source.id === candidate.sourceId) ?? externalSources[0];
  }

  function acceptToMemory(candidate: ImportedMemoryCandidate) {
    const note = acceptCandidateToMemory(candidate, findSource(candidate));
    const authorNotes = [note, ...notes];
    const authorMemoryEvents = authorNotes.map(createAuthorMemoryEvent);
    const authorPositionAssertions = inferAuthorPositionAssertions(authorNotes, authorMemoryEvents);

    patchImportState(
      {
        authorNotes,
        authorMemoryEvents,
        authorPositionAssertions,
        importCandidates: importCandidates.map((item) =>
          item.id === candidate.id ? markCandidateAcceptedToMemory(item) : item
        )
      },
      'Кандидат добавлен в память автора'
    );
    setTab('feed');
  }

  function acceptToArchive(candidate: ImportedMemoryCandidate) {
    addArchiveRecord(
      candidate,
      acceptCandidateToArchive(candidate, findSource(candidate)),
      'Кандидат принят в архив'
    );
  }

  function performBulkAction(action: PendingBulkAction) {
    const selected = importCandidates.filter((candidate) => action.candidateIds.includes(candidate.id));
    if (selected.length === 0) return;

    if (action.action === 'archive') {
      const result = bulkAcceptCandidatesToArchive(selected, externalSources);
      const changedById = new Map(result.candidates.map((candidate) => [candidate.id, candidate]));
      const recordById = new Map(result.archiveRecords.map((record) => [record.id, record]));

      patchImportState(
        {
          importCandidates: importCandidates.map((candidate) => changedById.get(candidate.id) ?? candidate),
          archiveRecords: [
            ...result.archiveRecords,
            ...archiveRecords.filter((record) => !recordById.has(record.id))
          ],
          bulkImportActions: [...bulkImportActions, result.action]
        },
        'Кандидаты приняты в архив'
      );
    } else {
      const result = bulkRejectCandidates(selected);
      const changedById = new Map(result.candidates.map((candidate) => [candidate.id, candidate]));

      patchImportState(
        {
          importCandidates: importCandidates.map((candidate) => changedById.get(candidate.id) ?? candidate),
          bulkImportActions: [...bulkImportActions, result.action]
        },
        'Кандидаты отклонены'
      );
    }

    setSelectedCandidateIds([]);
    setPendingBulkAction(null);
  }

  function undoLatestBulkAction() {
    const restored = undoLastBulkImportAction(workspace);
    patchImportState(
      {
        importCandidates: restored.importCandidates,
        archiveRecords: restored.archiveRecords,
        bulkImportActions: restored.bulkImportActions
      },
      'Последнее групповое действие отменено'
    );
  }

  function toggleCandidateSelection(candidateId: string) {
    setSelectedCandidateIds((current) =>
      current.includes(candidateId) ? current.filter((id) => id !== candidateId) : [...current, candidateId]
    );
  }

  function selectCandidates(candidateIds: string[]) {
    setSelectedCandidateIds(Array.from(new Set(candidateIds)));
  }

  function unselectCandidates(candidateIds: string[]) {
    const idsToRemove = new Set(candidateIds);
    setSelectedCandidateIds((current) => current.filter((candidateId) => !idsToRemove.has(candidateId)));
  }

  function clearCandidateSelection() {
    setSelectedCandidateIds([]);
  }

  function openQueueForSource(sourceId?: string) {
    setCandidateFilters((current) => ({ ...current, sourceId: sourceId ?? 'all', reviewStatus: 'new' }));
    setSelectedCandidateIds([]);
    setTab('queue');
  }

  function acceptArchiveRecordToMemory(record: ArchiveRecord) {
    const source = externalSources.find((item) => item.id === record.sourceId) ?? externalSources[0];
    const note: AuthorNote = {
      id: `note-archive-${record.id}-${Date.now()}`,
      type: 'linkReaction',
      title: record.title,
      body: record.bodyExcerpt,
      sourceUrl: record.originalUrl || source.url,
      tags: ['archive', 'imported'],
      attachments: [],
      capturedAt: new Date().toISOString()
    };
    const authorNotes = [note, ...notes];
    const authorMemoryEvents = authorNotes.map(createAuthorMemoryEvent);
    const authorPositionAssertions = inferAuthorPositionAssertions(authorNotes, authorMemoryEvents);

    patchImportState(
      {
        authorNotes,
        authorMemoryEvents,
        authorPositionAssertions
      },
      'Архивная запись добавлена в память автора'
    );
  }

  function restoreArchiveRecordToQueue(record: ArchiveRecord) {
    const source = externalSources.find((item) => item.id === record.sourceId) ?? externalSources[0];
    const existingCandidateId = record.id.replace(/^archive-/, '');
    const existingCandidate = importCandidates.find((candidate) => candidate.id === existingCandidateId);
    const restoredCandidate: ImportedMemoryCandidate = existingCandidate
      ? {
          ...existingCandidate,
          reviewStatus: 'new',
          evidencePolicy: record.evidencePolicy === 'ignored' ? 'ignored' : 'archiveOnly'
        }
      : {
          id: `restored-${record.id}`,
          sourceId: record.sourceId,
          title: record.title,
          excerpt: record.bodyExcerpt,
          originalUrl: record.originalUrl,
          capturedAt: record.publishedAt,
          detectedTags: ['archive'],
          duplicateRisk: 'medium',
          suggestedTarget: `Возвращено из архива ${source.title} для ручного review`,
          reviewStatus: 'new',
          evidencePolicy: record.evidencePolicy === 'ignored' ? 'ignored' : 'archiveOnly'
        };

    patchImportState(
      {
        archiveRecords: archiveRecords.filter((item) => item.id !== record.id),
        importCandidates: existingCandidate
          ? importCandidates.map((candidate) => (candidate.id === existingCandidateId ? restoredCandidate : candidate))
          : [restoredCandidate, ...importCandidates]
      },
      'Архивная запись возвращена в очередь разбора'
    );
    setCandidateFilters((current) => ({ ...current, reviewStatus: 'new', sourceId: record.sourceId }));
    setTab('queue');
  }

  function ignoreArchiveRecord(record: ArchiveRecord) {
    patchImportState(
      {
        archiveRecords: archiveRecords.map((item) =>
          item.id === record.id ? { ...item, evidencePolicy: 'ignored' } : item
        )
      },
      'Архивная запись помечена как не evidence'
    );
  }

  function deleteArchiveRecord(recordId: string) {
    patchImportState(
      {
        archiveRecords: archiveRecords.filter((record) => record.id !== recordId)
      },
      'Архивная запись удалена'
    );
  }

  return (
    <div className="page wide fade-up">
      <div className="sec-head">
        <div>
          <h2>Авторская память</h2>
          <p className="section-help">
            Фиксируйте мысли, реакции на ссылки и ручные правки без обязательной структуры. Система связывает
            записи с выводами о вашей позиции, а вы можете уточнять эти выводы прямо из evidence.
          </p>
        </div>
      </div>
      <MemoryTabNav active={tab} onChange={setTab} />
      <div className="memory-grid">
        <section className="memory-main">
          {tab === 'feed' ? (
            <>
          <div className="card memory-composer">
            <div className="form-row">
              <label>
                Тип записи
                <select value={type} onChange={(event) => changeNoteType(event.target.value as AuthorNoteType)}>
                  <option value="thought">Мысль</option>
                  <option value="linkReaction">Реакция на ссылку</option>
                  <option value="manualCorrection">Ручная корректировка</option>
                </select>
              </label>
              {isManualCorrection ? (
                <label>
                  Что корректируем
                  <select
                    value={correctionTarget ? correctionTargetKey(correctionTarget) : ''}
                    onChange={(event) =>
                      setCorrectionTarget(
                        correctionTargets.find((target) => correctionTargetKey(target) === event.target.value) ?? null
                      )
                    }
                  >
                    <option value="">Выберите вывод или evidence</option>
                    {correctionTargets.map((target) => (
                      <option key={correctionTargetKey(target)} value={correctionTargetKey(target)}>
                        {target.type === 'assertion' ? 'Вывод' : 'Evidence'} · {target.title}
                      </option>
                    ))}
                  </select>
                </label>
              ) : null}
              {type === 'linkReaction' ? (
                <label>
                  Ссылка
                  <input
                    value={sourceUrl}
                    onChange={(event) => setSourceUrl(event.target.value)}
                    placeholder="https://..."
                  />
                </label>
              ) : null}
            </div>
            {!isManualCorrection && (
              <div className="optional-tools">
                <button
                  className="btn btn-sec btn-sm"
                  type="button"
                  onClick={() => {
                    setShowTitle((current) => !current);
                    if (showTitle) setTitle('');
                  }}
                >
                  <Icon name={showTitle ? 'minus' : 'plus'} size={14} />
                  Заголовок
                </button>
                <button
                  className="btn btn-sec btn-sm"
                  type="button"
                  onClick={() => {
                    setShowFile((current) => !current);
                    if (showFile) {
                      setAttachments([]);
                      setAttachmentError('');
                    }
                  }}
                >
                  <Icon name={showFile ? 'minus' : 'plus'} size={14} />
                  Файл
                </button>
              </div>
            )}
            {!isManualCorrection && showTitle ? (
              <label>
                Заголовок
                <input value={title} onChange={(event) => setTitle(event.target.value)} />
              </label>
            ) : null}
            {!isManualCorrection && showFile ? (
              <FileAttachmentPicker
                attachments={attachments}
                error={attachmentError}
                inputLabel="Файл"
                onAttach={attachComposerFile}
                onRemove={() => {
                  setAttachments([]);
                  setAttachmentError('');
                }}
              />
            ) : null}
            {type === 'linkReaction' && linkPreview.isValid ? <LinkPreviewCard preview={linkPreview} /> : null}
            <label>
              {isManualCorrection ? 'Корректировка' : 'Заметка автора'}
              <textarea value={body} onChange={(event) => setBody(event.target.value)} />
            </label>
            {!isManualCorrection ? (
              <label>
                Теги
                <input
                  value={tags}
                  onChange={(event) => setTags(event.target.value)}
                  placeholder="workflow, evals, adoption"
                />
              </label>
            ) : null}
            <div className="composer-actions">
              <button
                className="btn btn-sec"
                type="button"
                onClick={startVoiceInput}
                disabled={!canUseVoice}
                title={canUseVoice ? 'Добавить голосом' : 'Голосовой ввод недоступен в этом браузере'}
              >
                <Icon name="mic" size={16} />
                Голосом
              </button>
              <button
                className="btn btn-pri"
                type="button"
                onClick={submitNote}
                disabled={
                  !body.trim() ||
                  (type === 'linkReaction' && !linkPreview.isValid) ||
                  (isManualCorrection && !correctionTarget)
                }
              >
                <Icon name="plus" size={16} />
                Добавить в память
              </button>
            </div>
            {pendingConflict ? (
              <div className="conflict-box" role="status">
                <b>Корректировка спорит с текущим evidence</b>
                <p>
                  Вы уточняете: {pendingConflict.targetTitle}. Выберите, как зафиксировать позицию в памяти.
                </p>
                <div className="inline-actions">
                  <button className="btn btn-sec btn-sm" type="button" onClick={() => resolveCorrectionConflict('merge')}>
                    Смержить
                  </button>
                  <button className="btn btn-sec btn-sm" type="button" onClick={() => resolveCorrectionConflict('replace')}>
                    Заменить вывод
                  </button>
                  <button className="btn btn-sec btn-sm" type="button" onClick={() => resolveCorrectionConflict('rollback')}>
                    Откатить корректировку
                  </button>
                </div>
              </div>
            ) : null}
          </div>

          <div className="card memory-toolbar">
            <div className="memory-search">
              <Icon name="search" size={16} />
              <input
                aria-label="Поиск по памяти"
                value={query}
                onChange={(event) => {
                  setQuery(event.target.value);
                  setVisibleCount(5);
                }}
                placeholder="Искать по заметкам, тегам, ссылкам..."
              />
            </div>
            <select
              aria-label="Фильтр типа заметки"
              value={filter}
              onChange={(event) => {
                setFilter(event.target.value as MemoryTypeFilter);
                setVisibleCount(5);
              }}
            >
              <option value="all">Все</option>
              <option value="thought">Мысли</option>
              <option value="linkReaction">Ссылки</option>
              <option value="manualCorrection">Правки</option>
            </select>
          </div>

          <div className="memory-feed">
            {visibleNotes.map((note) => (
              <AuthorNoteCard
                assertions={assertions}
                editingId={editingId}
                editBody={editBody}
                editAttachmentError={editAttachmentError}
                editAttachments={editAttachments}
                editSourceUrl={editSourceUrl}
                editTags={editTags}
                editTitle={editTitle}
                expanded={expandedNoteIds.includes(note.id)}
                key={note.id}
                note={note}
                onBeginEdit={beginEdit}
                onCancelEdit={() => setEditingId(null)}
                onChangeEditBody={setEditBody}
                onChangeEditSourceUrl={setEditSourceUrl}
                onChangeEditTags={setEditTags}
                onChangeEditTitle={setEditTitle}
                onDelete={requestDelete}
                onEditAttach={attachEditFile}
                onEditRemoveAttachment={() => {
                  setEditAttachments([]);
                  setEditAttachmentError('');
                }}
                onSaveEdit={saveEdit}
                onToggleExpanded={() => toggleExpanded(note.id)}
              />
            ))}
            {filteredNotes.length === 0 ? <EmptyState text="По этому запросу в памяти ничего не найдено." /> : null}
            {visibleCount < filteredNotes.length ? (
              <button className="btn btn-sec load-more" type="button" onClick={() => setVisibleCount((count) => count + 5)}>
                Показать еще
              </button>
            ) : null}
          </div>
            </>
          ) : null}
          {tab === 'sources' ? (
            <ExternalSourcesView
              candidates={importCandidates}
              sources={externalSources}
              onOpenQueue={openQueueForSource}
              onPatchSource={(source) =>
                onPatchWorkspace(
                  {
                    externalSources: externalSources.map((item) => (item.id === source.id ? source : item))
                  },
                  'Статус демо-источника обновлен'
                )
              }
            />
          ) : null}
          {tab === 'queue' ? (
            <ImportQueueView
              candidates={importCandidates}
              filteredCandidates={filteredCandidates}
              filters={candidateFilters}
              groups={importGroups}
              groupMode={groupMode}
              selectedCandidateIds={selectedCandidateIds}
              sources={externalSources}
              viewMode={importViewMode}
              onAcceptToArchive={acceptToArchive}
              onAcceptToMemory={acceptToMemory}
              onChangeFilters={(nextFilters) => {
                setCandidateFilters(nextFilters);
                setSelectedCandidateIds([]);
              }}
              onChangeGroupMode={setGroupMode}
              onChangeViewMode={setImportViewMode}
              onIgnoreEvidence={(candidate) =>
                replaceImportCandidate(ignoreCandidateForEvidence(candidate), 'Кандидат помечен как не evidence')
              }
              onOpenBulk={(action) => setPendingBulkAction(action)}
              onReject={(candidate) => replaceImportCandidate(rejectCandidate(candidate), 'Кандидат отклонен')}
              onClearSelection={clearCandidateSelection}
              onSelect={toggleCandidateSelection}
              onSelectAllFiltered={() => selectCandidates(filteredCandidates.map((candidate) => candidate.id))}
              onSelectPage={() => selectCandidates(filteredCandidates.slice(0, 10).map((candidate) => candidate.id))}
              onUnselectAllFiltered={() => unselectCandidates(filteredCandidates.map((candidate) => candidate.id))}
              onUnselectPage={() => unselectCandidates(filteredCandidates.slice(0, 10).map((candidate) => candidate.id))}
            />
          ) : null}
          {tab === 'archive' ? (
            <ArchiveView
              records={archiveRecords}
              sources={externalSources}
              onAcceptToMemory={acceptArchiveRecordToMemory}
              onDelete={deleteArchiveRecord}
              onIgnoreEvidence={ignoreArchiveRecord}
              onRestoreToQueue={restoreArchiveRecordToQueue}
            />
          ) : null}
        </section>

        <aside className="memory-side">
          <section className="panel import-summary">
            <h4>Импорт и архив</h4>
            <div className="summary-grid">
              <SummaryItem label="Источники" value={importSummary.sources} />
              <SummaryItem label="Кандидаты" value={importSummary.candidates} />
              <SummaryItem label="Review" value={importSummary.needsReview} />
              <SummaryItem label="Архив" value={importSummary.archived} />
              <SummaryItem label="Bulk" value={importSummary.bulkAccepted} />
              <SummaryItem label="Undo" value={importSummary.undoAvailable} />
            </div>
            <p className="panel-note">Архивные и неразобранные материалы не меняют выводы о позиции автора.</p>
            {bulkImportActions.some((action) => action.canUndo) ? (
              <button className="btn btn-sec btn-sm" type="button" onClick={undoLatestBulkAction}>
                Отменить последнее групповое действие
              </button>
            ) : null}
          </section>
          <section className="panel memory-summary">
            <h4>Сводка памяти</h4>
            <div className="summary-grid">
              <SummaryItem label="Всего" value={summary.total} />
              <SummaryItem label="Мысли" value={summary.thoughts} />
              <SummaryItem label="Ссылки" value={summary.links} />
              <SummaryItem label="Правки" value={summary.corrections} />
              <SummaryItem label="Месяц" value={summary.thisMonth} />
              <SummaryItem label="Год" value={summary.thisYear} />
            </div>
          </section>
          <section className="panel">
            <h4>Как система поняла автора</h4>
            <div className="assertions">
              {assertions.map((assertion) => (
                <AssertionCard assertion={assertion} key={assertion.id} onCorrect={beginCorrection} />
              ))}
            </div>
          </section>
        </aside>
      </div>
      {pendingBulkAction ? (
        <BulkActionDialog
          action={pendingBulkAction}
          candidates={importCandidates.filter((candidate) => pendingBulkAction.candidateIds.includes(candidate.id))}
          filters={candidateFilters}
          onCancel={() => setPendingBulkAction(null)}
          onConfirm={() => performBulkAction(pendingBulkAction)}
        />
      ) : null}
      {pendingDeleteNote ? (
        <div className="confirm-popover" role="dialog" aria-label="Подтверждение удаления">
          <div className="card">
            <h3>Удалить заметку из evidence?</h3>
            <p>
              Заметка "{deriveNoteTitle(pendingDeleteNote)}" участвует в выводах о позиции автора. После удаления
              assertions будут пересчитаны.
            </p>
            <div className="inline-actions">
              <button className="btn btn-sec btn-sm" type="button" onClick={() => setPendingDeleteNote(null)}>
                Отмена
              </button>
              <button className="btn btn-pri btn-sm" type="button" onClick={() => deleteNote(pendingDeleteNote.id)}>
                Удалить
              </button>
            </div>
          </div>
        </div>
      ) : null}
    </div>
  );
}

function AuthorNoteCard({
  assertions,
  editBody,
  editAttachmentError,
  editAttachments,
  editSourceUrl,
  editTags,
  editTitle,
  editingId,
  expanded,
  note,
  onBeginEdit,
  onCancelEdit,
  onChangeEditBody,
  onChangeEditSourceUrl,
  onChangeEditTags,
  onChangeEditTitle,
  onDelete,
  onEditAttach,
  onEditRemoveAttachment,
  onSaveEdit,
  onToggleExpanded
}: {
  assertions: AuthorPositionAssertion[];
  editBody: string;
  editAttachmentError: string;
  editAttachments: AuthorAttachment[];
  editSourceUrl: string;
  editTags: string;
  editTitle: string;
  editingId: string | null;
  expanded: boolean;
  note: AuthorNote;
  onBeginEdit: (note: AuthorNote) => void;
  onCancelEdit: () => void;
  onChangeEditBody: (value: string) => void;
  onChangeEditSourceUrl: (value: string) => void;
  onChangeEditTags: (value: string) => void;
  onChangeEditTitle: (value: string) => void;
  onDelete: (note: AuthorNote) => void;
  onEditAttach: (file: File | undefined) => Promise<void>;
  onEditRemoveAttachment: () => void;
  onSaveEdit: (note: AuthorNote) => void;
  onToggleExpanded: () => void;
}) {
  const isEditing = editingId === note.id;
  const preview = buildLinkPreview(note.sourceUrl);
  const noteAttachments = note.attachments ?? [];
  const bodyIsLong = note.body.length > 420;
  const visibleBody = !bodyIsLong || expanded ? note.body : `${note.body.slice(0, 420)}...`;

  return (
    <article className="card memory-note">
      <div className="note-top">
        <span className="sig info">{authorNoteTypeLabel(note.type)}</span>
        <span className="sc">{formatDate(note.capturedAt)}</span>
        {isEvidenceNote(note.id, assertions) ? <span className="sc">evidence</span> : null}
        <div className="note-actions">
          <button className="link-button" type="button" onClick={() => onBeginEdit(note)}>
            Редактировать
          </button>
          <button className="link-button danger" type="button" onClick={() => onDelete(note)}>
            Удалить
          </button>
        </div>
      </div>
      {isEditing ? (
        <div className="note-edit">
          <label>
            Заголовок
            <input value={editTitle} onChange={(event) => onChangeEditTitle(event.target.value)} />
          </label>
          {note.type === 'linkReaction' ? (
            <label>
              Ссылка
              <input value={editSourceUrl} onChange={(event) => onChangeEditSourceUrl(event.target.value)} />
            </label>
          ) : null}
          <label>
            Текст
            <textarea value={editBody} onChange={(event) => onChangeEditBody(event.target.value)} />
          </label>
          <label>
            Теги
            <input value={editTags} onChange={(event) => onChangeEditTags(event.target.value)} />
          </label>
          {note.type !== 'manualCorrection' ? (
            <FileAttachmentPicker
              attachments={editAttachments}
              error={editAttachmentError}
              inputLabel="Файл заметки"
              onAttach={onEditAttach}
              onRemove={onEditRemoveAttachment}
            />
          ) : null}
          <div className="inline-actions">
            <button className="btn btn-pri btn-sm" type="button" onClick={() => onSaveEdit(note)} disabled={!editBody.trim()}>
              Сохранить
            </button>
            <button className="btn btn-sec btn-sm" type="button" onClick={onCancelEdit}>
              Отмена
            </button>
          </div>
        </div>
      ) : (
        <>
          <h3>{deriveNoteTitle(note)}</h3>
          {note.targetTitle ? <span className="target-chip">Корректировка: {note.targetTitle}</span> : null}
          <p>{visibleBody}</p>
          {bodyIsLong ? (
            <button className="link-button" type="button" onClick={onToggleExpanded}>
              {expanded ? 'Свернуть' : 'Показать полностью'}
            </button>
          ) : null}
          {preview.isValid ? <LinkPreviewCard preview={preview} /> : null}
          {noteAttachments.length > 0 ? <AttachmentList attachments={noteAttachments} /> : null}
          <div className="tag-row">
            {note.tags.map((tag) => (
              <span className="rub" key={tag}>
                {tag}
              </span>
            ))}
          </div>
        </>
      )}
    </article>
  );
}

function AssertionCard({
  assertion,
  onCorrect
}: {
  assertion: AuthorPositionAssertion;
  onCorrect: (target: CorrectionTarget) => void;
}) {
  return (
    <article className="assertion">
      <div className="assertion-head">
        <span className="rub">{assertionTypeLabel(assertion.type)}</span>
        <span className="sc">confidence {formatScore(assertion.confidence)}</span>
      </div>
      <h3>{assertion.title}</h3>
      <p>{assertion.statement}</p>
      <button
        className="btn btn-sec btn-sm"
        type="button"
        onClick={() => onCorrect({ type: 'assertion', id: assertion.id, title: assertion.title })}
      >
        Корректировать
      </button>
      <details>
        <summary>Evidence</summary>
        <div className="evidence-list">
          {assertion.evidence.map((item) => (
            <blockquote key={`${assertion.id}-${item.noteId}-${item.quote}`}>
              <p>{item.quote}</p>
              <cite>{item.reason}</cite>
              <button
                className="link-button"
                type="button"
                onClick={() => onCorrect(buildEvidenceCorrectionTarget(assertion, item))}
              >
                Корректировать evidence
              </button>
            </blockquote>
          ))}
        </div>
      </details>
    </article>
  );
}

function LinkPreviewCard({ preview }: { preview: LinkPreview }) {
  return (
    <a className="link-preview" href={preview.normalizedUrl} target="_blank" rel="noreferrer">
      <span>{preview.domain}</span>
      <b>{preview.title}</b>
      <small>{preview.normalizedUrl}</small>
    </a>
  );
}

function FileAttachmentPicker({
  attachments,
  error,
  inputLabel,
  onAttach,
  onRemove
}: {
  attachments: AuthorAttachment[];
  error: string;
  inputLabel: string;
  onAttach: (file: File | undefined) => Promise<void>;
  onRemove: () => void;
}) {
  return (
    <div className="file-picker">
      <label>
        {inputLabel}
        <input
          accept=".txt,.md,.pdf,.doc,.docx,image/*"
          aria-label={inputLabel}
          type="file"
          onChange={(event) => {
            void onAttach(event.target.files?.[0]);
            event.target.value = '';
          }}
        />
      </label>
      <p>До 1 MB. Файл хранится локально как материал к заметке и пока не анализируется.</p>
      {error ? <span className="form-error">{error}</span> : null}
      {attachments.length > 0 ? <AttachmentList attachments={attachments} onRemove={onRemove} /> : null}
    </div>
  );
}

function AttachmentList({
  attachments,
  onRemove
}: {
  attachments: AuthorAttachment[];
  onRemove?: () => void;
}) {
  return (
    <div className="attachment-list">
      {attachments.map((attachment) => (
        <div className="attachment-card" key={attachment.id}>
          {attachment.mimeType.startsWith('image/') ? (
            <img alt="" src={attachment.dataUrl} />
          ) : (
            <span className="attachment-icon">{attachmentTypeLabel(attachment)}</span>
          )}
          <div>
            <b>{attachment.fileName}</b>
            <small>
              {attachment.mimeType || 'file'} · {formatBytes(attachment.sizeBytes)} · локально
            </small>
          </div>
          {onRemove ? (
            <button className="link-button danger" type="button" onClick={onRemove}>
              Удалить файл
            </button>
          ) : null}
        </div>
      ))}
    </div>
  );
}

function SummaryItem({ label, value }: { label: string; value: number }) {
  return (
    <div className="summary-item">
      <b>{value}</b>
      <span>{label}</span>
    </div>
  );
}

function MemoryTabNav({
  active,
  onChange
}: {
  active: MemoryInternalTab;
  onChange: (tab: MemoryInternalTab) => void;
}) {
  const tabs: Array<[MemoryInternalTab, string]> = [
    ['feed', 'Лента'],
    ['sources', 'Источники'],
    ['queue', 'Очередь разбора'],
    ['archive', 'Архив']
  ];

  return (
    <div className="tabs memory-tabs" role="tablist" aria-label="Память автора">
      {tabs.map(([id, label]) => (
        <button
          className={`tab${active === id ? ' active' : ''}`}
          key={id}
          role="tab"
          type="button"
          aria-selected={active === id}
          onClick={() => onChange(id)}
        >
          {label}
        </button>
      ))}
    </div>
  );
}

function ExternalSourcesView({
  candidates,
  sources,
  onOpenQueue,
  onPatchSource
}: {
  candidates: ImportedMemoryCandidate[];
  sources: AuthorExternalSource[];
  onOpenQueue: (sourceId?: string) => void;
  onPatchSource: (source: AuthorExternalSource) => void;
}) {
  const [expandedSourceId, setExpandedSourceId] = useState(sources[0]?.id ?? '');

  return (
    <div className="import-workspace">
      <section className="card import-intro">
        <span className="rub">Local-first shell</span>
        <h3>Демо-источники без API</h3>
        <p>
          Здесь показана будущая карта источников автора: архив TG-канала, интервью, блог, доклад и ручные uploads.
          Кандидаты mock/deterministic; Telegram, OAuth, crawlers и AI-анализ не подключены.
        </p>
      </section>
      <div className="source-list" data-testid="external-source-list">
        {sources.map((source) => {
          const sourceCandidates = candidates.filter((candidate) => candidate.sourceId === source.id);
          const needsReview = sourceCandidates.filter((candidate) => candidate.reviewStatus === 'new').length;
          const isExpanded = expandedSourceId === source.id;

          return (
            <article className={`card source-row${isExpanded ? ' expanded' : ''}`} data-testid="source-row" key={source.id}>
              <div className="source-row-main">
                <div className="source-row-title">
                  <span className="sig info">{sourceTypeLabel(source.type)}</span>
                  <button
                    className="entity-title-button source-title-button"
                    type="button"
                    aria-expanded={isExpanded}
                    onClick={() => setExpandedSourceId(isExpanded ? '' : source.id)}
                  >
                    {source.title}
                  </button>
                </div>
                <span className={`pill ${source.status === 'paused' ? 'pin' : 'ok'}`}>
                  <i />
                  {sourceStatusLabel(source.status)}
                </span>
              </div>
              <div className="source-row-meta-bar">
                <span className="entity-row-meta">{importModeLabel(source.importMode)}</span>
                <span className="entity-row-meta">
                  {sourceCandidates.length} total · {needsReview} review
                </span>
                <span className="entity-row-meta">checked {source.lastCheckedAt || 'нет'}</span>
              </div>
              {isExpanded ? (
                <div className="source-row-details">
                  <p>{source.notes}</p>
                  <dl className="entity-detail-list">
                <dt>Mode</dt>
                <dd>{importModeLabel(source.importMode)}</dd>
                <dt>Candidates</dt>
                <dd>
                  {sourceCandidates.length} total · {needsReview} review
                </dd>
                <dt>Checked</dt>
                <dd>{source.lastCheckedAt || 'не проверялся'}</dd>
                <dt>Imported</dt>
                <dd>{source.lastImportedAt || 'нет импорта'}</dd>
                  </dl>
                </div>
              ) : null}
              <div className="source-row-actions">
                <button className="btn btn-pri btn-sm" type="button" onClick={() => onOpenQueue(source.id)}>
                  Открыть очередь
                </button>
                <button
                  className="btn btn-sec btn-sm"
                  type="button"
                  onClick={() =>
                    onPatchSource({
                      ...source,
                      status: source.status === 'paused' ? 'needsReview' : 'paused'
                    })
                  }
                >
                  {source.status === 'paused' ? 'Возобновить' : 'Пауза'}
                </button>
                <button
                  className="btn btn-sec btn-sm"
                  type="button"
                  onClick={() => onPatchSource({ ...source, lastCheckedAt: new Date().toISOString().slice(0, 10) })}
                >
                  Проверить вручную
                </button>
              </div>
            </article>
          );
        })}
      </div>
    </div>
  );
}

function ImportQueueView({
  candidates,
  filteredCandidates,
  filters,
  groups,
  groupMode,
  selectedCandidateIds,
  sources,
  viewMode,
  onAcceptToArchive,
  onAcceptToMemory,
  onChangeFilters,
  onChangeGroupMode,
  onChangeViewMode,
  onIgnoreEvidence,
  onOpenBulk,
  onReject,
  onClearSelection,
  onSelect,
  onSelectAllFiltered,
  onSelectPage,
  onUnselectAllFiltered,
  onUnselectPage
}: {
  candidates: ImportedMemoryCandidate[];
  filteredCandidates: ImportedMemoryCandidate[];
  filters: ImportCandidateFilters;
  groups: ReturnType<typeof groupImportCandidates>;
  groupMode: ImportCandidateGroupType;
  selectedCandidateIds: string[];
  sources: AuthorExternalSource[];
  viewMode: ImportViewMode;
  onAcceptToArchive: (candidate: ImportedMemoryCandidate) => void;
  onAcceptToMemory: (candidate: ImportedMemoryCandidate) => void;
  onChangeFilters: (filters: ImportCandidateFilters) => void;
  onChangeGroupMode: (mode: ImportCandidateGroupType) => void;
  onChangeViewMode: (mode: ImportViewMode) => void;
  onIgnoreEvidence: (candidate: ImportedMemoryCandidate) => void;
  onOpenBulk: (action: PendingBulkAction) => void;
  onReject: (candidate: ImportedMemoryCandidate) => void;
  onClearSelection: () => void;
  onSelect: (candidateId: string) => void;
  onSelectAllFiltered: () => void;
  onSelectPage: () => void;
  onUnselectAllFiltered: () => void;
  onUnselectPage: () => void;
}) {
  const actionableSelected = selectedCandidateIds.filter((id) =>
    candidates.some((candidate) => candidate.id === id && candidate.reviewStatus === 'new')
  );
  const pageCandidateIds = filteredCandidates.slice(0, 10).map((candidate) => candidate.id);
  const filteredCandidateIds = filteredCandidates.map((candidate) => candidate.id);
  const allPageSelected =
    pageCandidateIds.length > 0 && pageCandidateIds.every((candidateId) => selectedCandidateIds.includes(candidateId));
  const allFilteredSelected =
    filteredCandidateIds.length > 0 &&
    filteredCandidateIds.every((candidateId) => selectedCandidateIds.includes(candidateId));

  function patchFilters(patch: ImportCandidateFilters) {
    onChangeFilters({ ...filters, ...patch });
  }

  return (
    <div className="import-workspace">
      <section className="card import-notice">
        <b>Архивные и неразобранные материалы не меняют выводы о позиции автора.</b>
        <span>Очередь показывает mock candidates без API и без AI-анализа. Evidence включается только после действия «В память».</span>
      </section>
      <section className="card import-toolbar-panel">
        <div className="import-filter-grid">
          <label>
            Источник
            <select value={filters.sourceId ?? 'all'} onChange={(event) => patchFilters({ sourceId: event.target.value })}>
              <option value="all">Все источники</option>
              {sources.map((source) => (
                <option key={source.id} value={source.id}>
                  {source.title}
                </option>
              ))}
            </select>
          </label>
          <label>
            Статус
            <select
              value={filters.reviewStatus ?? 'all'}
              onChange={(event) => patchFilters({ reviewStatus: event.target.value as ImportReviewStatus | 'all' })}
            >
              <option value="all">Все</option>
              <option value="new">Новые</option>
              <option value="acceptedToMemory">В памяти</option>
              <option value="acceptedToArchive">Принятые из очереди</option>
              <option value="bulkAcceptedToArchive">Bulk archive из очереди</option>
              <option value="rejected">Отклонены</option>
              <option value="ignoredForEvidence">Не evidence</option>
            </select>
          </label>
          <label>
            Evidence policy
            <select
              value={filters.evidencePolicy ?? 'all'}
              onChange={(event) => patchFilters({ evidencePolicy: event.target.value as EvidencePolicy | 'all' })}
            >
              <option value="all">Любая</option>
              <option value="canSupportAssertions">Может поддержать выводы</option>
              <option value="archiveOnly">Только архив</option>
              <option value="ignored">Игнорировать</option>
            </select>
          </label>
          <label>
            Duplicate risk
            <select
              value={filters.duplicateRisk ?? 'all'}
              onChange={(event) => patchFilters({ duplicateRisk: event.target.value as ImportRiskLevel | 'all' })}
            >
              <option value="all">Любой</option>
              <option value="low">Low</option>
              <option value="medium">Medium</option>
              <option value="high">High</option>
            </select>
          </label>
        </div>
        <label className="import-search">
          Поиск
          <input
            value={filters.query ?? ''}
            onChange={(event) => patchFilters({ query: event.target.value })}
            placeholder="tag, title, excerpt..."
          />
        </label>
        <div className="bulk-bar">
          <span>
            Показано {filteredCandidates.length} из {candidates.length}; выбрано {selectedCandidateIds.length}
          </span>
          <button className="btn btn-sec btn-sm" type="button" onClick={allPageSelected ? onUnselectPage : onSelectPage}>
            {allPageSelected ? 'Снять выделение со страницы' : 'Выбрать все на странице'}
          </button>
          <button
            className="btn btn-sec btn-sm"
            type="button"
            onClick={allFilteredSelected ? onUnselectAllFiltered : onSelectAllFiltered}
          >
            {allFilteredSelected ? 'Снять выделение по фильтру' : 'Выбрать все по фильтру'}
          </button>
          {selectedCandidateIds.length > 0 ? (
            <button className="btn btn-sec btn-sm" type="button" onClick={onClearSelection}>
              Сбросить выделение
            </button>
          ) : null}
          <button
            className="btn btn-pri btn-sm"
            type="button"
            disabled={filteredCandidates.length === 0}
            onClick={() =>
              onOpenBulk({
                action: 'archive',
                candidateIds: selectedCandidateIds.length > 0 ? selectedCandidateIds : filteredCandidates.map((candidate) => candidate.id),
                destination: 'Архив'
              })
            }
          >
            Добавить все
          </button>
          <button
            className="btn btn-sec btn-sm"
            type="button"
            disabled={actionableSelected.length === 0}
            onClick={() =>
              onOpenBulk({
                action: 'archive',
                candidateIds: actionableSelected,
                destination: 'Архив'
              })
            }
          >
            Принять выбранные в архив
          </button>
          <button
            className="btn btn-sec btn-sm"
            type="button"
            disabled={actionableSelected.length === 0}
            onClick={() =>
              onOpenBulk({
                action: 'reject',
                candidateIds: actionableSelected,
                destination: 'Отклонено'
              })
            }
          >
            Отклонить выбранные
          </button>
        </div>
        <div className="view-toggle">
          <button className={`tab${viewMode === 'list' ? ' active' : ''}`} type="button" onClick={() => onChangeViewMode('list')}>
            Список
          </button>
          <button className={`tab${viewMode === 'groups' ? ' active' : ''}`} type="button" onClick={() => onChangeViewMode('groups')}>
            Группы
          </button>
          {viewMode === 'groups' ? (
            <select value={groupMode} onChange={(event) => onChangeGroupMode(event.target.value as ImportCandidateGroupType)}>
              <option value="source">По источнику</option>
              <option value="status">По статусу</option>
              <option value="duplicateRisk">По дублям</option>
              <option value="evidencePolicy">По evidence</option>
              <option value="tag">По тегу</option>
            </select>
          ) : null}
        </div>
      </section>
      {viewMode === 'groups' ? (
        <div className="import-groups">
          {groups.map((group) => (
            <article className="card import-group" key={group.id}>
              <div>
                <span className={`risk-dot ${group.riskLevel}`} />
                <b>{group.title}</b>
              </div>
              <span>{group.summary}</span>
              <small>{group.candidateIds.join(', ')}</small>
            </article>
          ))}
        </div>
      ) : (
        <div className="candidate-list">
          {filteredCandidates.map((candidate) => (
            <CandidateCard
              candidate={candidate}
              key={candidate.id}
              selected={selectedCandidateIds.includes(candidate.id)}
              source={sources.find((item) => item.id === candidate.sourceId)}
              onAcceptToArchive={onAcceptToArchive}
              onAcceptToMemory={onAcceptToMemory}
              onIgnoreEvidence={onIgnoreEvidence}
              onReject={onReject}
              onSelect={onSelect}
            />
          ))}
          {filteredCandidates.length === 0 ? <EmptyState text="В очереди нет кандидатов под выбранные фильтры." /> : null}
        </div>
      )}
    </div>
  );
}

function CandidateCard({
  candidate,
  selected,
  source,
  onAcceptToArchive,
  onAcceptToMemory,
  onIgnoreEvidence,
  onReject,
  onSelect
}: {
  candidate: ImportedMemoryCandidate;
  selected: boolean;
  source?: AuthorExternalSource;
  onAcceptToArchive: (candidate: ImportedMemoryCandidate) => void;
  onAcceptToMemory: (candidate: ImportedMemoryCandidate) => void;
  onIgnoreEvidence: (candidate: ImportedMemoryCandidate) => void;
  onReject: (candidate: ImportedMemoryCandidate) => void;
  onSelect: (candidateId: string) => void;
}) {
  const disabled = candidate.reviewStatus !== 'new';

  return (
    <article className={`card candidate-card ${disabled ? 'muted' : ''}`}>
      <label className="candidate-check">
        <input
          type="checkbox"
          checked={selected}
          disabled={disabled}
          onChange={() => onSelect(candidate.id)}
          aria-label={`Выбрать ${candidate.title}`}
        />
      </label>
      <div className="candidate-body">
        <div className="candidate-head">
          <span className="sig info">{source?.title ?? candidate.sourceId}</span>
          <span className={`sc risk-${candidate.duplicateRisk}`}>duplicate {duplicateRiskLabel(candidate.duplicateRisk)}</span>
          <span className="sc">{reviewStatusLabel(candidate.reviewStatus)}</span>
        </div>
        <h3>{candidate.title}</h3>
        <p>{candidate.excerpt}</p>
        <dl className="meta-list">
          <dt>Captured</dt>
          <dd>{candidate.capturedAt}</dd>
          <dt>Target</dt>
          <dd>{candidate.suggestedTarget}</dd>
          <dt>Policy</dt>
          <dd>{evidencePolicyLabel(candidate.evidencePolicy)}</dd>
          <dt>Provenance</dt>
          <dd>{candidate.originalUrl || source?.fileReference || source?.url || 'local mock candidate'}</dd>
        </dl>
        <div className="tag-row">
          {candidate.detectedTags.map((tag) => (
            <span className="rub" key={tag}>
              {tag}
            </span>
          ))}
        </div>
        <div className="inline-actions">
          <button className="btn btn-pri btn-sm" type="button" disabled={disabled} onClick={() => onAcceptToMemory(candidate)}>
            В память
          </button>
          <button className="btn btn-sec btn-sm" type="button" disabled={disabled} onClick={() => onAcceptToArchive(candidate)}>
            В архив
          </button>
          <button className="btn btn-sec btn-sm" type="button" disabled={disabled} onClick={() => onReject(candidate)}>
            Отклонить
          </button>
          <button className="btn btn-sec btn-sm" type="button" disabled={disabled} onClick={() => onIgnoreEvidence(candidate)}>
            Не evidence
          </button>
        </div>
      </div>
    </article>
  );
}

function ArchiveView({
  records,
  sources,
  onAcceptToMemory,
  onDelete,
  onIgnoreEvidence,
  onRestoreToQueue
}: {
  records: ArchiveRecord[];
  sources: AuthorExternalSource[];
  onAcceptToMemory: (record: ArchiveRecord) => void;
  onDelete: (recordId: string) => void;
  onIgnoreEvidence: (record: ArchiveRecord) => void;
  onRestoreToQueue: (record: ArchiveRecord) => void;
}) {
  return (
    <div className="archive-list">
      <section className="card import-notice">
        <b>Архив хранит контекст, но не является active evidence.</b>
        <span>Чтобы материал влиял на позицию автора, примите конкретного кандидата во вкладке «Очередь разбора» через «В память».</span>
      </section>
      {records.map((record) => (
        <article className="card archive-card" key={record.id}>
          <div className="candidate-head">
            <span className="sig info">{sources.find((source) => source.id === record.sourceId)?.title ?? record.sourceId}</span>
            <span className="sc">{record.acceptanceMode === 'bulk' ? 'bulk accepted' : 'manual accepted'}</span>
            <span className="sc">{record.id.startsWith('archive-seeded') ? 'исторический архив' : 'из очереди'}</span>
            <span className="sc">{evidencePolicyLabel(record.evidencePolicy)}</span>
          </div>
          <h3>{record.title}</h3>
          <p>{record.bodyExcerpt}</p>
          <dl className="meta-list">
            <dt>Published</dt>
            <dd>{record.publishedAt}</dd>
            <dt>Accepted</dt>
            <dd>{formatDate(record.acceptedAt)}</dd>
            <dt>Original</dt>
            <dd>{record.originalUrl || 'local archive record'}</dd>
          </dl>
          <div className="inline-actions">
            <button className="btn btn-pri btn-sm" type="button" onClick={() => onAcceptToMemory(record)}>
              Добавить в память
            </button>
            <button className="btn btn-sec btn-sm" type="button" onClick={() => onRestoreToQueue(record)}>
              Вернуть в очередь
            </button>
            <button className="btn btn-sec btn-sm" type="button" onClick={() => onIgnoreEvidence(record)}>
              Не evidence
            </button>
            {record.originalUrl ? (
              <a className="btn btn-sec btn-sm" href={record.originalUrl} target="_blank" rel="noreferrer">
                Открыть источник
              </a>
            ) : null}
            <button className="btn btn-sec btn-sm" type="button" onClick={() => onDelete(record.id)}>
              Удалить из архива
            </button>
          </div>
        </article>
      ))}
      {records.length === 0 ? <EmptyState text="Архив пока пуст." /> : null}
    </div>
  );
}

function BulkActionDialog({
  action,
  candidates,
  filters,
  onCancel,
  onConfirm
}: {
  action: PendingBulkAction;
  candidates: ImportedMemoryCandidate[];
  filters: ImportCandidateFilters;
  onCancel: () => void;
  onConfirm: () => void;
}) {
  const highDuplicateCount = candidates.filter((candidate) => candidate.duplicateRisk === 'high').length;
  const activeEvidenceCount = candidates.filter((candidate) => candidate.evidencePolicy === 'canSupportAssertions').length;

  return (
    <div className="confirm-popover" role="dialog" aria-label="Подтверждение группового действия">
      <div className="card bulk-confirm">
        <h3>{action.action === 'archive' ? 'Добавить все в архив?' : 'Отклонить выбранные?'}</h3>
        <p>
          Будет обработано {candidates.length} кандидатов. Назначение: {action.destination}. Активные фильтры: {formatImportFilters(filters)}.
        </p>
        <dl className="meta-list">
          <dt>High duplicate</dt>
          <dd>{highDuplicateCount}</dd>
          <dt>Can support assertions</dt>
          <dd>{activeEvidenceCount}</dd>
          <dt>Evidence impact</dt>
          <dd>Архив и отклонение не меняют блок «Как система поняла автора».</dd>
        </dl>
        <div className="inline-actions">
          <button className="btn btn-sec btn-sm" type="button" onClick={onCancel}>
            Отмена
          </button>
          <button className="btn btn-pri btn-sm" type="button" onClick={onConfirm}>
            Подтвердить
          </button>
        </div>
      </div>
    </div>
  );
}

type EditorialModelTab = 'publisher' | 'topics' | 'fabulas' | 'matrix';

const EDITORIAL_TABS: Array<[EditorialModelTab, string]> = [
  ['publisher', 'Издательство'],
  ['topics', 'Темы'],
  ['fabulas', 'Фабулы'],
  ['matrix', 'Матрица']
];

function EditorialModelView({
  activeTab,
  chatIntent,
  workspace,
  projectProfile,
  editorialRules,
  topics,
  fabulas,
  matrix,
  onProjectProfileChange,
  onEditorialRulesChange,
  onTopicsChange,
  onFabulasChange,
  onMatrixChange,
  onTopicsAndMatrixChange,
  onFabulasAndMatrixChange,
  onChangeTab,
  onChatIntentConsumed,
  onRunValidation
}: {
  activeTab: EditorialModelTab;
  chatIntent: ContextChatIntent | null;
  workspace: WorkspaceState;
  model: EditorialModel;
  projectProfile: ProjectProfile;
  editorialRules: EditorialRule[];
  topics: Topic[];
  fabulas: Fabula[];
  matrix: TopicFabulaMatrixEntry[];
  onModelChange: (model: EditorialModel) => void;
  onProjectProfileChange: (profile: ProjectProfile) => void;
  onEditorialRulesChange: (rules: EditorialRule[]) => void;
  onTopicsChange: (topics: Topic[]) => void;
  onFabulasChange: (fabulas: Fabula[]) => void;
  onMatrixChange: (matrix: TopicFabulaMatrixEntry[]) => void;
  onTopicsAndMatrixChange: (topics: Topic[], matrix: TopicFabulaMatrixEntry[]) => void;
  onFabulasAndMatrixChange: (fabulas: Fabula[], matrix: TopicFabulaMatrixEntry[]) => void;
  onChangeTab: (tab: EditorialModelTab) => void;
  onChatIntentConsumed: () => void;
  onRunValidation: () => void;
}) {
  const tab = activeTab;
  const setTab = onChangeTab;
  const warnings = getTopicFabulaWarnings(topics, fabulas, matrix);
  const enabledPairs = matrix.filter((entry) => entry.enabled).length;

  function saveRule(rule: EditorialRule) {
    const exists = editorialRules.some((item) => item.id === rule.id);
    onEditorialRulesChange(exists ? updateEditorialRule(editorialRules, rule) : [rule, ...editorialRules]);
  }

  function removeRule(ruleId: string) {
    onEditorialRulesChange(deleteEditorialRule(editorialRules, ruleId));
  }

  function updateTopic(topic: Topic) {
    onTopicsChange(topics.map((item) => (item.id === topic.id ? topic : item)));
  }

  function createTopic(topic: Topic) {
    const nextTopics = addTopic(topics, topic);
    onTopicsAndMatrixChange(nextTopics, completeTopicFabulaMatrix(nextTopics, fabulas, matrix));
  }

  function removeTopic(topicId: string) {
    const result = deleteTopic(topics, matrix, topicId);
    onTopicsAndMatrixChange(result.topics, result.matrix);
  }

  function updateFabula(fabula: Fabula) {
    onFabulasChange(fabulas.map((item) => (item.id === fabula.id ? fabula : item)));
  }

  function createFabula(fabula: Fabula) {
    const nextFabulas = addFabula(fabulas, fabula);
    onFabulasAndMatrixChange(nextFabulas, completeTopicFabulaMatrix(topics, nextFabulas, matrix));
  }

  function removeFabula(fabulaId: string) {
    const result = deleteFabula(fabulas, matrix, fabulaId);
    onFabulasAndMatrixChange(result.fabulas, result.matrix);
  }

  return (
    <div className="page wide fade-up">
      <ProjectProfileHeader
        enabledPairs={enabledPairs}
        fabulaCount={fabulas.length}
        profile={projectProfile}
        topicCount={topics.length}
        warningCount={warnings.length}
        onSave={onProjectProfileChange}
      />
      <div className="tabs memory-tabs model-tabs" role="tablist" aria-label="Редакционная модель">
        {EDITORIAL_TABS.map(([id, label]) => (
          <button
            aria-selected={tab === id}
            className={`tab${tab === id ? ' active' : ''}`}
            key={id}
            role="tab"
            type="button"
            onClick={() => setTab(id)}
          >
            {label}
          </button>
        ))}
      </div>
      <div className="editorial-workspace">
        <div className="editorial-main">
          {tab === 'publisher' ? (
            <PublisherRulesView
              chatIntent={chatIntent?.actionType === 'addEditorialRule' ? chatIntent : null}
              rules={editorialRules}
              onChatIntentConsumed={onChatIntentConsumed}
              onDelete={removeRule}
              onSave={saveRule}
            />
          ) : null}
          {tab === 'topics' ? (
            <TopicListView
              chatIntent={chatIntent?.actionType === 'addTopic' ? chatIntent : null}
              fabulas={fabulas}
              matrix={matrix}
              referencedTopicIds={getReferencedTopicIds(workspace)}
              topics={topics}
              onCreate={createTopic}
              onChatIntentConsumed={onChatIntentConsumed}
              onDelete={removeTopic}
              onSave={updateTopic}
            />
          ) : null}
          {tab === 'fabulas' ? (
            <FabulaListView
              chatIntent={chatIntent?.actionType === 'addFabula' ? chatIntent : null}
              fabulas={fabulas}
              matrix={matrix}
              referencedFabulaIds={getReferencedFabulaIds(workspace)}
              topics={topics}
              onCreate={createFabula}
              onChatIntentConsumed={onChatIntentConsumed}
              onDelete={removeFabula}
              onSave={updateFabula}
            />
          ) : null}
          {tab === 'matrix' ? (
            <TopicFabulaMatrixView fabulas={fabulas} matrix={matrix} topics={topics} onSave={onMatrixChange} />
          ) : null}
        </div>
        <EditorialValidationPanel
          activeTab={tab}
          currentRevision={workspace.editorialSetupRevision ?? 0}
          validationRun={workspace.editorialValidationRun}
          onRunValidation={onRunValidation}
        />
      </div>
    </div>
  );
}

const RULE_SECTIONS: Array<{ title: string; description: string; groups: EditorialRuleGroup[] }> = [
  {
    title: 'Автор',
    description: 'Характеристики образа автора, которые потом должны проверяться в тексте.',
    groups: ['author']
  },
  {
    title: 'Аудитория',
    description: 'Кому пишем и какую пользу читатель должен получать.',
    groups: ['audience']
  },
  {
    title: 'Позиция',
    description: 'Что автор утверждает, с чем спорит и какую оптику удерживает.',
    groups: ['positioning']
  },
  {
    title: 'Стиль',
    description: 'Голос, язык, ритм, anti-AI-паттерны и запрещенные формулировки.',
    groups: ['styleVoice', 'styleLanguage', 'styleRhythm', 'antiAiPattern']
  },
  {
    title: 'Цели',
    description: 'Зачем существует блог и что должно поддерживаться каждым выпуском.',
    groups: ['goal']
  },
  {
    title: 'Запреты',
    description: 'Темы, углы и обещания, которые нельзя протаскивать в публикации.',
    groups: ['forbiddenTopic']
  }
];

function ProjectProfileHeader({
  profile,
  topicCount,
  fabulaCount,
  enabledPairs,
  warningCount,
  onSave
}: {
  profile: ProjectProfile;
  topicCount: number;
  fabulaCount: number;
  enabledPairs: number;
  warningCount: number;
  onSave: (profile: ProjectProfile) => void;
}) {
  const [editing, setEditing] = useState(false);
  const [draft, setDraft] = useState(profile);

  useEffect(() => {
    if (!editing) setDraft(profile);
  }, [editing, profile]);

  function save() {
    onSave(draft);
    setEditing(false);
  }

  return (
    <section className="card project-profile-header">
      <div className="project-profile-main">
        <span className="mono-label">Проект</span>
        {editing ? (
          <div className="profile-edit-grid">
            <label>
              Название
              <input value={draft.name} onChange={(event) => setDraft({ ...draft, name: event.target.value })} />
            </label>
            <label>
              Описание
              <textarea
                value={draft.description}
                onChange={(event) => setDraft({ ...draft, description: event.target.value })}
              />
            </label>
            <label>
              Статус настройки
              <select
                value={draft.setupStatus}
                onChange={(event) =>
                  setDraft({ ...draft, setupStatus: event.target.value as ProjectProfile['setupStatus'] })
                }
              >
                <option value="draft">Черновик</option>
                <option value="needsReview">Нужна проверка</option>
                <option value="validated">Проверено</option>
              </select>
            </label>
          </div>
        ) : (
          <>
            <h2>{profile.name}</h2>
            <p>{profile.description}</p>
          </>
        )}
      </div>
      <div className="project-profile-meta">
        <div>
          <b>{topicCount}</b>
          <span>тем</span>
        </div>
        <div>
          <b>{fabulaCount}</b>
          <span>фабул</span>
        </div>
        <div>
          <b>{enabledPairs}</b>
          <span>активных связок</span>
        </div>
        <div className={warningCount > 0 ? 'warn' : 'ok'}>
          <b>{warningCount}</b>
          <span>предупреждений</span>
        </div>
      </div>
      <div className="inline-actions">
        {editing ? (
          <>
            <button className="btn btn-sec btn-sm" type="button" onClick={() => setEditing(false)}>
              Отменить
            </button>
            <button className="btn btn-pri btn-sm" type="button" onClick={save}>
              Сохранить
            </button>
          </>
        ) : (
          <button className="btn btn-sec btn-sm" type="button" onClick={() => setEditing(true)}>
            Редактировать проект
          </button>
        )}
      </div>
    </section>
  );
}

function PublisherRulesView({
  chatIntent,
  rules,
  onChatIntentConsumed,
  onSave,
  onDelete
}: {
  chatIntent: Extract<ContextChatIntent, { actionType: 'addEditorialRule' }> | null;
  rules: EditorialRule[];
  onChatIntentConsumed: () => void;
  onSave: (rule: EditorialRule) => void;
  onDelete: (ruleId: string) => void;
}) {
  return (
    <div className="rule-sections">
      {RULE_SECTIONS.map((section) => (
        <RuleSection
          chatIntent={chatIntent && section.groups.includes(chatIntent.payload.group) ? chatIntent : null}
          key={section.title}
          rules={rules}
          section={section}
          onChatIntentConsumed={onChatIntentConsumed}
          onDelete={onDelete}
          onSave={onSave}
        />
      ))}
    </div>
  );
}

function RuleSection({
  chatIntent,
  section,
  rules,
  onChatIntentConsumed,
  onSave,
  onDelete
}: {
  chatIntent: Extract<ContextChatIntent, { actionType: 'addEditorialRule' }> | null;
  section: { title: string; description: string; groups: EditorialRuleGroup[] };
  rules: EditorialRule[];
  onChatIntentConsumed: () => void;
  onSave: (rule: EditorialRule) => void;
  onDelete: (ruleId: string) => void;
}) {
  const sectionRules = rules.filter((rule) => section.groups.includes(rule.group));
  const [editingId, setEditingId] = useState<string | null>(null);
  const [draft, setDraft] = useState<EditorialRule | null>(null);

  function startAdd() {
    const group = section.groups[0];
    setEditingId('new');
    setDraft(createEditorialRule(group, '', ''));
  }

  useEffect(() => {
    if (!chatIntent) return;

    setEditingId('new');
    setDraft(createEditorialRule(chatIntent.payload.group, chatIntent.payload.title, chatIntent.payload.statement));
    onChatIntentConsumed();
  }, [chatIntent, onChatIntentConsumed]);

  function startEdit(rule: EditorialRule) {
    setEditingId(rule.id);
    setDraft({ ...rule });
  }

  function cancel() {
    setEditingId(null);
    setDraft(null);
  }

  function save() {
    if (!draft) return;
    onSave(draft);
    cancel();
  }

  return (
    <section className="card rule-section">
      <div className="rule-section-head">
        <div>
          <span className="mono-label">{section.title}</span>
          <p>{section.description}</p>
        </div>
        <button className="btn btn-sec btn-sm" type="button" onClick={startAdd}>
          + Правило
        </button>
      </div>
      <div className="rule-list">
        {editingId === 'new' && draft ? (
          <RuleEditor
            availableGroups={section.groups}
            rule={draft}
            onCancel={cancel}
            onChange={setDraft}
            onSave={save}
          />
        ) : null}
        {sectionRules.map((rule) =>
          editingId === rule.id && draft ? (
            <RuleEditor
              availableGroups={section.groups}
              key={rule.id}
              rule={draft}
              onCancel={cancel}
              onChange={setDraft}
              onSave={save}
            />
          ) : (
            <article className="rule-card" key={rule.id}>
              <div className="rule-card-main">
                <div className="rule-head">
                  <b>{rule.title}</b>
                  <span className={`status-chip ${rule.status}`}>{rule.status === 'active' ? 'активно' : 'пауза'}</span>
                </div>
                <p>{rule.statement}</p>
                <span className="sub">{editorialRuleGroupLabel(rule.group)}</span>
              </div>
              <div className="inline-actions">
                <button className="btn btn-sec btn-sm" type="button" onClick={() => startEdit(rule)}>
                  Редактировать
                </button>
                <button className="btn btn-sec btn-sm danger-text" type="button" onClick={() => onDelete(rule.id)}>
                  Удалить
                </button>
              </div>
            </article>
          )
        )}
        {sectionRules.length === 0 && editingId !== 'new' ? <EmptyState text="В этом блоке пока нет правил." /> : null}
      </div>
    </section>
  );
}

function RuleEditor({
  rule,
  availableGroups,
  onChange,
  onSave,
  onCancel
}: {
  rule: EditorialRule;
  availableGroups: EditorialRuleGroup[];
  onChange: (rule: EditorialRule) => void;
  onSave: () => void;
  onCancel: () => void;
}) {
  return (
    <article className="rule-card rule-edit">
      <label>
        Тип правила
        <select
          value={rule.group}
          onChange={(event) => onChange({ ...rule, group: event.target.value as EditorialRuleGroup })}
        >
          {availableGroups.map((group) => (
            <option key={group} value={group}>
              {editorialRuleGroupLabel(group)}
            </option>
          ))}
        </select>
      </label>
      <label>
        Название
        <input value={rule.title} onChange={(event) => onChange({ ...rule, title: event.target.value })} />
      </label>
      <label>
        Правило
        <textarea value={rule.statement} onChange={(event) => onChange({ ...rule, statement: event.target.value })} />
      </label>
      <label>
        Статус
        <select
          value={rule.status}
          onChange={(event) => onChange({ ...rule, status: event.target.value as EditorialRule['status'] })}
        >
          <option value="active">Активно</option>
          <option value="paused">Пауза</option>
        </select>
      </label>
      <div className="inline-actions">
        <button className="btn btn-sec btn-sm" type="button" onClick={onCancel}>
          Отменить
        </button>
        <button className="btn btn-pri btn-sm" type="button" onClick={onSave} disabled={!rule.title.trim() || !rule.statement.trim()}>
          Сохранить
        </button>
      </div>
    </article>
  );
}

function TopicListView({
  chatIntent,
  topics,
  fabulas,
  matrix,
  referencedTopicIds,
  onCreate,
  onChatIntentConsumed,
  onDelete,
  onSave
}: {
  chatIntent: Extract<ContextChatIntent, { actionType: 'addTopic' }> | null;
  topics: Topic[];
  fabulas: Fabula[];
  matrix: TopicFabulaMatrixEntry[];
  referencedTopicIds: Set<string>;
  onCreate: (topic: Topic) => void;
  onChatIntentConsumed: () => void;
  onDelete: (topicId: string) => void;
  onSave: (topic: Topic) => void;
}) {
  const [expandedId, setExpandedId] = useState<string | null>(topics[0]?.id ?? null);
  const [editingId, setEditingId] = useState<string | null>(null);
  const [draft, setDraft] = useState<Topic | null>(null);

  function startEdit(topic: Topic) {
    setExpandedId(topic.id);
    setEditingId(topic.id);
    setDraft({ ...topic, rules: [...topic.rules], forbiddenAngles: [...topic.forbiddenAngles] });
  }

  function startCreate() {
    if (editingId === 'new' && draft) {
      setExpandedId(draft.id);
      return;
    }

    const topic = createTopicDraft();
    setExpandedId(topic.id);
    setEditingId('new');
    setDraft(topic);
  }

  useEffect(() => {
    if (!chatIntent) return;

    const topic = {
      ...createTopicDraft(),
      ...chatIntent.payload,
      rules: chatIntent.payload.rules ? [...chatIntent.payload.rules] : [],
      forbiddenAngles: chatIntent.payload.forbiddenAngles ? [...chatIntent.payload.forbiddenAngles] : []
    };
    setExpandedId(topic.id);
    setEditingId('new');
    setDraft(topic);
    onChatIntentConsumed();
  }, [chatIntent, onChatIntentConsumed]);

  function save() {
    if (!draft) return;
    const normalized = { ...draft, weightRange: normalizeWeightRange(draft.weightRange) };
    if (editingId === 'new') {
      onCreate(normalized);
      setExpandedId(normalized.id);
    } else {
      onSave(normalized);
    }
    setEditingId(null);
    setDraft(null);
  }

  function remove(topic: Topic) {
    const hasProductionReferences = referencedTopicIds.has(topic.id);
    const message = hasProductionReferences
      ? `Тема "${topic.title}" уже используется в текущих производственных артефактах. Удаление уберет тему и ее связи в матрице, но не перепишет уже созданные инсайты, планы или фабулы постов. Удалить?`
      : `Удалить тему "${topic.title}" и все ее связи в матрице?`;

    if (!window.confirm(message)) return;

    onDelete(topic.id);
    if (expandedId === topic.id) setExpandedId(null);
    if (editingId === topic.id) {
      setEditingId(null);
      setDraft(null);
    }
  }

  return (
    <div className="entity-list">
      <div className="entity-list-toolbar">
        <span className="mono-label">{topics.length} тем</span>
        <button className="btn btn-sec btn-sm" type="button" onClick={startCreate}>
          + Тема
        </button>
      </div>
      {editingId === 'new' && draft ? (
        <article className="card entity-row">
          <div className="entity-row-main">
            <span className="entity-title-placeholder">{draft.title.trim() || 'Новая тема'}</span>
            <div className="entity-row-meta">
              <span className="entity-meta-chip">{draft.weightRange.min}-{draft.weightRange.max}%</span>
              <span className={`status-chip ${draft.status}`}>{draft.status === 'active' ? 'активно' : 'пауза'}</span>
              <span className="entity-meta-chip">{draft.rules.length} правил</span>
              <span className="entity-meta-chip">{fabulas.length} фабул</span>
            </div>
            <ValidationBadge status={draft.title.trim() ? 'green' : 'yellow'} />
          </div>
          <TopicEditor
            topic={draft}
            onCancel={() => {
              setEditingId(null);
              setDraft(null);
              setExpandedId(topics[0]?.id ?? null);
            }}
            onChange={setDraft}
            onSave={save}
          />
        </article>
      ) : null}
      {topics.map((topic) => {
        const compatibleCount = countCompatibleFabulas(topic.id, matrix);
        const isExpanded = expandedId === topic.id;
        const isEditing = editingId === topic.id && draft;
        return (
          <article className="card entity-row" key={topic.id}>
            <div className="entity-row-main">
              <button
                className="entity-title-button"
                type="button"
                onClick={() => setExpandedId(isExpanded ? null : topic.id)}
              >
                {topic.title}
              </button>
              <div className="entity-row-meta">
                <span className="entity-meta-chip">{topic.weightRange.min}-{topic.weightRange.max}%</span>
                <span className={`status-chip ${topic.status}`}>{topic.status === 'active' ? 'активно' : 'пауза'}</span>
                <span className="entity-meta-chip">{topic.rules.length} правил</span>
                <span className="entity-meta-chip">{compatibleCount} фабул</span>
              </div>
              <ValidationBadge status={compatibleCount > 0 ? 'green' : 'red'} />
            </div>
            {isExpanded ? (
              isEditing ? (
                <TopicEditor
                  topic={draft}
                  onCancel={() => {
                    setEditingId(null);
                    setDraft(null);
                  }}
                  onChange={setDraft}
                  onSave={save}
                />
              ) : (
                <div className="entity-details">
                  <div className="entity-details-scroll">
                    <p>{topic.description}</p>
                    <dl className="entity-detail-list">
                      <dt>Зачем</dt>
                      <dd>{topic.purpose}</dd>
                      <dt>Ценность</dt>
                      <dd>{topic.audienceValue}</dd>
                      <dt>Позиция автора</dt>
                      <dd>{topic.authorStance}</dd>
                      <dt>Правила</dt>
                      <dd>{topic.rules.join('; ')}</dd>
                      <dt>Запреты</dt>
                      <dd>{topic.forbiddenAngles.join('; ')}</dd>
                      <dt>Совместимые фабулы</dt>
                      <dd>{fabulas.filter((fabula) => isMatrixEnabled(topic.id, fabula.id, matrix)).map((fabula) => fabula.title).join(', ')}</dd>
                    </dl>
                  </div>
                  <div className="inline-actions">
                    <button className="btn btn-sec btn-sm" type="button" onClick={() => startEdit(topic)}>
                      Редактировать
                    </button>
                    <button className="btn btn-sec btn-sm danger-text" type="button" onClick={() => remove(topic)}>
                      Удалить
                    </button>
                  </div>
                </div>
              )
            ) : null}
          </article>
        );
      })}
    </div>
  );
}

function TopicEditor({
  topic,
  onChange,
  onSave,
  onCancel
}: {
  topic: Topic;
  onChange: (topic: Topic) => void;
  onSave: () => void;
  onCancel: () => void;
}) {
  return (
    <div className="entity-edit-form">
      <div className="entity-edit-scroll">
        <label>
          Название
          <input value={topic.title} onChange={(event) => onChange({ ...topic, title: event.target.value })} />
        </label>
        <label>
          Описание
          <textarea value={topic.description} onChange={(event) => onChange({ ...topic, description: event.target.value })} />
        </label>
        <label>
          Зачем эта тема
          <textarea value={topic.purpose} onChange={(event) => onChange({ ...topic, purpose: event.target.value })} />
        </label>
        <label>
          Ценность для аудитории
          <textarea value={topic.audienceValue} onChange={(event) => onChange({ ...topic, audienceValue: event.target.value })} />
        </label>
        <label>
          Позиция автора
          <textarea value={topic.authorStance} onChange={(event) => onChange({ ...topic, authorStance: event.target.value })} />
        </label>
        <WeightRangeEditor value={topic.weightRange} onChange={(weightRange) => onChange({ ...topic, weightRange })} />
        <label>
          Правила
          <textarea value={topic.rules.join('\n')} onChange={(event) => onChange({ ...topic, rules: splitLines(event.target.value) })} />
        </label>
        <label>
          Запреты
          <textarea
            value={topic.forbiddenAngles.join('\n')}
            onChange={(event) => onChange({ ...topic, forbiddenAngles: splitLines(event.target.value) })}
          />
        </label>
      </div>
      <div className="inline-actions">
        <button className="btn btn-sec btn-sm" type="button" onClick={onCancel}>
          Отменить
        </button>
        <button className="btn btn-pri btn-sm" type="button" onClick={onSave} disabled={!topic.title.trim()}>
          Сохранить
        </button>
      </div>
    </div>
  );
}

function FabulaListView({
  chatIntent,
  fabulas,
  topics,
  matrix,
  referencedFabulaIds,
  onCreate,
  onChatIntentConsumed,
  onDelete,
  onSave
}: {
  chatIntent: Extract<ContextChatIntent, { actionType: 'addFabula' }> | null;
  fabulas: Fabula[];
  topics: Topic[];
  matrix: TopicFabulaMatrixEntry[];
  referencedFabulaIds: Set<string>;
  onCreate: (fabula: Fabula) => void;
  onChatIntentConsumed: () => void;
  onDelete: (fabulaId: string) => void;
  onSave: (fabula: Fabula) => void;
}) {
  const [expandedId, setExpandedId] = useState<string | null>(fabulas[0]?.id ?? null);
  const [editingId, setEditingId] = useState<string | null>(null);
  const [draft, setDraft] = useState<Fabula | null>(null);

  function startEdit(fabula: Fabula) {
    setExpandedId(fabula.id);
    setEditingId(fabula.id);
    setDraft({ ...fabula, rules: [...fabula.rules], structure: [...fabula.structure], proofRequirements: [...fabula.proofRequirements] });
  }

  function startCreate() {
    if (editingId === 'new' && draft) {
      setExpandedId(draft.id);
      return;
    }

    const fabula = createFabulaDraft();
    setExpandedId(fabula.id);
    setEditingId('new');
    setDraft(fabula);
  }

  useEffect(() => {
    if (!chatIntent) return;

    const fabula = {
      ...createFabulaDraft(),
      ...chatIntent.payload,
      rules: chatIntent.payload.rules ? [...chatIntent.payload.rules] : [],
      structure: chatIntent.payload.structure ? [...chatIntent.payload.structure] : [],
      proofRequirements: chatIntent.payload.proofRequirements ? [...chatIntent.payload.proofRequirements] : []
    };
    setExpandedId(fabula.id);
    setEditingId('new');
    setDraft(fabula);
    onChatIntentConsumed();
  }, [chatIntent, onChatIntentConsumed]);

  function save() {
    if (!draft) return;
    const normalized = { ...draft, weightRange: normalizeWeightRange(draft.weightRange) };
    if (editingId === 'new') {
      onCreate(normalized);
      setExpandedId(normalized.id);
    } else {
      onSave(normalized);
    }
    setEditingId(null);
    setDraft(null);
  }

  function remove(fabula: Fabula) {
    const hasProductionReferences = referencedFabulaIds.has(fabula.id);
    const message = hasProductionReferences
      ? `Фабула "${fabula.title}" уже используется в текущих производственных артефактах. Удаление уберет фабулу и ее связи в матрице, но не перепишет уже созданные инсайты, планы или фабулы постов. Удалить?`
      : `Удалить фабулу "${fabula.title}" и все ее связи в матрице?`;

    if (!window.confirm(message)) return;

    onDelete(fabula.id);
    if (expandedId === fabula.id) setExpandedId(null);
    if (editingId === fabula.id) {
      setEditingId(null);
      setDraft(null);
    }
  }

  return (
    <div className="entity-list">
      <div className="entity-list-toolbar">
        <span className="mono-label">{fabulas.length} фабул</span>
        <button className="btn btn-sec btn-sm" type="button" onClick={startCreate}>
          + Фабула
        </button>
      </div>
      {editingId === 'new' && draft ? (
        <article className="card entity-row">
          <div className="entity-row-main">
            <span className="entity-title-placeholder">{draft.title.trim() || 'Новая фабула'}</span>
            <div className="entity-row-meta">
              <span className="entity-meta-chip">{draft.weightRange.min}-{draft.weightRange.max}%</span>
              <span className={`status-chip ${draft.status}`}>{draft.status === 'active' ? 'активно' : 'пауза'}</span>
              <span className="entity-meta-chip">{draft.rules.length} правил</span>
              <span className="entity-meta-chip">{draft.proofRequirements.length} proof</span>
              <span className="entity-meta-chip">{topics.length} тем</span>
            </div>
            <ValidationBadge status={draft.title.trim() ? 'green' : 'yellow'} />
          </div>
          <FabulaEditor
            fabula={draft}
            onCancel={() => {
              setEditingId(null);
              setDraft(null);
              setExpandedId(fabulas[0]?.id ?? null);
            }}
            onChange={setDraft}
            onSave={save}
          />
        </article>
      ) : null}
      {fabulas.map((fabula) => {
        const compatibleCount = countCompatibleTopics(fabula.id, matrix);
        const isExpanded = expandedId === fabula.id;
        const isEditing = editingId === fabula.id && draft;
        return (
          <article className="card entity-row" key={fabula.id}>
            <div className="entity-row-main">
              <button
                className="entity-title-button"
                type="button"
                onClick={() => setExpandedId(isExpanded ? null : fabula.id)}
              >
                {fabula.title}
              </button>
              <div className="entity-row-meta">
                <span className="entity-meta-chip">{fabula.weightRange.min}-{fabula.weightRange.max}%</span>
                <span className={`status-chip ${fabula.status}`}>{fabula.status === 'active' ? 'активно' : 'пауза'}</span>
                <span className="entity-meta-chip">{fabula.rules.length} правил</span>
                <span className="entity-meta-chip">{fabula.proofRequirements.length} proof</span>
                <span className="entity-meta-chip">{compatibleCount} тем</span>
              </div>
              <ValidationBadge status={compatibleCount > 0 ? 'green' : 'red'} />
            </div>
            {isExpanded ? (
              isEditing ? (
                <FabulaEditor
                  fabula={draft}
                  onCancel={() => {
                    setEditingId(null);
                    setDraft(null);
                  }}
                  onChange={setDraft}
                  onSave={save}
                />
              ) : (
                <div className="entity-details">
                  <div className="entity-details-scroll">
                    <p>{fabula.description}</p>
                    <dl className="entity-detail-list">
                      <dt>Драматургия</dt>
                      <dd>{fabula.dramaturgy}</dd>
                      <dt>Структура</dt>
                      <dd>{fabula.structure.join('; ')}</dd>
                      <dt>Proof requirements</dt>
                      <dd>{fabula.proofRequirements.join('; ')}</dd>
                      <dt>Правила</dt>
                      <dd>{fabula.rules.join('; ')}</dd>
                      <dt>Применимые темы</dt>
                      <dd>{topics.filter((topic) => isMatrixEnabled(topic.id, fabula.id, matrix)).map((topic) => topic.title).join(', ')}</dd>
                    </dl>
                  </div>
                  <div className="inline-actions">
                    <button className="btn btn-sec btn-sm" type="button" onClick={() => startEdit(fabula)}>
                      Редактировать
                    </button>
                    <button className="btn btn-sec btn-sm danger-text" type="button" onClick={() => remove(fabula)}>
                      Удалить
                    </button>
                  </div>
                </div>
              )
            ) : null}
          </article>
        );
      })}
    </div>
  );
}

function FabulaEditor({
  fabula,
  onChange,
  onSave,
  onCancel
}: {
  fabula: Fabula;
  onChange: (fabula: Fabula) => void;
  onSave: () => void;
  onCancel: () => void;
}) {
  return (
    <div className="entity-edit-form">
      <div className="entity-edit-scroll">
        <label>
          Название
          <input value={fabula.title} onChange={(event) => onChange({ ...fabula, title: event.target.value })} />
        </label>
        <label>
          Описание
          <textarea value={fabula.description} onChange={(event) => onChange({ ...fabula, description: event.target.value })} />
        </label>
        <label>
          Драматургия
          <textarea value={fabula.dramaturgy} onChange={(event) => onChange({ ...fabula, dramaturgy: event.target.value })} />
        </label>
        <WeightRangeEditor value={fabula.weightRange} onChange={(weightRange) => onChange({ ...fabula, weightRange })} />
        <label>
          Структура
          <textarea value={fabula.structure.join('\n')} onChange={(event) => onChange({ ...fabula, structure: splitLines(event.target.value) })} />
        </label>
        <label>
          Proof requirements
          <textarea
            value={fabula.proofRequirements.join('\n')}
            onChange={(event) => onChange({ ...fabula, proofRequirements: splitLines(event.target.value) })}
          />
        </label>
        <label>
          Правила
          <textarea value={fabula.rules.join('\n')} onChange={(event) => onChange({ ...fabula, rules: splitLines(event.target.value) })} />
        </label>
      </div>
      <div className="inline-actions">
        <button className="btn btn-sec btn-sm" type="button" onClick={onCancel}>
          Отменить
        </button>
        <button className="btn btn-pri btn-sm" type="button" onClick={onSave} disabled={!fabula.title.trim()}>
          Сохранить
        </button>
      </div>
    </div>
  );
}

function TopicFabulaMatrixView({
  topics,
  fabulas,
  matrix,
  onSave
}: {
  topics: Topic[];
  fabulas: Fabula[];
  matrix: TopicFabulaMatrixEntry[];
  onSave: (matrix: TopicFabulaMatrixEntry[]) => void;
}) {
  const [draft, setDraft] = useState(matrix);
  const isDirty = !sameMatrix(draft, matrix);

  useEffect(() => {
    setDraft(matrix);
  }, [matrix]);

  function toggle(topicId: string, fabulaId: string) {
    setDraft((current) =>
      current.map((entry) =>
        entry.topicId === topicId && entry.fabulaId === fabulaId ? { ...entry, enabled: !entry.enabled } : entry
      )
    );
  }

  return (
    <section className="card matrix-card">
      <div className="matrix-head">
        <div>
          <h3>Матрица совместимости</h3>
          <p>Связки определяют, какие фабулы допустимы для каждой темы. Изменения применяются только после сохранения.</p>
        </div>
        <div className="matrix-actions">
          {isDirty ? <span className="dirty-note">Есть несохраненные изменения</span> : null}
          <button className="btn btn-sec btn-sm" type="button" onClick={() => setDraft(matrix)} disabled={!isDirty}>
            Отменить
          </button>
          <button className="btn btn-pri btn-sm" type="button" onClick={() => onSave(draft)} disabled={!isDirty}>
            Сохранить матрицу
          </button>
        </div>
      </div>
      <div className="matrix-scroll" data-testid="topic-fabula-matrix-scroll">
        <table className="matrix-table">
          <thead>
            <tr>
              <th className="matrix-sticky matrix-topic-head" scope="col">Тема</th>
              {fabulas.map((fabula) => (
                <th className="matrix-fabula-head" key={fabula.id} scope="col">{fabula.title}</th>
              ))}
            </tr>
          </thead>
          <tbody>
            {topics.map((topic) => (
              <tr key={topic.id}>
                <th className="matrix-sticky matrix-topic-cell" scope="row">{topic.title}</th>
                {fabulas.map((fabula) => {
                  const entry = draft.find((item) => item.topicId === topic.id && item.fabulaId === fabula.id);
                  return (
                    <td className="matrix-toggle-cell" key={fabula.id}>
                      <label className="matrix-check">
                        <input
                          aria-label={`${topic.title} · ${fabula.title}`}
                          checked={Boolean(entry?.enabled)}
                          type="checkbox"
                          onChange={() => toggle(topic.id, fabula.id)}
                        />
                      </label>
                    </td>
                  );
                })}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </section>
  );
}

function EditorialValidationPanel({
  validationRun,
  currentRevision,
  activeTab,
  onRunValidation
}: {
  validationRun: EditorialValidationRun | null;
  currentRevision: number;
  activeTab: EditorialModelTab;
  onRunValidation: () => void;
}) {
  const validation = validationRun?.summary ?? null;
  const validatorResults = validationRun?.results ?? [];
  const aggregateStatus = validationRun?.aggregateStatus ?? validation?.status ?? null;
  const aggregateScore = validationRun?.aggregateScore ?? 0;
  const isStale = Boolean(validationRun && validationRun.revision !== currentRevision);
  const runState = !validationRun ? 'Еще не проверено' : isStale ? 'Требует повторной проверки' : 'Проверено';

  return (
    <aside className="card validation-panel">
      <div className="validation-head">
        <span className="mono-label">Проверка</span>
        <span className={`validation-run-state ${!validationRun ? 'empty' : isStale ? 'stale' : 'fresh'}`}>
          {runState}
        </span>
        {aggregateStatus ? <ValidationBadge status={aggregateStatus} /> : null}
        <h3>{validation?.title ?? 'Проверка еще не запускалась'}</h3>
        <p>
          {validation
            ? validation.summary
            : 'Заполните или отредактируйте правила, темы, фабулы и матрицу, затем запустите проверку вручную.'}
        </p>
        {isStale ? (
          <p className="validation-stale-note">
            После последней проверки были сохранены изменения. Запустите проверку повторно, чтобы получить актуальный вывод.
          </p>
        ) : null}
        <button className="btn btn-pri btn-sm" type="button" onClick={onRunValidation}>
          Проверить
        </button>
      </div>
      {validation ? (
        <div className="validator-summary">
          <div>
            <span className="mono-label">Score</span>
            <strong>{Math.round(aggregateScore * 100)}%</strong>
          </div>
          <div>
            <span className="mono-label">Validators</span>
            <strong>{validatorResults.length || validation.items.length}</strong>
          </div>
        </div>
      ) : null}
      {validatorResults.length > 0 ? (
        <div className="validation-items validator-cards">
          {validatorResults.map((result) => (
            <ValidatorCard key={result.id} result={result} />
          ))}
        </div>
      ) : validation ? (
        <div className="validation-items">
          {validation.items.map((item) => (
            <article className="validation-item" key={item.id}>
              <div>
                <ValidationBadge status={item.status} />
                <b>{item.title}</b>
              </div>
              <p>{item.summary}</p>
              <small>{item.recommendation}</small>
            </article>
          ))}
        </div>
      ) : null}
      <p className="validation-note">
        Вкладка: {editorialTabLabel(activeTab)}. Проверка deterministic, без AI provider. Результат обновляется только по кнопке.
      </p>
      {validationRun ? <p className="validation-note">Последняя проверка: {formatDateTime(validationRun.checkedAt)}</p> : null}
    </aside>
  );
}

function ValidatorCard({ result }: { result: ValidatorResult }) {
  return (
    <article className="validation-item validator-card">
      <div className="validator-card-head">
        <ValidationBadge status={result.status} />
        <div>
          <b>{validatorDefinitionTitle(result.validatorId)}</b>
          <span>{result.validatorId}</span>
        </div>
        <strong>{Math.round(result.score * 100)}%</strong>
      </div>
      <p>{result.summary}</p>
      <details className="validator-details">
        <summary>Evidence и рекомендации</summary>
        <div className="validator-detail-block">
          <span className="mono-label">Evidence</span>
          {result.evidence.length > 0 ? (
            result.evidence.map((item) => (
              <blockquote key={item.id}>
                <b>{item.title}</b>
                <p>{item.quote}</p>
                <small>{item.reason}</small>
              </blockquote>
            ))
          ) : (
            <p className="muted-text">Evidence пока нет.</p>
          )}
        </div>
        <div className="validator-detail-block">
          <span className="mono-label">Suggestions</span>
          {result.suggestions.length > 0 ? (
            result.suggestions.map((item) => (
              <div className={`validator-suggestion ${item.severity}`} key={item.id}>
                <b>{item.title}</b>
                <p>{item.description}</p>
              </div>
            ))
          ) : (
            <p className="muted-text">Рекомендаций нет.</p>
          )}
        </div>
      </details>
    </article>
  );
}

function WeightRangeEditor({ value, onChange }: { value: WeightRange; onChange: (value: WeightRange) => void }) {
  return (
    <div className="weight-editor">
      <label>
        Минимум, %
        <input
          min={0}
          max={100}
          type="number"
          value={value.min}
          onChange={(event) => onChange(normalizeWeightRange({ ...value, min: Number(event.target.value) }))}
        />
      </label>
      <label>
        Максимум, %
        <input
          min={0}
          max={100}
          type="number"
          value={value.max}
          onChange={(event) => onChange(normalizeWeightRange({ ...value, max: Number(event.target.value) }))}
        />
      </label>
    </div>
  );
}

function ValidationBadge({ status }: { status: 'green' | 'yellow' | 'red' }) {
  const label = status === 'green' ? 'ок' : status === 'yellow' ? 'внимание' : 'риск';
  return <span className={`validation-badge ${status}`}>{label}</span>;
}

function editorialRuleGroupLabel(group: EditorialRuleGroup): string {
  const labels: Record<EditorialRuleGroup, string> = {
    author: 'Образ автора',
    audience: 'Аудитория',
    positioning: 'Позиция',
    styleVoice: 'Голос',
    styleLanguage: 'Язык',
    styleRhythm: 'Ритм',
    antiAiPattern: 'Anti-AI',
    goal: 'Цель',
    forbiddenTopic: 'Запрет'
  };
  return labels[group];
}

function editorialTabLabel(tab: EditorialModelTab): string {
  if (tab === 'publisher') return 'Издательство';
  if (tab === 'topics') return 'Темы';
  if (tab === 'fabulas') return 'Фабулы';
  return 'Матрица';
}

function getReferencedTopicIds(workspace: WorkspaceState): Set<string> {
  return new Set(
    [workspace.insightCard?.topicId, workspace.contentPlanItem?.topicId, workspace.postBrief?.topicId].filter(
      Boolean
    ) as string[]
  );
}

function getReferencedFabulaIds(workspace: WorkspaceState): Set<string> {
  return new Set(
    [workspace.insightCard?.fabulaId, workspace.contentPlanItem?.fabulaId, workspace.postBrief?.fabulaId].filter(
      Boolean
    ) as string[]
  );
}

function countCompatibleFabulas(topicId: string, matrix: TopicFabulaMatrixEntry[]): number {
  return matrix.filter((entry) => entry.topicId === topicId && entry.enabled).length;
}

function countCompatibleTopics(fabulaId: string, matrix: TopicFabulaMatrixEntry[]): number {
  return matrix.filter((entry) => entry.fabulaId === fabulaId && entry.enabled).length;
}

function isMatrixEnabled(topicId: string, fabulaId: string, matrix: TopicFabulaMatrixEntry[]): boolean {
  return matrix.some((entry) => entry.topicId === topicId && entry.fabulaId === fabulaId && entry.enabled);
}

function sameMatrix(left: TopicFabulaMatrixEntry[], right: TopicFabulaMatrixEntry[]): boolean {
  if (left.length !== right.length) return false;
  return left.every((entry) => {
    const other = right.find((item) => item.topicId === entry.topicId && item.fabulaId === entry.fabulaId);
    return other ? other.enabled === entry.enabled : false;
  });
}

type SignalsTab = 'radars' | 'signals' | 'candidates';

function radarSourceTypeLabel(sourceType: RadarDefinition['sourceType']): string {
  if (sourceType === 'authorMemory') return 'Память';
  if (sourceType === 'archive') return 'Архив';
  if (sourceType === 'externalSource') return 'Внешний источник';
  return 'Ручной ввод';
}

function radarAcceptancePolicyLabel(policy: RadarDefinition['acceptancePolicy']): string {
  if (policy === 'automatic') return 'Автоматически';
  if (policy === 'automaticWithReview') return 'Авто + review';
  return 'Вручную';
}

function radarTriggerModeLabel(mode: RadarDefinition['triggerMode']): string {
  if (mode === 'scheduled') return 'По расписанию';
  if (mode === 'deficitDriven') return 'По дефициту плана';
  return 'Вручную';
}

function radarStatusLabel(status: RadarDefinition['status']): string {
  if (status === 'active') return 'Активен';
  if (status === 'paused') return 'Пауза';
  return 'Нужен review';
}

function signalReviewStatusLabel(status: SignalReviewStatus | undefined): string {
  if (status === 'approved') return 'Утвержден';
  if (status === 'rejected') return 'Отклонен';
  if (status === 'archived') return 'В архиве';
  if (status === 'corrected') return 'Исправлен';
  return 'Новый';
}

function SignalsView({
  workspace,
  onApproveSignal,
  onRejectSignal,
  onArchiveSignal,
  onCorrectSignal,
  onCreateInsight,
  onPlan
}: {
  workspace: WorkspaceState;
  onApproveSignal: (signal: SourceSignal) => void;
  onRejectSignal: (signal: SourceSignal) => void;
  onArchiveSignal: (signal: SourceSignal) => void;
  onCorrectSignal: (signal: SourceSignal, patch: Partial<SourceSignal>) => void;
  onCreateInsight: () => void;
  onPlan: () => void;
}) {
  const [tab, setTab] = useState<SignalsTab>('radars');
  const [expandedRadarId, setExpandedRadarId] = useState<string | null>(workspace.radars[0]?.id ?? null);
  const [expandedSignalId, setExpandedSignalId] = useState<string | null>(workspace.sourceSignal.id);
  const [editingSignal, setEditingSignal] = useState<SourceSignal | null>(null);
  const [radarFilter, setRadarFilter] = useState('all');
  const [statusFilter, setStatusFilter] = useState<SignalReviewStatus | 'all'>('all');
  const [topicFilter, setTopicFilter] = useState('all');
  const [fabulaFilter, setFabulaFilter] = useState('all');
  const [riskFilter, setRiskFilter] = useState<'all' | 'low' | 'medium' | 'high'>('all');
  const insight = workspace.insightCard;

  const filteredSignals = workspace.sourceSignals.filter((signal) => {
    if (radarFilter !== 'all' && signal.radarId !== radarFilter) return false;
    if (statusFilter !== 'all' && signal.reviewStatus !== statusFilter) return false;
    if (topicFilter !== 'all' && signal.suggestedTopicId !== topicFilter) return false;
    if (fabulaFilter !== 'all' && signal.suggestedFabulaId !== fabulaFilter) return false;
    if (riskFilter !== 'all' && signal.duplicateRisk !== riskFilter) return false;
    return true;
  });
  const approvedSignals = workspace.sourceSignals.filter((signal) => signal.reviewStatus === 'approved');

  function startSignalEdit(signal: SourceSignal) {
    setExpandedSignalId(signal.id);
    setEditingSignal({ ...signal });
  }

  function patchEditingSignal(patch: Partial<SourceSignal>) {
    if (!editingSignal) return;
    setEditingSignal({ ...editingSignal, ...patch });
  }

  function saveSignalEdit() {
    if (!editingSignal) return;
    onCorrectSignal(editingSignal, editingSignal);
    setExpandedSignalId(editingSignal.id);
    setEditingSignal(null);
  }

  return (
    <div className="page wide fade-up">
      <div className="sec-head">
        <h2>Сигналы</h2>
        <span className="sub">Радары собирают материал, автор утверждает сигналы, кандидаты появятся следующим слоем</span>
      </div>
      <div className="tabs signals-tabs" role="tablist" aria-label="Сигналы">
        <button className={`tab ${tab === 'radars' ? 'active' : ''}`} type="button" onClick={() => setTab('radars')}>
          Радары
        </button>
        <button className={`tab ${tab === 'signals' ? 'active' : ''}`} type="button" onClick={() => setTab('signals')}>
          Найденные сигналы
        </button>
        <button className={`tab ${tab === 'candidates' ? 'active' : ''}`} type="button" onClick={() => setTab('candidates')}>
          Кандидаты постов
        </button>
      </div>

      {tab === 'radars' ? (
        <section className="signals-stack" data-testid="radar-list">
          {workspace.radars.map((radar) => {
            const matchingSignals = workspace.sourceSignals.filter((signal) => signal.radarId === radar.id);
            const isExpanded = expandedRadarId === radar.id;
            return (
              <article className="card entity-row" key={radar.id}>
                <button className="entity-row-main" type="button" onClick={() => setExpandedRadarId(isExpanded ? null : radar.id)}>
                  <span className="pill">{radarSourceTypeLabel(radar.sourceType)}</span>
                  <strong>{radar.title}</strong>
                  <span>{radarAcceptancePolicyLabel(radar.acceptancePolicy)}</span>
                  <span>{matchingSignals.length} сигналов</span>
                  <span className={`sig ${radar.status === 'active' ? 'ok' : radar.status === 'paused' ? 'warn' : 'info'}`}>
                    {radarStatusLabel(radar.status)}
                  </span>
                </button>
                {isExpanded ? (
                  <div className="entity-details">
                    <p>{radar.scope}</p>
                    <dl className="signal-meta-grid">
                      <dt>Запуск</dt>
                      <dd>{radarTriggerModeLabel(radar.triggerMode)}</dd>
                      <dt>Последний run</dt>
                      <dd>{radar.lastRunAt}</dd>
                      <dt>Заметка</dt>
                      <dd>{radar.notes}</dd>
                    </dl>
                    <div className="actions">
                      <button className="btn btn-sec btn-sm" type="button" onClick={() => setTab('signals')}>
                        Открыть сигналы
                      </button>
                      <button className="btn btn-ghost btn-sm" type="button" disabled>
                        Проверить вручную
                      </button>
                    </div>
                  </div>
                ) : null}
              </article>
            );
          })}
        </section>
      ) : null}

      {tab === 'signals' ? (
        <section className="signals-layout">
          <div className="signals-main">
            <div className="card signal-filters">
              <select aria-label="Фильтр радара" value={radarFilter} onChange={(event) => setRadarFilter(event.target.value)}>
                <option value="all">Все радары</option>
                {workspace.radars.map((radar) => (
                  <option key={radar.id} value={radar.id}>
                    {radar.title}
                  </option>
                ))}
              </select>
              <select aria-label="Фильтр статуса сигнала" value={statusFilter} onChange={(event) => setStatusFilter(event.target.value as SignalReviewStatus | 'all')}>
                <option value="all">Все статусы</option>
                <option value="new">Новые</option>
                <option value="approved">Утвержденные</option>
                <option value="corrected">Исправленные</option>
                <option value="rejected">Отклоненные</option>
                <option value="archived">В архиве</option>
              </select>
              <select aria-label="Фильтр темы сигнала" value={topicFilter} onChange={(event) => setTopicFilter(event.target.value)}>
                <option value="all">Все темы</option>
                {workspace.topics.map((topic) => (
                  <option key={topic.id} value={topic.id}>
                    {topic.title}
                  </option>
                ))}
              </select>
              <select aria-label="Фильтр фабулы сигнала" value={fabulaFilter} onChange={(event) => setFabulaFilter(event.target.value)}>
                <option value="all">Все фабулы</option>
                {workspace.fabulas.map((fabula) => (
                  <option key={fabula.id} value={fabula.id}>
                    {fabula.title}
                  </option>
                ))}
              </select>
              <select aria-label="Фильтр риска дубля" value={riskFilter} onChange={(event) => setRiskFilter(event.target.value as 'all' | 'low' | 'medium' | 'high')}>
                <option value="all">Любой дубль-риск</option>
                <option value="low">Низкий</option>
                <option value="medium">Средний</option>
                <option value="high">Высокий</option>
              </select>
            </div>
            <div className="signals-stack" data-testid="source-signal-list">
              {filteredSignals.map((signal) => {
                const isExpanded = expandedSignalId === signal.id;
                const editing = editingSignal?.id === signal.id ? editingSignal : null;
                const radar = workspace.radars.find((candidate) => candidate.id === signal.radarId);
                const topic = workspace.topics.find((candidate) => candidate.id === signal.suggestedTopicId);
                const fabula = workspace.fabulas.find((candidate) => candidate.id === signal.suggestedFabulaId);
                return (
                  <article className="card entity-row signal-row" key={signal.id}>
                    <button className="entity-row-main" type="button" onClick={() => setExpandedSignalId(isExpanded ? null : signal.id)}>
                      <span className="pill">{radar?.title ?? 'Радар'}</span>
                      <strong>{signal.title}</strong>
                      <span>{topic?.title ?? 'Тема не выбрана'}</span>
                      <span>{fabula?.title ?? 'Фабула не выбрана'}</span>
                      <span className={`sig ${signal.reviewStatus === 'approved' ? 'ok' : signal.reviewStatus === 'rejected' ? 'danger' : 'info'}`}>
                        {signalReviewStatusLabel(signal.reviewStatus)}
                      </span>
                    </button>
                    {isExpanded ? (
                      <div className="entity-details">
                        {editing ? (
                          <div className="signal-edit-form">
                            <label>
                              Заголовок
                              <input value={editing.title} onChange={(event) => patchEditingSignal({ title: event.target.value })} />
                            </label>
                            <label>
                              Кратко
                              <textarea value={editing.summary} onChange={(event) => patchEditingSignal({ summary: event.target.value })} />
                            </label>
                            <div className="form-row">
                              <label>
                                Тема
                                <select value={editing.suggestedTopicId ?? ''} onChange={(event) => patchEditingSignal({ suggestedTopicId: event.target.value })}>
                                  {workspace.topics.map((topicOption) => (
                                    <option key={topicOption.id} value={topicOption.id}>
                                      {topicOption.title}
                                    </option>
                                  ))}
                                </select>
                              </label>
                              <label>
                                Фабула
                                <select value={editing.suggestedFabulaId ?? ''} onChange={(event) => patchEditingSignal({ suggestedFabulaId: event.target.value })}>
                                  {workspace.fabulas.map((fabulaOption) => (
                                    <option key={fabulaOption.id} value={fabulaOption.id}>
                                      {fabulaOption.title}
                                    </option>
                                  ))}
                                </select>
                              </label>
                            </div>
                            <label>
                              Ценность
                              <textarea value={editing.suggestedValue ?? ''} onChange={(event) => patchEditingSignal({ suggestedValue: event.target.value })} />
                            </label>
                            <label>
                              Правка автора
                              <textarea value={editing.authorCorrection ?? ''} onChange={(event) => patchEditingSignal({ authorCorrection: event.target.value })} />
                            </label>
                            <div className="actions">
                              <button className="btn btn-pri btn-sm" type="button" onClick={saveSignalEdit}>
                                Сохранить
                              </button>
                              <button className="btn btn-sec btn-sm" type="button" onClick={() => setEditingSignal(null)}>
                                Отменить
                              </button>
                            </div>
                          </div>
                        ) : (
                          <>
                            <p>{signal.summary}</p>
                            <dl className="signal-meta-grid">
                              <dt>Источник</dt>
                              <dd>{signal.source}</dd>
                              <dt>Дата</dt>
                              <dd>{signal.capturedAt}</dd>
                              <dt>Ценность</dt>
                              <dd>{signal.suggestedValue}</dd>
                              <dt>Риск дубля</dt>
                              <dd>{duplicateRiskLabel(signal.duplicateRisk ?? 'low')}</dd>
                              <dt>Заметка</dt>
                              <dd>{signal.rawNote}</dd>
                              {signal.authorCorrection ? (
                                <>
                                  <dt>Правка автора</dt>
                                  <dd>{signal.authorCorrection}</dd>
                                </>
                              ) : null}
                            </dl>
                            <div className="actions">
                              <button className="btn btn-pri btn-sm" type="button" onClick={() => onApproveSignal(signal)}>
                                Утвердить сигнал
                              </button>
                              <button className="btn btn-sec btn-sm" type="button" onClick={() => startSignalEdit(signal)}>
                                Редактировать
                              </button>
                              <button className="btn btn-ghost btn-sm" type="button" onClick={() => onArchiveSignal(signal)}>
                                В архив
                              </button>
                              <button className="btn btn-ghost btn-sm" type="button" onClick={() => onRejectSignal(signal)}>
                                Отклонить
                              </button>
                            </div>
                          </>
                        )}
                      </div>
                    ) : null}
                  </article>
                );
              })}
            </div>
          </div>
          <aside className="signals-aside card">
            <h3>Сигналы перед планом</h3>
            <p>Утвержденный сигнал становится текущим материалом для инсайта и сетки вещания.</p>
            <div className="memory-summary-grid">
              <div className="mini-stat"><b>{workspace.sourceSignals.length}</b><span>Всего</span></div>
              <div className="mini-stat"><b>{approvedSignals.length}</b><span>Утверждено</span></div>
              <div className="mini-stat"><b>{workspace.sourceSignals.filter((signal) => signal.reviewStatus === 'new').length}</b><span>Новые</span></div>
              <div className="mini-stat"><b>{workspace.sourceSignals.filter((signal) => signal.reviewStatus === 'corrected').length}</b><span>Правки</span></div>
            </div>
            <button className="btn btn-sec" type="button" onClick={onCreateInsight}>
              <Icon name="radar" size={16} />
              Собрать инсайт
            </button>
            {insight ? (
              <div className="signal-insight-summary">
                <span className="sig info">{workspace.sourceSignal.type}</span>
                <h4>{insight.title}</h4>
                <p>{insight.whyItMatters}</p>
                <button className="btn btn-pri btn-sm" type="button" onClick={onPlan}>
                  <Icon name="caret" size={14} />В план
                </button>
              </div>
            ) : null}
          </aside>
        </section>
      ) : null}

      {tab === 'candidates' ? (
        <section className="card empty-state">
          <span className="pill">Slice 1.6</span>
          <h3>Кандидаты постов появятся следующим слоем</h3>
          <p>
            Здесь будут сборки: сигнал, тема, фабула, аудитория, ценность и цель. Сейчас слайс
            фокусируется на радаре и ручном review сигналов, чтобы план не заполнялся без материала.
          </p>
        </section>
      ) : null}
    </div>
  );
}

function RadarView({
  workspace,
  onSignalChange,
  onCreateInsight,
  onPlan
}: {
  workspace: WorkspaceState;
  onSignalChange: (signal: SourceSignal) => void;
  onCreateInsight: () => void;
  onPlan: () => void;
}) {
  const insight = workspace.insightCard;

  return (
    <div className="page fade-up">
      <div className="sec-head">
        <h2>Поводы и инсайты</h2>
        <span className="sub">Один ручной сигнал для первого рабочего периметра</span>
      </div>
      <section className="card signal-editor">
        <div className="form-row">
          <label>
            Тип сигнала
            <input
              value={workspace.sourceSignal.type}
              onChange={(event) => onSignalChange({ ...workspace.sourceSignal, type: event.target.value })}
            />
          </label>
          <label>
            Источник
            <input
              value={workspace.sourceSignal.source}
              onChange={(event) => onSignalChange({ ...workspace.sourceSignal, source: event.target.value })}
            />
          </label>
        </div>
        <label>
          Заголовок сигнала
          <input
            value={workspace.sourceSignal.title}
            onChange={(event) => onSignalChange({ ...workspace.sourceSignal, title: event.target.value })}
          />
        </label>
        <label>
          Краткое содержание
          <textarea
            value={workspace.sourceSignal.summary}
            onChange={(event) => onSignalChange({ ...workspace.sourceSignal, summary: event.target.value })}
          />
        </label>
        <label>
          Заметка автора
          <textarea
            value={workspace.sourceSignal.rawNote}
            onChange={(event) => onSignalChange({ ...workspace.sourceSignal, rawNote: event.target.value })}
          />
        </label>
        <button className="btn btn-sec" type="button" onClick={onCreateInsight}>
          <Icon name="radar" size={16} />
          Собрать инсайт
        </button>
      </section>
      {insight ? (
        <section className="card hover insight">
          <div className="top">
            <span className="sig info">{workspace.sourceSignal.type}</span>
            <span className="rub">{insight.rubric}</span>
            <span className="urgent">Риск банальности {formatScore(insight.banalityRisk)}</span>
          </div>
          <h3>{insight.title}</h3>
          <p className="why">{insight.whyItMatters}</p>
          <div className="foot">
            <span className="sc">
              релевантность <b>{formatScore(insight.score)}</b>
            </span>
            <span className="sc">
              срочность <b>{insight.urgency}</b>
            </span>
            <div className="actions">
              <button className="btn btn-pri btn-sm" type="button" onClick={onPlan}>
                <Icon name="caret" size={14} />В план
              </button>
            </div>
          </div>
        </section>
      ) : null}
    </div>
  );
}

function PlanView({
  workspace,
  onGenerate,
  onItemChange,
  onApprove,
  onBrief
}: {
  workspace: WorkspaceState;
  onGenerate: () => void;
  onItemChange: (item: ContentPlanItem) => void;
  onApprove: (itemId: string) => void;
  onBrief: (item: ContentPlanItem) => void;
}) {
  const [expandedId, setExpandedId] = useState<string | null>(workspace.contentPlanItems[0]?.id ?? null);
  const [editingItem, setEditingItem] = useState<ContentPlanItem | null>(null);
  const items = workspace.contentPlanItems;
  const warnings = useMemo(
    () => detectBroadcastPlanConflicts(workspace, items),
    [workspace, items]
  );
  const activeWarnings = warnings.filter((warning) => warning.severity !== 'green');
  const topicDistribution = getPlanDistribution(items, 'topicTitle');
  const fabulaDistribution = getPlanDistribution(items, 'fabulaTitle');

  function startEdit(item: ContentPlanItem) {
    setExpandedId(item.id);
    setEditingItem({ ...item });
  }

  function saveEdit() {
    if (!editingItem) return;
    onItemChange({ ...editingItem, manualOverride: true });
    setExpandedId(editingItem.id);
    setEditingItem(null);
  }

  function updateEditingItem(patch: Partial<ContentPlanItem>) {
    setEditingItem((current) => (current ? { ...current, ...patch } : current));
  }

  function updateEditingTopic(topicId: string) {
    const topic = workspace.topics.find((item) => item.id === topicId);
    updateEditingItem({ topicId, topicTitle: topic?.title ?? '' });
  }

  function updateEditingFabula(fabulaId: string) {
    const fabula = workspace.fabulas.find((item) => item.id === fabulaId);
    updateEditingItem({ fabulaId, fabulaTitle: fabula?.title ?? '' });
  }

  return (
    <div className="page wide fade-up">
      <div className="broadcast-layout">
        <section className="broadcast-main">
          <HitlGate
            tag="HITL · Gate 1 — Сетка вещания"
            title="Соберите и утвердите слоты контент-плана"
            subtitle="Сетка распределяет темы и фабулы по датам, форматам и площадкам. Ручные правки важнее весов, но конфликты подсвечиваются."
            action={items.length > 0 ? 'Пересобрать сетку' : 'Собрать сетку'}
            onAction={onGenerate}
          />
          {items.length > 0 ? (
            <div className="broadcast-list" data-testid="broadcast-grid">
              <div className="broadcast-toolbar">
                <div>
                  <h2>Сетка на {workspace.contentPlanSettings.planningHorizonDays} дней</h2>
                  <p>{workspace.contentPlanSettings.postsPerWeek} поста в неделю · {items.length} слотов</p>
                </div>
                <span className={`validation-run-state ${activeWarnings.length > 0 ? 'stale' : 'fresh'}`}>
                  {activeWarnings.length > 0 ? `${activeWarnings.length} предупрежд.` : 'OK'}
                </span>
              </div>
              {items.map((item) => {
                const isExpanded = expandedId === item.id;
                const isEditing = editingItem?.id === item.id;
                const itemWarnings = warnings.filter((warning) =>
                  warning.targetType === 'slot' && warning.targetId === item.id
                );
                const current = isEditing ? editingItem : item;

                return (
                  <article className={`card broadcast-row${isExpanded ? ' expanded' : ''}`} key={item.id}>
                    <button
                      className="broadcast-row-main"
                      type="button"
                      onClick={() => setExpandedId(isExpanded ? null : item.id)}
                    >
                      <span className="broadcast-date">{formatPlanDate(item.date)}</span>
                      <span className="broadcast-title">{item.title}</span>
                      <span className="broadcast-meta">{item.platform}</span>
                      <span className="broadcast-meta">{item.format}</span>
                      <span className="broadcast-meta">{item.topicTitle}</span>
                      <span className="broadcast-meta">{item.fabulaTitle}</span>
                      <span className={`pill ${item.approvalStatus === 'approved' ? 'ok' : 'pin'}`}>
                        <i />
                        {statusLabel(item.approvalStatus)}
                      </span>
                      {itemWarnings.length > 0 ? <span className="validation-badge yellow">warning</span> : null}
                    </button>
                    {isExpanded ? (
                      <div className="broadcast-details">
                        {isEditing && current ? (
                          <div className="broadcast-edit-grid">
                            <label>
                              Заголовок
                              <input
                                value={current.title}
                                onChange={(event) => updateEditingItem({ title: event.target.value })}
                              />
                            </label>
                            <label>
                              Дата
                              <input
                                type="date"
                                value={current.date}
                                onChange={(event) => updateEditingItem({ date: event.target.value })}
                              />
                            </label>
                            <label>
                              Площадка
                              <input
                                value={current.platform}
                                onChange={(event) => updateEditingItem({ platform: event.target.value })}
                              />
                            </label>
                            <label>
                              Формат
                              <select
                                value={current.format}
                                onChange={(event) => updateEditingItem({ format: event.target.value })}
                              >
                                {workspace.contentPlanSettings.allowedFormats.map((format) => (
                                  <option value={format} key={format}>{format}</option>
                                ))}
                              </select>
                            </label>
                            <label>
                              Тема
                              <select value={current.topicId ?? ''} onChange={(event) => updateEditingTopic(event.target.value)}>
                                {workspace.topics.map((topic) => (
                                  <option value={topic.id} key={topic.id}>{topic.title}</option>
                                ))}
                              </select>
                            </label>
                            <label>
                              Фабула
                              <select value={current.fabulaId ?? ''} onChange={(event) => updateEditingFabula(event.target.value)}>
                                {workspace.fabulas.map((fabula) => (
                                  <option value={fabula.id} key={fabula.id}>{fabula.title}</option>
                                ))}
                              </select>
                            </label>
                            <label>
                              Приоритет
                              <input
                                value={current.priority}
                                onChange={(event) => updateEditingItem({ priority: event.target.value })}
                              />
                            </label>
                            <label className="broadcast-edit-wide">
                              Ожидаемый эффект
                              <textarea
                                value={current.expectedEffect}
                                onChange={(event) => updateEditingItem({ expectedEffect: event.target.value })}
                              />
                            </label>
                            <div className="entity-actions broadcast-edit-actions">
                              <button className="btn btn-pri" type="button" onClick={saveEdit}>
                                Сохранить
                              </button>
                              <button className="btn btn-sec" type="button" onClick={() => setEditingItem(null)}>
                                Отменить
                              </button>
                            </div>
                          </div>
                        ) : (
                          <>
                            <dl className="entity-detail-list">
                              <div>
                                <dt>Ожидаемый эффект</dt>
                                <dd>{item.expectedEffect}</dd>
                              </div>
                              <div>
                                <dt>Связка</dt>
                                <dd>{item.topicTitle} · {item.fabulaTitle}</dd>
                              </div>
                              <div>
                                <dt>Источник</dt>
                                <dd>{item.sourceSignalId ?? item.insightId}</dd>
                              </div>
                              <div>
                                <dt>Режим</dt>
                                <dd>{item.manualOverride ? 'Ручная правка сетки' : 'Собрано deterministic-сервисом'}</dd>
                              </div>
                            </dl>
                            {itemWarnings.length > 0 ? (
                              <div className="matrix-warnings">
                                {itemWarnings.map((warning) => <p key={warning.id}>{warning.message}</p>)}
                              </div>
                            ) : null}
                            <div className="entity-actions">
                              <button className="btn btn-sec" type="button" onClick={() => startEdit(item)}>
                                Редактировать
                              </button>
                              <button
                                className="btn btn-sec"
                                type="button"
                                disabled={item.approvalStatus === 'approved'}
                                onClick={() => onApprove(item.id)}
                              >
                                Утвердить
                              </button>
                              <button
                                className="btn btn-pri"
                                type="button"
                                disabled={item.approvalStatus !== 'approved'}
                                onClick={() => onBrief(item)}
                              >
                                <Icon name="brief" size={16} />
                                Подготовить фабулу поста
                              </button>
                            </div>
                          </>
                        )}
                      </div>
                    ) : null}
                  </article>
                );
              })}
            </div>
          ) : (
            <EmptyState text="Соберите сетку вещания из текущего радара, тем и фабул редакционной модели." />
          )}
        </section>
        <aside className="aside broadcast-aside">
          <div className="panel validation-panel">
            <div className="validation-head">
              <h3>Сетка вещания</h3>
              <span className={`validation-run-state ${activeWarnings.length > 0 ? 'stale' : 'fresh'}`}>
                {activeWarnings.length > 0 ? 'Есть конфликты' : 'Баланс OK'}
              </span>
              <p>Ручные правки слотов сохраняются, даже если выходят за declared weights. Конфликт нужен как сигнал редактору.</p>
            </div>
            <div className="validator-summary">
              <div><strong>{items.length}</strong><span>слотов</span></div>
              <div><strong>{workspace.contentPlanSettings.postsPerWeek}</strong><span>в неделю</span></div>
              <div><strong>{topicDistribution.length}</strong><span>тем</span></div>
              <div><strong>{fabulaDistribution.length}</strong><span>фабул</span></div>
            </div>
            <DistributionList title="Темы" items={topicDistribution} />
            <DistributionList title="Фабулы" items={fabulaDistribution} />
            {activeWarnings.length > 0 ? (
              <div className="validation-warnings">
                {activeWarnings.slice(0, 6).map((warning) => <p key={warning.id}>{warning.message}</p>)}
              </div>
            ) : null}
          </div>
        </aside>
      </div>
    </div>
  );
}

function DistributionList({ title, items }: { title: string; items: Array<{ title: string; count: number; share: number }> }) {
  return (
    <div className="plan-distribution">
      <h4>{title}</h4>
      {items.length > 0 ? (
        items.map((item) => (
          <div className="plan-distribution-row" key={item.title}>
            <span>{item.title}</span>
            <b>{Math.round(item.share)}%</b>
          </div>
        ))
      ) : (
        <p className="panel-note">Нет слотов для расчета.</p>
      )}
    </div>
  );
}

function getPlanDistribution(
  items: ContentPlanItem[],
  field: 'topicTitle' | 'fabulaTitle'
): Array<{ title: string; count: number; share: number }> {
  const total = Math.max(items.length, 1);
  const counts = new Map<string, number>();
  items.forEach((item) => {
    const title = item[field] ?? 'Не задано';
    counts.set(title, (counts.get(title) ?? 0) + 1);
  });

  return Array.from(counts.entries()).map(([title, count]) => ({
    title,
    count,
    share: (count / total) * 100
  }));
}

function formatPlanDate(date: string): string {
  if (!date) return 'Без даты';
  const parsed = new Date(`${date}T00:00:00`);
  if (Number.isNaN(parsed.getTime())) return date;
  return parsed.toLocaleDateString('ru-RU', { day: '2-digit', month: 'short' });
}

function BriefView({
  workspace,
  onBriefChange,
  onBackToPlan,
  onApprove
}: {
  workspace: WorkspaceState;
  onBriefChange: (brief: PostBrief) => void;
  onBackToPlan: () => void;
  onApprove: () => void;
}) {
  const brief = workspace.postBrief;

  if (!brief) {
    return (
      <div className="page fade-up">
        <button className="btn btn-sec" type="button" onClick={onBackToPlan}>
          Вернуться в план
        </button>
        <EmptyState text="Сначала подготовьте фабулу из утвержденного элемента плана." />
      </div>
    );
  }

  return (
    <div className="page wide fade-up">
      <HitlGate
        tag="HITL · Gate 2 — Замысел"
        title="Утвердите фабулу перед написанием"
        subtitle="Слабые тексты обычно проваливаются на замысле. Решение остается за главным редактором."
        action="Утвердить фабулу"
        onAction={onApprove}
      />
      <div className="inline-actions">
        <button className="btn btn-sec" type="button" onClick={onBackToPlan}>
          Вернуться в план
        </button>
      </div>
      <div className="brief-grid">
        <section className="brief-body">
          <span className="rub">{brief.rubric}</span>
          <FieldInput label="Заголовок" value={brief.title} onChange={(title) => onBriefChange({ ...brief, title })} />
          <FieldInput
            label="Главный тезис"
            value={brief.thesis}
            onChange={(thesis) => onBriefChange({ ...brief, thesis })}
            serif
          />
          <FieldInput
            label="Конфликт"
            value={brief.conflict}
            onChange={(conflict) => onBriefChange({ ...brief, conflict })}
          />
          <FieldInput
            label="Авторская позиция"
            value={brief.authorPosition}
            onChange={(authorPosition) => onBriefChange({ ...brief, authorPosition })}
          />
          <FieldList label="Доказательства" items={brief.evidence} onChange={(evidence) => onBriefChange({ ...brief, evidence })} />
          <FieldList label="Структура" items={brief.structure} onChange={(structure) => onBriefChange({ ...brief, structure })} />
          <FieldInput label="CTA" value={brief.cta} onChange={(cta) => onBriefChange({ ...brief, cta })} />
          <FieldList label="Риски" items={brief.risks} onChange={(risks) => onBriefChange({ ...brief, risks })} />
        </section>
        <aside className="aside">
          <div className="panel">
            <h4>Статус</h4>
            <span className={`pill ${brief.approvalStatus === 'approved' ? 'ok' : 'pin'}`}>
              <i />
              {statusLabel(brief.approvalStatus)}
            </span>
          </div>
          <div className="panel">
            <h4>Источники</h4>
            <ul className="bullets">
              {brief.sources.map((source) => (
                <li key={source}>{source}</li>
              ))}
            </ul>
          </div>
        </aside>
      </div>
    </div>
  );
}

function EditView({
  workspace,
  onGoBrief,
  onCreateDraft,
  onDraftChange,
  onApproveFinal
}: {
  workspace: WorkspaceState;
  onGoBrief: () => void;
  onCreateDraft: () => void;
  onDraftChange: (body: string) => void;
  onApproveFinal: () => void;
}) {
  const [tab, setTab] = useState<'brief' | 'draft' | 'final'>(() => (workspace.finalText ? 'final' : 'draft'));
  const brief = workspace.postBrief;
  const draft = workspace.postDraft;
  const finalText = workspace.finalText;

  if (!brief || brief.approvalStatus !== 'approved') {
    return (
      <div className="page fade-up">
        <section className="card edit-empty">
          <div className="placeholder-icon">
            <Icon name="brief" size={28} />
          </div>
          <h2>Сначала утвердите фабулу</h2>
          <p>Редактура открывается только после Gate 2: утвержденной фабулы поста.</p>
          <button className="btn btn-pri" type="button" onClick={onGoBrief}>
            <Icon name="brief" size={16} />
            Перейти к фабуле
          </button>
        </section>
      </div>
    );
  }

  return (
    <div className="page wide fade-up">
      <HitlGate
        tag="HITL · Gate 3 — Финальный текст"
        title="Проверьте драфт и утвердите финальную версию"
        subtitle="Warnings не блокируют утверждение: человек остается главным редактором и видит риски перед решением."
        action="Утвердить текст"
        disabled={!draft}
        onAction={onApproveFinal}
      />
      <div className="tabs" role="tablist" aria-label="Редакторские вкладки">
        <button className={`tab${tab === 'brief' ? ' active' : ''}`} type="button" onClick={() => setTab('brief')}>
          Фабула
        </button>
        <button className={`tab${tab === 'draft' ? ' active' : ''}`} type="button" onClick={() => setTab('draft')}>
          Драфт
        </button>
        <button className={`tab${tab === 'final' ? ' active' : ''}`} type="button" onClick={() => setTab('final')}>
          Финал
        </button>
      </div>

      {!draft ? (
        <section className="card draft-start">
          <span className="rub">{brief.rubric}</span>
          <h2>{brief.title}</h2>
          <p>{brief.thesis}</p>
          <button className="btn btn-pri" type="button" onClick={onCreateDraft}>
            <Icon name="edit" size={16} />
            Написать драфт
          </button>
        </section>
      ) : (
        <div className="edit-grid">
          <section className="doc">
            {tab === 'brief' && <BriefSnapshot brief={brief} />}
            {tab === 'draft' && (
              <>
                <div className="doc-head">
                  <div>
                    <span className="rub">Версия {draft.version}</span>
                    <h2>{draft.title}</h2>
                  </div>
                  <span className={`pill ${draft.status === 'revised' ? 'pin' : 'ok'}`}>
                    <i />
                    {draft.status === 'revised' ? 'Отредактирован' : 'Драфт'}
                  </span>
                </div>
                <label className="draft-editor">
                  <span className="k">Текст</span>
                  <textarea
                    aria-label="Текст драфта"
                    value={draft.body}
                    onChange={(event) => onDraftChange(event.target.value)}
                  />
                </label>
              </>
            )}
            {tab === 'final' && <FinalTextView finalText={finalText} draft={draft} />}
          </section>
          <aside className="edit-side">
            <section className="panel">
              <h4>Проверки</h4>
              <div className="checks">
                {workspace.editorialChecks.map((check) => (
                  <CheckCard key={check.id} check={check} />
                ))}
              </div>
            </section>
            <section className="panel">
              <h4>Заметки редакторов</h4>
              <div className="notes">
                {workspace.editorNotes.map((note) => (
                  <article className="note" key={note.id}>
                    <div className="note-head">
                      <span className="av">{note.agent.slice(0, 2)}</span>
                      <div>
                        <b>{note.agent}</b>
                        <span>{note.tone} · {note.target}</span>
                      </div>
                    </div>
                    <p>{note.text}</p>
                  </article>
                ))}
              </div>
            </section>
          </aside>
        </div>
      )}
    </div>
  );
}

function BriefSnapshot({ brief }: { brief: PostBrief }) {
  return (
    <div className="brief-snapshot">
      <span className="rub">{brief.rubric}</span>
      <h2>{brief.title}</h2>
      <p className="lead">{brief.thesis}</p>
      <div className="snapshot-grid">
        <InfoBlock title="Конфликт" items={[brief.conflict]} />
        <InfoBlock title="Позиция" items={[brief.authorPosition]} />
        <InfoBlock title="Доказательства" items={brief.evidence} />
        <InfoBlock title="Риски" items={brief.risks} />
      </div>
    </div>
  );
}

function FinalTextView({ finalText, draft }: { finalText: FinalText | null; draft: PostDraft }) {
  if (!finalText) {
    return (
      <div className="final-empty">
        <h2>Финал еще не утвержден</h2>
        <p>Проверьте драфт, замечания редакторов и нажмите «Утвердить текст».</p>
      </div>
    );
  }

  return (
    <article className="final-doc">
      <div className="final-status">
        <span className="pill ok">
          <i />
          Финальный текст утвержден
        </span>
        <span>на основе версии {draft.version}</span>
      </div>
      <h2>{finalText.title}</h2>
      <pre>{finalText.body}</pre>
    </article>
  );
}

function InfoBlock({ title, items }: { title: string; items: string[] }) {
  return (
    <div className="info-block">
      <h4>{title}</h4>
      <ul className="bullets">
        {items.map((item) => (
          <li key={item}>{item}</li>
        ))}
      </ul>
    </div>
  );
}

function CheckCard({ check }: { check: EditorialCheck }) {
  return (
    <article className={`check check-${check.status}`}>
      <div className="check-head">
        <span className="ci">{check.title.slice(0, 1)}</span>
        <div>
          <b>{check.title}</b>
          <span>{checkStatusLabel(check.status)}</span>
        </div>
      </div>
      <p>{check.summary}</p>
      <ul className="bullets">
        {check.findings.map((finding) => (
          <li key={finding}>{finding}</li>
        ))}
      </ul>
    </article>
  );
}

function ReleaseView({
  workspace,
  onGoEdit,
  onCreatePackage,
  onToggleChecklist,
  onMarkReady,
  onCopy,
  onDownload
}: {
  workspace: WorkspaceState;
  onGoEdit: () => void;
  onCreatePackage: () => void;
  onToggleChecklist: (itemId: string) => void;
  onMarkReady: () => void;
  onCopy: () => void;
  onDownload: () => void;
}) {
  const finalText = workspace.finalText;
  const releasePackage = workspace.releasePackage;
  const allChecklistDone = releasePackage?.checklist.every((item) => item.done) ?? false;

  if (!finalText || finalText.approvalStatus !== 'approved') {
    return (
      <div className="page fade-up">
        <section className="card edit-empty">
          <div className="placeholder-icon">
            <Icon name="edit" size={28} />
          </div>
          <h2>Сначала утвердите финальный текст</h2>
          <p>Выпуск открывается после Gate 3: утвержденного текста в разделе «Редактура».</p>
          <button className="btn btn-pri" type="button" onClick={onGoEdit}>
            <Icon name="edit" size={16} />
            Перейти в редактуру
          </button>
        </section>
      </div>
    );
  }

  if (!releasePackage) {
    return (
      <div className="page wide fade-up">
        <section className="card draft-start">
          <span className="rub">Manual export</span>
          <h2>{finalText.title}</h2>
          <p>Финальный текст утвержден. Подготовьте пакет выпуска для Telegram и LinkedIn без автопостинга.</p>
          <button className="btn btn-pri" type="button" onClick={onCreatePackage}>
            <Icon name="release" size={16} />
            Подготовить выпуск
          </button>
        </section>
      </div>
    );
  }

  return (
    <div className="page wide fade-up">
      <HitlGate
        tag="Release · Manual export"
        title={`Статус: ${releaseStatusLabel(releasePackage.status)}`}
        subtitle="Пакет выпуска не публикует пост автоматически. Он готовит текст, markdown и чеклист для ручной публикации."
        action="Готово к выпуску"
        disabled={!allChecklistDone}
        onAction={onMarkReady}
      />
      <div className="release-grid">
        <section className="release-doc">
          <div className="doc-head">
            <div>
              <span className="rub">Финальный текст</span>
              <h2>{finalText.title}</h2>
            </div>
            <span className={`pill ${releasePackage.status === 'exported' ? 'ok' : 'pin'}`}>
              <i />
              {releaseStatusLabel(releasePackage.status)}
            </span>
          </div>
          <pre className="release-text">{finalText.body}</pre>
          <div className="markdown-preview">
            <div className="doc-head">
              <h3>Markdown export</h3>
              <div className="actions">
                <button className="btn btn-sec btn-sm" type="button" onClick={onCopy}>
                  <Icon name="check" size={14} />
                  Скопировать текст
                </button>
                <button className="btn btn-pri btn-sm" type="button" onClick={onDownload}>
                  <Icon name="release" size={14} />
                  Скачать Markdown
                </button>
              </div>
            </div>
            <pre>{releasePackage.markdown}</pre>
          </div>
        </section>
        <aside className="edit-side">
          <section className="panel">
            <h4>Площадки</h4>
            <div className="target-list">
              {releasePackage.targets.map((target) => (
                <span className="sig info" key={target}>
                  {targetLabel(target)}
                </span>
              ))}
            </div>
          </section>
          <section className="panel">
            <h4>Release checklist</h4>
            <div className="release-checklist">
              {releasePackage.checklist.map((item) => (
                <label className="check-row" key={item.id}>
                  <input
                    type="checkbox"
                    checked={item.done}
                    onChange={() => onToggleChecklist(item.id)}
                  />
                  <span>{item.label}</span>
                </label>
              ))}
            </div>
          </section>
          <section className="panel">
            <h4>Метаданные</h4>
            <dl className="meta-list">
              <dt>Обновлено</dt>
              <dd>{releasePackage.updatedAt}</dd>
              <dt>Статус</dt>
              <dd>{releaseStatusLabel(releasePackage.status)}</dd>
              <dt>Тип выпуска</dt>
              <dd>ручной export</dd>
            </dl>
          </section>
        </aside>
      </div>
    </div>
  );
}

function AnalyticsView({
  workspace,
  onGoRelease,
  onCreateNote,
  onChangeNote,
  onCapture
}: {
  workspace: WorkspaceState;
  onGoRelease: () => void;
  onCreateNote: () => void;
  onChangeNote: (note: EditorialLearningNote) => void;
  onCapture: () => void;
}) {
  const releasePackage = workspace.releasePackage;
  const note = workspace.editorialLearningNote;

  if (!releasePackage || releasePackage.status !== 'exported') {
    return (
      <div className="page fade-up">
        <section className="card edit-empty">
          <div className="placeholder-icon">
            <Icon name="release" size={28} />
          </div>
          <h2>Сначала завершите ручной выпуск</h2>
          <p>Аналитика открывается после статуса «Экспортировано вручную» в разделе «Выпуск».</p>
          <button className="btn btn-pri" type="button" onClick={onGoRelease}>
            <Icon name="release" size={16} />
            Перейти в выпуск
          </button>
        </section>
      </div>
    );
  }

  if (!note) {
    return (
      <div className="page wide fade-up">
        <section className="card draft-start">
          <span className="rub">Analytics prep</span>
          <h2>Подготовить редакционные выводы</h2>
          <p>
            Метрики вводятся вручную. Этот слой фиксирует не просмотры ради просмотров,
            а выводы для следующего редакционного цикла.
          </p>
          <button className="btn btn-pri" type="button" onClick={onCreateNote}>
            <Icon name="analytics" size={16} />
            Подготовить аналитику
          </button>
        </section>
      </div>
    );
  }

  const currentNote = note;

  function patchNote(patch: Partial<EditorialLearningNote>) {
    onChangeNote(updateLearningNote(currentNote, patch));
  }

  function patchMetric(metric: keyof ManualMetricSnapshot, value: string) {
    patchNote({
      metricSnapshot: {
        ...currentNote.metricSnapshot,
        [metric]: Number(value) || 0
      }
    });
  }

  return (
    <div className="page wide fade-up">
      <HitlGate
        tag="Analytics · Learning"
        title={`Статус: ${analyticsStatusLabel(note.status)}`}
        subtitle="Площадочные API не подключены: редакция вручную заносит метрики и фиксирует выводы."
        action="Зафиксировать выводы"
        onAction={onCapture}
      />
      <div className="analytics-grid">
        <section className="analytics-doc">
          <div className="doc-head">
            <div>
              <span className="rub">Ручные метрики</span>
              <h2>Редакционный разбор выпуска</h2>
            </div>
            <span className={`pill ${note.status === 'captured' ? 'ok' : 'pin'}`}>
              <i />
              {analyticsStatusLabel(note.status)}
            </span>
          </div>
          <div className="metric-grid">
            <MetricInput label="Просмотры" value={note.metricSnapshot.views} onChange={(value) => patchMetric('views', value)} />
            <MetricInput label="Реакции" value={note.metricSnapshot.reactions} onChange={(value) => patchMetric('reactions', value)} />
            <MetricInput label="Комментарии" value={note.metricSnapshot.comments} onChange={(value) => patchMetric('comments', value)} />
            <MetricInput label="Сохранения" value={note.metricSnapshot.saves} onChange={(value) => patchMetric('saves', value)} />
            <MetricInput label="Лиды" value={note.metricSnapshot.leads} onChange={(value) => patchMetric('leads', value)} />
          </div>
          <div className="learning-fields">
            <LearningTextArea label="Что сработало" value={note.observedResult} onChange={(observedResult) => patchNote({ observedResult })} />
            <LearningTextArea label="Реакция аудитории" value={note.audienceReaction} onChange={(audienceReaction) => patchNote({ audienceReaction })} />
            <LearningTextArea label="Какие тезисы работают" value={note.workingTheses} onChange={(workingTheses) => patchNote({ workingTheses })} />
            <LearningTextArea label="Какие рубрики усиливают доверие" value={note.trustRubrics} onChange={(trustRubrics) => patchNote({ trustRubrics })} />
            <LearningTextArea label="Какие темы приводят качественную аудиторию" value={note.qualityAudienceTopics} onChange={(qualityAudienceTopics) => patchNote({ qualityAudienceTopics })} />
            <LearningTextArea label="Где автор звучит сильнее" value={note.strongerVoice} onChange={(strongerVoice) => patchNote({ strongerVoice })} />
            <LearningTextArea label="Какие форматы стоит повторить" value={note.repeatFormats} onChange={(repeatFormats) => patchNote({ repeatFormats })} />
            <LearningTextArea label="Что развить в серию" value={note.seriesCandidates} onChange={(seriesCandidates) => patchNote({ seriesCandidates })} />
          </div>
        </section>
        <aside className="edit-side">
          <section className="panel">
            <h4>Контекст выпуска</h4>
            <dl className="meta-list">
              <dt>Release</dt>
              <dd>{note.releasePackageId}</dd>
              <dt>Статус</dt>
              <dd>{releaseStatusLabel(releasePackage.status)}</dd>
              <dt>Площадки</dt>
              <dd>{releasePackage.targets.map(targetLabel).join(' + ')}</dd>
            </dl>
          </section>
          <section className="panel">
            <h4>Learning note</h4>
            <span className={`pill ${note.status === 'captured' ? 'ok' : 'pin'}`}>
              <i />
              {analyticsStatusLabel(note.status)}
            </span>
            <dl className="meta-list analytics-meta">
              <dt>Обновлено</dt>
              <dd>{note.updatedAt}</dd>
              <dt>Зафиксировано</dt>
              <dd>{note.capturedAt ?? 'еще нет'}</dd>
            </dl>
          </section>
        </aside>
      </div>
    </div>
  );
}

function MetricInput({
  label,
  value,
  onChange
}: {
  label: string;
  value: number;
  onChange: (value: string) => void;
}) {
  return (
    <label className="metric-input">
      <span>{label}</span>
      <input type="number" min="0" value={value} onChange={(event) => onChange(event.target.value)} />
    </label>
  );
}

function LearningTextArea({
  label,
  value,
  onChange
}: {
  label: string;
  value: string;
  onChange: (value: string) => void;
}) {
  return (
    <label className="learning-field">
      <span>{label}</span>
      <textarea value={value} onChange={(event) => onChange(event.target.value)} />
    </label>
  );
}

function HitlGate({
  tag,
  title,
  subtitle,
  action,
  disabled,
  onAction
}: {
  tag: string;
  title: string;
  subtitle: string;
  action: string;
  disabled?: boolean;
  onAction: () => void;
}) {
  return (
    <section className="gate">
      <div className="gm">
        <Icon name="caret" size={24} />
      </div>
      <div>
        <div className="gtag">{tag}</div>
        <div className="gttl">{title}</div>
        <div className="gsub">{subtitle}</div>
      </div>
      <div className="gbtns">
        <button className="btn btn-pri" type="button" disabled={disabled} onClick={onAction}>
          <Icon name="check" size={16} />
          {action}
        </button>
      </div>
    </section>
  );
}

function FieldInput({
  label,
  value,
  onChange,
  serif
}: {
  label: string;
  value: string;
  onChange: (value: string) => void;
  serif?: boolean;
}) {
  return (
    <label className="field-row">
      <span className="k">{label}</span>
      <textarea className={serif ? 'serif' : ''} value={value} onChange={(event) => onChange(event.target.value)} />
    </label>
  );
}

function FieldList({
  label,
  items,
  onChange
}: {
  label: string;
  items: string[];
  onChange: (items: string[]) => void;
}) {
  return <FieldInput label={label} value={items.join('\n')} onChange={(value) => onChange(splitLines(value))} />;
}

function Placeholder({ icon, title, text }: { icon: string; title: string; text: string }) {
  return (
    <div className="page fade-up placeholder">
      <div className="placeholder-icon">
        <Icon name={icon} size={30} />
      </div>
      <h2>{title}</h2>
      <p>{text}</p>
    </div>
  );
}

function EmptyState({ text }: { text: string }) {
  return <div className="card empty-state">{text}</div>;
}

function splitTags(value: string): string[] {
  return value
    .split(/[\n,]/)
    .map((item) => item.trim())
    .filter(Boolean);
}

function splitLines(value: string): string[] {
  return value
    .split('\n')
    .map((item) => item.trim())
    .filter(Boolean);
}

function formatScore(value: number): string {
  return value.toFixed(2);
}

function formatDate(value: string): string {
  return value.slice(0, 10);
}

function formatDateTime(value: string): string {
  return new Date(value).toLocaleString('ru-RU', {
    day: '2-digit',
    month: '2-digit',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  });
}

function authorNoteTypeLabel(type: AuthorNoteType): string {
  if (type === 'linkReaction') return 'Реакция';
  if (type === 'manualCorrection') return 'Правка';
  return 'Мысль';
}

function assertionTypeLabel(type: string): string {
  if (type === 'persona') return 'Образ';
  if (type === 'style') return 'Стиль';
  if (type === 'audience') return 'Аудитория';
  if (type === 'topic') return 'Тема';
  return 'Принцип';
}

function deriveNoteTitle(note: AuthorNote): string {
  if (note.title.trim()) return note.title;

  const normalized = note.body.replace(/\s+/g, ' ').trim();
  if (!normalized) return authorNoteTypeLabel(note.type);

  return normalized.length > 64 ? `${normalized.slice(0, 61)}...` : normalized;
}

function buildLinkPreview(value: string): LinkPreview {
  const trimmed = value.trim();

  if (!trimmed) {
    return { isValid: false, domain: '', normalizedUrl: '', title: '' };
  }

  try {
    const url = new URL(trimmed.startsWith('http') ? trimmed : `https://${trimmed}`);
    const domain = url.hostname.replace(/^www\./, '');

    return {
      isValid: true,
      domain,
      normalizedUrl: url.toString(),
      title: `Ссылка из ${domain}`
    };
  } catch {
    return { isValid: false, domain: '', normalizedUrl: trimmed, title: '' };
  }
}

function getMemorySummary(notes: AuthorNote[]) {
  const now = new Date();
  const currentMonth = now.getMonth();
  const currentYear = now.getFullYear();

  return notes.reduce(
    (summary, note) => {
      const capturedAt = new Date(note.capturedAt);
      const isSameYear = capturedAt.getFullYear() === currentYear;

      return {
        total: summary.total + 1,
        thoughts: summary.thoughts + (note.type === 'thought' ? 1 : 0),
        links: summary.links + (note.type === 'linkReaction' ? 1 : 0),
        corrections: summary.corrections + (note.type === 'manualCorrection' ? 1 : 0),
        thisMonth: summary.thisMonth + (isSameYear && capturedAt.getMonth() === currentMonth ? 1 : 0),
        thisYear: summary.thisYear + (isSameYear ? 1 : 0)
      };
    },
    { total: 0, thoughts: 0, links: 0, corrections: 0, thisMonth: 0, thisYear: 0 }
  );
}

function filterAuthorNotes(notes: AuthorNote[], query: string, filter: MemoryTypeFilter): AuthorNote[] {
  const normalizedQuery = query.trim().toLowerCase();

  return notes.filter((note) => {
    const matchesType = filter === 'all' || note.type === filter;
    const haystack = [
      note.title,
      note.body,
      note.sourceUrl,
      note.targetTitle ?? '',
      ...note.tags
    ]
      .join(' ')
      .toLowerCase();

    return matchesType && (!normalizedQuery || haystack.includes(normalizedQuery));
  });
}

function isEvidenceNote(noteId: string, assertions: AuthorPositionAssertion[]): boolean {
  return assertions.some((assertion) => assertion.evidence.some((item) => item.noteId === noteId));
}

function buildCorrectionTargets(assertions: AuthorPositionAssertion[]): CorrectionTarget[] {
  return assertions.flatMap((assertion) => [
    { type: 'assertion' as const, id: assertion.id, title: assertion.title },
    ...assertion.evidence.map((item) => buildEvidenceCorrectionTarget(assertion, item))
  ]);
}

function buildEvidenceCorrectionTarget(
  assertion: AuthorPositionAssertion,
  item: { noteId: string; quote: string }
): CorrectionTarget {
  return {
    type: 'evidence',
    id: `${assertion.id}:${item.noteId}`,
    title: `${assertion.title}: ${item.quote.slice(0, 60)}`
  };
}

function correctionTargetKey(target: CorrectionTarget): string {
  return `${target.type}:${target.id}`;
}

function hasCorrectionConflict(value: string): boolean {
  const normalized = value.toLowerCase();
  return ['не согласен', 'неверно', 'противоречит', 'убрать', 'заменить', 'не так'].some((marker) =>
    normalized.includes(marker)
  );
}

async function createAuthorAttachment(
  file: File | undefined
): Promise<{ attachment: AuthorAttachment } | { error: string }> {
  if (!file) {
    return { error: 'Файл не выбран.' };
  }

  if (file.size > MAX_AUTHOR_ATTACHMENT_BYTES) {
    return { error: 'Файл больше 1 MB. Для локального демо добавьте ссылку или короткую выдержку.' };
  }

  return {
    attachment: {
      id: `attachment-${Date.now()}`,
      fileName: file.name,
      mimeType: file.type || 'application/octet-stream',
      sizeBytes: file.size,
      dataUrl: await readFileAsDataUrl(file),
      createdAt: new Date().toISOString(),
      localOnly: true
    }
  };
}

function readFileAsDataUrl(file: File): Promise<string> {
  return new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.onerror = () => reject(new Error('Failed to read file'));
    reader.onload = () => resolve(String(reader.result ?? ''));
    reader.readAsDataURL(file);
  });
}

function formatBytes(value: number): string {
  if (value < 1024) return `${value} B`;
  if (value < 1024 * 1024) return `${(value / 1024).toFixed(1)} KB`;
  return `${(value / (1024 * 1024)).toFixed(1)} MB`;
}

function attachmentTypeLabel(attachment: AuthorAttachment): string {
  if (attachment.mimeType.includes('pdf')) return 'PDF';
  if (attachment.mimeType.includes('word') || attachment.fileName.match(/\.docx?$/i)) return 'DOC';
  if (attachment.mimeType.startsWith('text/') || attachment.fileName.match(/\.(md|txt)$/i)) return 'TXT';
  return 'FILE';
}

function getSpeechRecognitionConstructor() {
  const speechWindow = window as SpeechRecognitionWindow;
  return speechWindow.SpeechRecognition ?? speechWindow.webkitSpeechRecognition;
}

function sourceTypeLabel(type: string): string {
  const labels: Record<string, string> = {
    telegramChannel: 'Telegram archive',
    socialProfile: 'Social profile',
    blogSite: 'Blog/site',
    document: 'Document',
    articleArchive: 'Article archive',
    manualUpload: 'Manual upload'
  };

  return labels[type] ?? type;
}

function sourceStatusLabel(status: string): string {
  const labels: Record<string, string> = {
    planned: 'Запланирован',
    connected: 'Демо подключен',
    needsReview: 'Нужен review',
    imported: 'Импортирован',
    paused: 'Пауза',
    failed: 'Ошибка'
  };

  return labels[status] ?? status;
}

function importModeLabel(mode: string): string {
  const labels: Record<string, string> = {
    manualOnly: 'Только вручную',
    reviewedQueue: 'Через очередь',
    archiveOnly: 'Только архив',
    bulkArchive: 'Bulk archive'
  };

  return labels[mode] ?? mode;
}

function evidencePolicyLabel(policy: string): string {
  const labels: Record<string, string> = {
    canSupportAssertions: 'Может поддержать выводы',
    archiveOnly: 'Только архив',
    ignored: 'Не evidence'
  };

  return labels[policy] ?? policy;
}

function reviewStatusLabel(status: string): string {
  const labels: Record<string, string> = {
    new: 'Новый',
    acceptedToMemory: 'В памяти',
    acceptedToArchive: 'В архиве',
    bulkAcceptedToArchive: 'Bulk archive',
    rejected: 'Отклонен',
    ignoredForEvidence: 'Не evidence'
  };

  return labels[status] ?? status;
}

function duplicateRiskLabel(risk: string): string {
  if (risk === 'high') return 'high';
  if (risk === 'medium') return 'medium';
  return 'low';
}

function getImportSummary(
  sources: AuthorExternalSource[],
  candidates: ImportedMemoryCandidate[],
  archiveRecords: ArchiveRecord[],
  actions: BulkImportAction[]
) {
  return {
    sources: sources.length,
    candidates: candidates.length,
    needsReview: candidates.filter((candidate) => candidate.reviewStatus === 'new').length,
    archived: archiveRecords.length,
    bulkAccepted: candidates.filter((candidate) => candidate.reviewStatus === 'bulkAcceptedToArchive').length,
    undoAvailable: actions.some((action) => action.canUndo) ? 1 : 0
  };
}

function formatImportFilters(filters: ImportCandidateFilters): string {
  return [
    filters.sourceId && filters.sourceId !== 'all' ? `source=${filters.sourceId}` : '',
    filters.reviewStatus && filters.reviewStatus !== 'all' ? `status=${filters.reviewStatus}` : '',
    filters.evidencePolicy && filters.evidencePolicy !== 'all' ? `policy=${filters.evidencePolicy}` : '',
    filters.duplicateRisk && filters.duplicateRisk !== 'all' ? `risk=${filters.duplicateRisk}` : '',
    filters.query ? `query=${filters.query}` : ''
  ]
    .filter(Boolean)
    .join(', ') || 'нет';
}

function statusLabel(status: string): string {
  if (status === 'approved') return 'Утверждено';
  if (status === 'rejected') return 'Отклонено';
  return 'Черновик';
}

function checkStatusLabel(status: string): string {
  if (status === 'passed') return 'Пройдено';
  if (status === 'warning') return 'Есть warning';
  return 'Блокер';
}

function releaseStatusLabel(status: string): string {
  if (status === 'ready') return 'Готово к выпуску';
  if (status === 'exported') return 'Экспортировано вручную';
  return 'Черновик выпуска';
}

function analyticsStatusLabel(status: string): string {
  if (status === 'captured') return 'Выводы зафиксированы';
  return 'Черновик аналитики';
}

function targetLabel(target: string): string {
  if (target === 'telegram') return 'Telegram';
  if (target === 'linkedin') return 'LinkedIn';
  return target;
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
