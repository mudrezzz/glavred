import type { AuthorExternalSource, ImportedMemoryCandidate } from '../../domain/editorialWorkspace';
import { CandidateCard } from './CandidateCard';
import { ImportQueueEmptyState } from './ImportQueueEmptyState';

export function ImportCandidateList({
  filteredCandidates,
  selectedCandidateIds,
  sources,
  onAcceptToArchive,
  onAcceptToMemory,
  onIgnoreEvidence,
  onReject,
  onSelect
}: {
  filteredCandidates: ImportedMemoryCandidate[];
  selectedCandidateIds: string[];
  sources: AuthorExternalSource[];
  onAcceptToArchive: (candidate: ImportedMemoryCandidate) => void;
  onAcceptToMemory: (candidate: ImportedMemoryCandidate) => void;
  onIgnoreEvidence: (candidate: ImportedMemoryCandidate) => void;
  onReject: (candidate: ImportedMemoryCandidate) => void;
  onSelect: (candidateId: string) => void;
}) {
  return (
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
      {filteredCandidates.length === 0 ? <ImportQueueEmptyState /> : null}
    </div>
  );
}
