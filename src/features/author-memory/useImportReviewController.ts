import { useMemo, useState } from 'react';
import { createAuthorMemoryEvent, inferAuthorPositionAssertions } from '../../application/editorialServices';
import { acceptCandidateToArchive, acceptCandidateToMemory, bulkAcceptCandidatesToArchive, bulkRejectCandidates, filterImportCandidates, groupImportCandidates, ignoreCandidateForEvidence, markCandidateAcceptedToArchive, markCandidateAcceptedToMemory, rejectCandidate, undoLastBulkImportAction, type ArchiveRecord, type AuthorExternalSource, type AuthorNote, type ImportedMemoryCandidate, type ImportCandidateFilters, type ImportCandidateGroupType, type WorkspaceState } from '../../domain/editorialWorkspace';
import type { ImportViewMode, MemoryInternalTab, PendingBulkAction } from './types';
import { getImportSummary } from './helpers';

export function useImportReviewController({
  workspace,
  onChangeTab,
  onPatchWorkspace
}: {
  workspace: WorkspaceState;
  onChangeTab: (tab: MemoryInternalTab) => void;
  onPatchWorkspace: (patch: Partial<WorkspaceState>, message?: string) => void;
}) {
  const notes = workspace.authorNotes;
  const externalSources = workspace.externalSources;
  const importCandidates = workspace.importCandidates;
  const archiveRecords = workspace.archiveRecords;
  const bulkImportActions = workspace.bulkImportActions;
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
    onChangeTab('feed');
  }

  function acceptToArchive(candidate: ImportedMemoryCandidate) {
    addArchiveRecord(
      candidate,
      acceptCandidateToArchive(candidate, findSource(candidate)),
      'Кандидат принят в архив'
    );
  }

  function performPendingBulkAction(action: PendingBulkAction) {
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
    onChangeTab('queue');
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
    onChangeTab('queue');
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

  function patchSource(source: AuthorExternalSource) {
    onPatchWorkspace(
      {
        externalSources: externalSources.map((item) => (item.id === source.id ? source : item))
      },
      'Статус демо-источника обновлен'
    );
  }

  return {
    archiveRecords, bulkImportActions, candidateFilters, externalSources, filteredCandidates,
    importCandidates, importGroups, importSummary, importViewMode, groupMode,
    pendingBulkAction, selectedCandidateIds, acceptArchiveRecordToMemory,
    acceptToArchive, acceptToMemory, clearCandidateSelection, deleteArchiveRecord,
    ignoreArchiveRecord, openQueueForSource, patchSource, performPendingBulkAction,
    replaceImportCandidate, restoreArchiveRecordToQueue, setCandidateFilters,
    setGroupMode, setImportViewMode, setPendingBulkAction, toggleCandidateSelection,
    undoLatestBulkAction, unselectCandidates, selectCandidates
  };
}

export type ImportReviewController = ReturnType<typeof useImportReviewController>;
