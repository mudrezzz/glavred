import type {
  Fabula,
  PostCandidate,
  PostCandidateEditPatch,
  SourceSignal,
  Topic,
  TopicFabulaMatrixEntry
} from '../../domain/editorialWorkspace';
import { PostCandidateCard } from './PostCandidateCard';
import type { PostCandidateGroup } from './postCandidateTypes';

export function PostCandidateGroupList({
  fabulas,
  groups,
  matrix,
  selectedCandidateId,
  signals,
  topics,
  onApprove,
  onEdit,
  onReject
}: {
  fabulas: Fabula[];
  groups: PostCandidateGroup[];
  matrix: TopicFabulaMatrixEntry[];
  selectedCandidateId: string;
  signals: SourceSignal[];
  topics: Topic[];
  onApprove: (candidate: PostCandidate) => void;
  onEdit: (candidate: PostCandidate, patch: PostCandidateEditPatch) => void;
  onReject: (candidate: PostCandidate) => void;
}) {
  return (
    <div className="post-candidate-groups">
      {groups.map((group) => (
        <section className="candidate-group" key={group.id}>
          <div className="entity-list-toolbar">
            <div className="entity-toolbar-copy">
              <h2>{group.title}</h2>
              <p>{group.candidates.length} кандидата</p>
            </div>
          </div>
          <PostCandidateRows
            candidates={group.candidates}
            fabulas={fabulas}
            matrix={matrix}
            selectedCandidateId={selectedCandidateId}
            signals={signals}
            topics={topics}
            onApprove={onApprove}
            onEdit={onEdit}
            onReject={onReject}
          />
        </section>
      ))}
    </div>
  );
}

export function PostCandidateRows({
  candidates,
  fabulas,
  matrix,
  selectedCandidateId,
  signals,
  topics,
  onApprove,
  onEdit,
  onReject
}: {
  candidates: PostCandidate[];
  fabulas: Fabula[];
  matrix: TopicFabulaMatrixEntry[];
  selectedCandidateId: string;
  signals: SourceSignal[];
  topics: Topic[];
  onApprove: (candidate: PostCandidate) => void;
  onEdit: (candidate: PostCandidate, patch: PostCandidateEditPatch) => void;
  onReject: (candidate: PostCandidate) => void;
}) {
  return (
    <>
      {candidates.map((candidate) => (
        <PostCandidateCard
          key={candidate.id}
          candidate={candidate}
          fabula={fabulas.find((fabula) => fabula.id === candidate.fabulaId)}
          fabulas={fabulas}
          isSelected={candidate.id === selectedCandidateId}
          matrix={matrix}
          signal={signals.find((signal) => signal.id === candidate.sourceSignalId)}
          topic={topics.find((topic) => topic.id === candidate.topicId)}
          onApprove={onApprove}
          onEdit={onEdit}
          onReject={onReject}
        />
      ))}
    </>
  );
}
