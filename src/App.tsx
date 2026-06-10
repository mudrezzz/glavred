import { useEffect, useMemo, useState } from 'react';
import {
  createAuthorMemoryEvent,
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
  approveFinalText,
  approvePlanItem,
  approvePostBrief,
  markLearningNoteCaptured,
  markReleaseExported,
  markReleaseReady,
  reviseDraft,
  toggleReleaseChecklistItem,
  updateLearningNote,
  type AuthorAttachment,
  type AuthorNote,
  type AuthorNoteType,
  type AuthorPositionAssertion,
  type EditorialCheck,
  type EditorialLearningNote,
  type EditorialModel,
  type FinalText,
  type ManualMetricSnapshot,
  type PostBrief,
  type PostDraft,
  type ReleasePackage,
  type SourceSignal,
  type WorkspaceSection,
  type WorkspaceState
} from './domain/editorialWorkspace';
import { LocalWorkspaceStore } from './infrastructure/localWorkspaceStore';

const store = new LocalWorkspaceStore();

const NAV: Array<{ id: WorkspaceSection; icon: string; label: string; count?: string; disabled?: boolean }> = [
  { id: 'memory', icon: 'memory', label: 'Память автора' },
  { id: 'editorialModel', icon: 'model', label: 'Редакционная модель' },
  { id: 'radar', icon: 'radar', label: 'Радар', count: '1' },
  { id: 'plan', icon: 'plan', label: 'План', count: '1' },
  { id: 'brief', icon: 'brief', label: 'Фабулы', count: '1' },
  { id: 'edit', icon: 'edit', label: 'Редактура' },
  { id: 'release', icon: 'release', label: 'Выпуск' },
  { id: 'analytics', icon: 'analytics', label: 'Аналитика' }
];

const TITLES: Record<WorkspaceSection, [string, string]> = {
  memory: ['Память автора', 'Заметки -> позиция автора'],
  editorialModel: ['Редакционная модель', 'Правила и контекст блога'],
  radar: ['Радар', 'Источник -> инсайт'],
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
  const [toast, setToast] = useState('Рабочее пространство сохранено локально');

  useEffect(() => {
    store.save({ ...workspace, updatedAt: new Date().toISOString() });
  }, [workspace]);

  function patchWorkspace(patch: Partial<WorkspaceState>, message?: string) {
    setWorkspace((current) => ({ ...current, ...patch, updatedAt: new Date().toISOString() }));
    if (message) {
      setToast(message);
    }
  }

  function go(section: WorkspaceSection) {
    patchWorkspace({ activeSection: section });
  }

  function resetDemo() {
    setWorkspace(store.reset());
    setToast('Демо-сценарий восстановлен');
  }

  return (
    <div className="app">
      <Sidebar active={active} onNav={go} workspace={workspace} />
      <main className="main">
        <Topbar active={active} onReset={resetDemo} />
        <div className="scroll">
          {active === 'memory' && (
            <AuthorMemoryView
              notes={workspace.authorNotes}
              assertions={workspace.authorPositionAssertions}
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
              model={workspace.editorialModel}
              onChange={(editorialModel) => patchWorkspace({ editorialModel })}
            />
          )}
          {active === 'radar' && (
            <RadarView
              workspace={workspace}
              onSignalChange={(sourceSignal) => patchWorkspace({ sourceSignal })}
              onCreateInsight={() => {
                const insightCard = createInsightCard(workspace.sourceSignal, workspace.editorialModel);
                patchWorkspace({ insightCard }, 'Карточка инсайта собрана');
              }}
              onPlan={() => {
                const insightCard =
                  workspace.insightCard ?? createInsightCard(workspace.sourceSignal, workspace.editorialModel);
                const contentPlanItem = createContentPlanItem(insightCard);
                patchWorkspace(
                  { insightCard, contentPlanItem, activeSection: 'plan' },
                  'Инсайт добавлен в план'
                );
              }}
            />
          )}
          {active === 'plan' && (
            <PlanView
              workspace={workspace}
              onApprove={() => {
                if (!workspace.contentPlanItem) return;
                patchWorkspace(
                  { contentPlanItem: approvePlanItem(workspace.contentPlanItem) },
                  'План утвержден'
                );
              }}
              onBrief={() => {
                if (!workspace.contentPlanItem || !workspace.insightCard) return;
                const postBrief = createPostBrief(
                  workspace.contentPlanItem,
                  workspace.insightCard,
                  workspace.editorialModel
                );
                patchWorkspace({ postBrief, activeSection: 'brief' }, 'Фабула подготовлена');
              }}
            />
          )}
          {active === 'brief' && (
            <BriefView
              workspace={workspace}
              onBriefChange={(postBrief) => patchWorkspace({ postBrief })}
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
          {item.id !== 'memory' && item.count ? <span className="count">{item.count}</span> : null}
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

function Topbar({ active, onReset }: { active: WorkspaceSection; onReset: () => void }) {
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
      <button className="btn btn-sec btn-sm" type="button" onClick={onReset}>
        <Icon name="reset" size={14} />
        Сбросить демо
      </button>
    </header>
  );
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
  notes,
  assertions,
  onChangeNotes
}: {
  notes: AuthorNote[];
  assertions: AuthorPositionAssertion[];
  onChangeNotes: (notes: AuthorNote[], message?: string) => void;
}) {
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
  const correctionTargets = useMemo(() => buildCorrectionTargets(assertions), [assertions]);
  const summary = useMemo(() => getMemorySummary(notes), [notes]);
  const filteredNotes = useMemo(() => filterAuthorNotes(notes, query, filter), [filter, notes, query]);
  const visibleNotes = filteredNotes.slice(0, visibleCount);
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
      <div className="memory-grid">
        <section className="memory-main">
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
        </section>

        <aside className="memory-side">
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

function EditorialModelView({
  model,
  onChange
}: {
  model: EditorialModel;
  onChange: (model: EditorialModel) => void;
}) {
  return (
    <div className="page wide fade-up">
      <section className="model-hero">
        <blockquote>{model.fabula}</blockquote>
        <span className="gr-mark">Фабула блога · ядро решений редакции</span>
      </section>
      <div className="model-grid">
        <TextAreaCard title="Автор" value={model.author} onChange={(author) => onChange({ ...model, author })} />
        <TextAreaCard
          title="Аудитория"
          value={model.audience}
          onChange={(audience) => onChange({ ...model, audience })}
        />
        <TextAreaCard
          title="Позиционирование"
          value={model.positioning}
          onChange={(positioning) => onChange({ ...model, positioning })}
        />
        <TextAreaCard
          title="Фабула"
          value={model.fabula}
          onChange={(fabula) => onChange({ ...model, fabula })}
        />
        <ListCard title="Рубрики" items={model.rubrics} onChange={(rubrics) => onChange({ ...model, rubrics })} />
        <ListCard
          title="Стиль автора"
          items={model.styleRules}
          onChange={(styleRules) => onChange({ ...model, styleRules })}
        />
        <ListCard
          title="Запреты"
          items={model.forbiddenTopics}
          onChange={(forbiddenTopics) => onChange({ ...model, forbiddenTopics })}
        />
        <ListCard title="Цели блога" items={model.goals} onChange={(goals) => onChange({ ...model, goals })} />
      </div>
    </div>
  );
}

function TextAreaCard({
  title,
  value,
  onChange
}: {
  title: string;
  value: string;
  onChange: (value: string) => void;
}) {
  return (
    <label className="card edit-card">
      <span>{title}</span>
      <textarea value={value} onChange={(event) => onChange(event.target.value)} />
    </label>
  );
}

function ListCard({
  title,
  items,
  onChange
}: {
  title: string;
  items: string[];
  onChange: (items: string[]) => void;
}) {
  return (
    <label className="card edit-card">
      <span>{title}</span>
      <textarea value={items.join('\n')} onChange={(event) => onChange(splitLines(event.target.value))} />
    </label>
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
  onApprove,
  onBrief
}: {
  workspace: WorkspaceState;
  onApprove: () => void;
  onBrief: () => void;
}) {
  const item = workspace.contentPlanItem;

  return (
    <div className="page wide fade-up">
      <HitlGate
        tag="HITL · Gate 1 — План"
        title="Утвердите публикацию перед фабулой"
        subtitle="План фиксирует формат, дату, площадку и ожидаемый эффект."
        action="Утвердить план"
        disabled={!item}
        onAction={onApprove}
      />
      {item ? (
        <div className="week single-week">
          <div className="day today">
            <div className="dh">
              <b>Пт</b>
              <span>5 июня</span>
            </div>
            <article className="pcard">
              <span className="rub">{item.format}</span>
              <div className="pt">{item.title}</div>
              <div className="pf">
                <span className="plat">{item.platform}</span>
                <span className={`pill ${item.approvalStatus === 'approved' ? 'ok' : 'pin'}`}>
                  <i />
                  {statusLabel(item.approvalStatus)}
                </span>
              </div>
            </article>
            <p className="plan-effect">{item.expectedEffect}</p>
            <button
              className="btn btn-pri"
              type="button"
              disabled={item.approvalStatus !== 'approved'}
              onClick={onBrief}
            >
              <Icon name="brief" size={16} />
              Подготовить фабулу
            </button>
          </div>
        </div>
      ) : (
        <EmptyState text="Сначала добавьте инсайт в план из раздела «Радар»." />
      )}
    </div>
  );
}

function BriefView({
  workspace,
  onBriefChange,
  onApprove
}: {
  workspace: WorkspaceState;
  onBriefChange: (brief: PostBrief) => void;
  onApprove: () => void;
}) {
  const brief = workspace.postBrief;

  if (!brief) {
    return (
      <div className="page fade-up">
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
