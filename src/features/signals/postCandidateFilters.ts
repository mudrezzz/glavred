import type { WorkspaceState } from '../../domain/editorialWorkspace';
import type { CandidateGroupMode, CandidateRiskLevel, PostCandidateFilters, PostCandidateGroup } from './postCandidateTypes';

type Candidate = WorkspaceState['postCandidates'][number];

export function getCandidateRiskLevel(candidate: { confidence: number; risks: string[] }): CandidateRiskLevel {
  if (candidate.risks.some((risk) => risk.toLowerCase().includes('высокий')) || candidate.confidence < 0.75) {
    return 'high';
  }
  if (candidate.risks.length > 0 || candidate.confidence < 0.85) return 'medium';
  return 'low';
}

export function candidateMatchesFilters(candidate: Candidate, filters: PostCandidateFilters): boolean {
  const query = filters.query.trim().toLowerCase();

  return (
    (filters.signalId === 'all' || candidate.sourceSignalId === filters.signalId) &&
    (filters.status === 'all' || candidate.approvalStatus === filters.status) &&
    (filters.topicId === 'all' || candidate.topicId === filters.topicId) &&
    (filters.risk === 'all' ||
      (filters.risk === 'withRisks' ? candidate.risks.length > 0 : getCandidateRiskLevel(candidate) === filters.risk)) &&
    (!query ||
      [candidate.title, candidate.thesis, candidate.value, candidate.evidenceSummary]
        .join(' ')
        .toLowerCase()
        .includes(query))
  );
}

export function groupCandidates(
  candidates: Candidate[],
  groupMode: CandidateGroupMode,
  workspace: WorkspaceState
): PostCandidateGroup[] {
  const groups = new Map<string, Candidate[]>();

  for (const candidate of candidates) {
    const id = getGroupId(candidate, groupMode);
    groups.set(id, [...(groups.get(id) ?? []), candidate]);
  }

  return Array.from(groups, ([id, groupCandidates]) => ({
    id,
    title: getGroupTitle(id, groupMode, workspace),
    candidates: groupCandidates
  }));
}

function getGroupId(candidate: Candidate, groupMode: CandidateGroupMode): string {
  if (groupMode === 'signal') return candidate.sourceSignalId;
  if (groupMode === 'topic') return candidate.topicId;
  if (groupMode === 'risk') return getCandidateRiskLevel(candidate);
  return candidate.approvalStatus;
}

function getGroupTitle(id: string, groupMode: CandidateGroupMode, workspace: WorkspaceState): string {
  if (groupMode === 'signal') return workspace.sourceSignals.find((signal) => signal.id === id)?.title ?? id;
  if (groupMode === 'topic') return workspace.topics.find((topic) => topic.id === id)?.title ?? id;
  if (groupMode === 'risk') return `Risk ${id}`;
  if (id === 'approved') return 'Утвержденные';
  if (id === 'rejected') return 'Отклоненные';
  return 'Новые';
}
