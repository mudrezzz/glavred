import type { AuthorExternalSource, AuthorNote, ImportedMemoryCandidate } from '../author-memory/types';
import type { WorkspaceState } from '../workspace/types';
import type { ArchiveRecord, BulkImportAction, ImportCandidateFilters, ImportCandidateGroup, ImportCandidateGroupType, ImportReviewStatus, ImportRiskLevel } from './types';

// Import transitions keep archive-only material out of author-position evidence until accepted.
export function acceptCandidateToMemory(
  candidate: ImportedMemoryCandidate,
  source: AuthorExternalSource
): AuthorNote {
  return {
    id: `note-import-${candidate.id}`,
    type: 'linkReaction',
    title: candidate.title,
    body: candidate.excerpt,
    sourceUrl: candidate.originalUrl || source.url,
    tags: Array.from(new Set([...candidate.detectedTags, 'imported'])),
    attachments: [],
    capturedAt: new Date().toISOString()
  };
}

export function markCandidateAcceptedToMemory(
  candidate: ImportedMemoryCandidate
): ImportedMemoryCandidate {
  return {
    ...candidate,
    reviewStatus: 'acceptedToMemory',
    evidencePolicy: 'canSupportAssertions'
  };
}

export function acceptCandidateToArchive(
  candidate: ImportedMemoryCandidate,
  _source: AuthorExternalSource,
  mode: 'manual' | 'bulk' = 'manual'
): ArchiveRecord {
  return {
    id: `archive-${candidate.id}`,
    sourceId: candidate.sourceId,
    title: candidate.title,
    bodyExcerpt: candidate.excerpt,
    originalUrl: candidate.originalUrl,
    publishedAt: candidate.capturedAt,
    acceptedAt: new Date().toISOString(),
    acceptanceMode: mode,
    evidencePolicy: mode === 'bulk' ? 'archiveOnly' : candidate.evidencePolicy
  };
}

export function markCandidateAcceptedToArchive(
  candidate: ImportedMemoryCandidate,
  mode: 'manual' | 'bulk' = 'manual'
): ImportedMemoryCandidate {
  return {
    ...candidate,
    reviewStatus: mode === 'bulk' ? 'bulkAcceptedToArchive' : 'acceptedToArchive',
    evidencePolicy: 'archiveOnly'
  };
}

export function rejectCandidate(candidate: ImportedMemoryCandidate): ImportedMemoryCandidate {
  return {
    ...candidate,
    reviewStatus: 'rejected',
    evidencePolicy: 'ignored'
  };
}

export function ignoreCandidateForEvidence(candidate: ImportedMemoryCandidate): ImportedMemoryCandidate {
  return {
    ...candidate,
    reviewStatus: 'ignoredForEvidence',
    evidencePolicy: 'ignored'
  };
}

export function bulkAcceptCandidatesToArchive(
  candidates: ImportedMemoryCandidate[],
  sources: AuthorExternalSource[]
): {
  candidates: ImportedMemoryCandidate[];
  archiveRecords: ArchiveRecord[];
  action: BulkImportAction;
} {
  const sourceById = new Map(sources.map((source) => [source.id, source]));
  const changedCandidates = candidates.map((candidate) => markCandidateAcceptedToArchive(candidate, 'bulk'));
  const archiveRecords = candidates.map((candidate) =>
    acceptCandidateToArchive(
      candidate,
      sourceById.get(candidate.sourceId) ?? {
        id: candidate.sourceId,
        type: 'manualUpload',
        title: candidate.sourceId,
        url: '',
        fileReference: '',
        status: 'planned',
        importMode: 'archiveOnly',
        lastCheckedAt: '',
        lastImportedAt: '',
        notes: ''
      },
      'bulk'
    )
  );

  return {
    candidates: changedCandidates,
    archiveRecords,
    action: {
      id: `bulk-archive-${Date.now()}`,
      action: 'bulkAcceptToArchive',
      candidateIds: candidates.map((candidate) => candidate.id),
      previousStatuses: Object.fromEntries(candidates.map((candidate) => [candidate.id, candidate.reviewStatus])),
      createdAt: new Date().toISOString(),
      canUndo: true,
      createdArchiveRecordIds: archiveRecords.map((record) => record.id)
    }
  };
}

export function bulkRejectCandidates(candidates: ImportedMemoryCandidate[]): {
  candidates: ImportedMemoryCandidate[];
  action: BulkImportAction;
} {
  return {
    candidates: candidates.map(rejectCandidate),
    action: {
      id: `bulk-reject-${Date.now()}`,
      action: 'bulkReject',
      candidateIds: candidates.map((candidate) => candidate.id),
      previousStatuses: Object.fromEntries(candidates.map((candidate) => [candidate.id, candidate.reviewStatus])),
      createdAt: new Date().toISOString(),
      canUndo: true,
      createdArchiveRecordIds: []
    }
  };
}

export function undoLastBulkImportAction(workspace: WorkspaceState): WorkspaceState {
  const lastAction = [...workspace.bulkImportActions].reverse().find((action) => action.canUndo);

  if (!lastAction) {
    return workspace;
  }

  return {
    ...workspace,
    importCandidates: workspace.importCandidates.map((candidate) =>
      lastAction.previousStatuses[candidate.id]
        ? { ...candidate, reviewStatus: lastAction.previousStatuses[candidate.id] }
        : candidate
    ),
    archiveRecords: workspace.archiveRecords.filter(
      (record) => !lastAction.createdArchiveRecordIds.includes(record.id)
    ),
    bulkImportActions: workspace.bulkImportActions.filter((action) => action.id !== lastAction.id)
  };
}

export function filterImportCandidates(
  candidates: ImportedMemoryCandidate[],
  filters: ImportCandidateFilters
): ImportedMemoryCandidate[] {
  const query = filters.query?.trim().toLowerCase() ?? '';

  return candidates.filter((candidate) => {
    const matchesSource = !filters.sourceId || filters.sourceId === 'all' || candidate.sourceId === filters.sourceId;
    const matchesStatus =
      !filters.reviewStatus || filters.reviewStatus === 'all' || candidate.reviewStatus === filters.reviewStatus;
    const matchesPolicy =
      !filters.evidencePolicy ||
      filters.evidencePolicy === 'all' ||
      candidate.evidencePolicy === filters.evidencePolicy;
    const matchesRisk =
      !filters.duplicateRisk || filters.duplicateRisk === 'all' || candidate.duplicateRisk === filters.duplicateRisk;
    const haystack = [
      candidate.title,
      candidate.excerpt,
      candidate.originalUrl,
      candidate.suggestedTarget,
      ...candidate.detectedTags
    ]
      .join(' ')
      .toLowerCase();

    return matchesSource && matchesStatus && matchesPolicy && matchesRisk && (!query || haystack.includes(query));
  });
}

export function groupImportCandidates(
  candidates: ImportedMemoryCandidate[],
  mode: ImportCandidateGroupType = 'source'
): ImportCandidateGroup[] {
  const grouped = candidates.reduce<Record<string, ImportedMemoryCandidate[]>>((groups, candidate) => {
    const key =
      mode === 'source'
        ? candidate.sourceId
        : mode === 'status'
          ? candidate.reviewStatus
          : mode === 'duplicateRisk'
            ? candidate.duplicateRisk
            : mode === 'evidencePolicy'
              ? candidate.evidencePolicy
              : candidate.detectedTags[0] ?? 'untagged';

    return {
      ...groups,
      [key]: [...(groups[key] ?? []), candidate]
    };
  }, {});

  return Object.entries(grouped).map(([key, items]) => ({
    id: `${mode}-${key}`,
    type: mode,
    title: key,
    candidateIds: items.map((item) => item.id),
    summary: `${items.length} candidates`,
    riskLevel: items.some((item) => item.duplicateRisk === 'high')
      ? 'high'
      : items.some((item) => item.duplicateRisk === 'medium')
        ? 'medium'
      : 'low'
  }));
}

