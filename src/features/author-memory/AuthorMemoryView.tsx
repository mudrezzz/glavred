import { useEffect, useMemo, useState } from 'react';
import { type ContextChatIntent } from '../../application/contextChat';
import { createAuthorMemoryEvent, inferAuthorPositionAssertions } from '../../application/editorialServices';
import {
  acceptCandidateToArchive,
  acceptCandidateToMemory,
  bulkAcceptCandidatesToArchive,
  bulkRejectCandidates,
  filterImportCandidates,
  groupImportCandidates,
  ignoreCandidateForEvidence,
  markCandidateAcceptedToArchive,
  markCandidateAcceptedToMemory,
  rejectCandidate,
  undoLastBulkImportAction,
  type ArchiveRecord,
  type AuthorAttachment,
  type AuthorExternalSource,
  type AuthorNote,
  type AuthorNoteType,
  type AuthorPositionAssertion,
  type BulkImportAction,
  type EvidencePolicy,
  type ImportedMemoryCandidate,
  type ImportCandidateFilters,
  type ImportCandidateGroupType,
  type ImportReviewStatus,
  type ImportRiskLevel,
  type WorkspaceState
} from '../../domain/editorialWorkspace';
import { Icon } from '../../shared/ui/Icon';
import type { CorrectionTarget, ImportViewMode, LinkPreview, MemoryInternalTab, MemoryTypeFilter, PendingBulkAction, PendingCorrectionConflict } from './types';
import { ArchiveView, BulkActionDialog, ExternalSourcesView, ImportQueueView } from './ImportViews';
import {
  AssertionCard,
  AttachmentList,
  EmptyState,
  FileAttachmentPicker,
  LinkPreviewCard,
  MemoryTabNav,
  SummaryItem,
  AuthorNoteCard
} from './components';
import {
  attachmentTypeLabel,
  authorNoteTypeLabel,
  assertionTypeLabel,
  buildCorrectionTargets,
  buildEvidenceCorrectionTarget,
  buildLinkPreview,
  createAuthorAttachment,
  correctionTargetKey,
  deriveNoteTitle,
  duplicateRiskLabel,
  evidencePolicyLabel,
  filterAuthorNotes,
  formatBytes,
  formatDate,
  formatDateTime,
  formatImportFilters,
  formatScore,
  getImportSummary,
  getMemorySummary,
  getSpeechRecognitionConstructor,
  hasCorrectionConflict,
  importModeLabel,
  isEvidenceNote,
  MAX_AUTHOR_ATTACHMENT_BYTES,
  readFileAsDataUrl,
  reviewStatusLabel,
  sourceStatusLabel,
  sourceTypeLabel,
  splitLines,
  splitTags
} from './helpers';

export function AuthorMemoryView({
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
