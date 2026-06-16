import { useMemo, useState } from 'react';
import { createPostCandidates } from '../../application/editorialServices';
import type { WorkspaceState } from '../../domain/editorialWorkspace';
import { candidateMatchesFilters, groupCandidates } from './postCandidateFilters';
import type { CandidateGroupMode, CandidateViewMode, PostCandidateFilters } from './postCandidateTypes';

export function usePostCandidatesController(workspace: WorkspaceState) {
  const [filters, setFilters] = useState<PostCandidateFilters>({
    signalId: 'all',
    status: 'all',
    topicId: 'all',
    risk: 'all',
    query: ''
  });
  const [viewMode, setViewMode] = useState<CandidateViewMode>('list');
  const [groupMode, setGroupMode] = useState<CandidateGroupMode>('signal');

  const derived = useMemo(() => {
    const candidates = createPostCandidates(workspace);
    const approvedSignals = workspace.sourceSignals.filter((signal) => signal.reviewStatus === 'approved');
    const filteredCandidates = candidates.filter((candidate) => candidateMatchesFilters(candidate, filters));

    return {
      approvedSignalCount: approvedSignals.length,
      candidates,
      filteredCandidates,
      groups: groupCandidates(filteredCandidates, groupMode, workspace),
      selectedCandidateId: workspace.postCandidate?.id ?? ''
    };
  }, [filters, groupMode, workspace]);

  return {
    ...derived,
    filters,
    groupMode,
    viewMode,
    setFilters,
    setGroupMode,
    setViewMode
  };
}
