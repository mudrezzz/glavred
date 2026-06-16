import type { PostCandidate, PostCandidateEditPatch, WorkspaceState } from '../../domain/editorialWorkspace';
import { PostCandidateGroupList, PostCandidateRows } from './PostCandidateGroupList';
import { PostCandidatesToolbar } from './PostCandidatesToolbar';
import { SignalsSidePanel } from './SignalsSidePanel';
import type { SignalsController } from './useSignalsController';
import { usePostCandidatesController } from './usePostCandidatesController';

export function PostCandidatesPreviewTab({
  workspace,
  controller,
  onApprovePostCandidate,
  onEditPostCandidate,
  onRejectPostCandidate,
  onCreateInsight,
  onPlan
}: {
  workspace: WorkspaceState;
  controller: SignalsController;
  onApprovePostCandidate: (candidate: PostCandidate) => void;
  onEditPostCandidate: (candidate: PostCandidate, patch: PostCandidateEditPatch) => void;
  onRejectPostCandidate: (candidate: PostCandidate) => void;
  onCreateInsight: () => void;
  onPlan: () => void;
}) {
  const candidatesController = usePostCandidatesController(workspace);
  const approvedSignals = workspace.sourceSignals.filter((signal) => signal.reviewStatus === 'approved');

  return (
    <div className="memory-grid signals-workspace-grid">
      <section className="memory-main">
        <PostCandidatesToolbar
          filters={candidatesController.filters}
          groupMode={candidatesController.groupMode}
          signals={approvedSignals}
          topics={workspace.topics}
          viewMode={candidatesController.viewMode}
          onChangeFilters={candidatesController.setFilters}
          onChangeGroupMode={candidatesController.setGroupMode}
          onChangeViewMode={candidatesController.setViewMode}
        />

        <div className="card post-candidates-list">
          {candidatesController.candidates.length === 0 ? (
            <div className="empty-state">
              Сначала утвердите подходящий сигнал во вкладке «Найденные сигналы». После этого здесь появятся варианты поста.
            </div>
          ) : candidatesController.filteredCandidates.length === 0 ? (
            <div className="empty-state">По текущим фильтрам кандидатов нет.</div>
          ) : candidatesController.viewMode === 'groups' ? (
            <PostCandidateGroupList
              fabulas={workspace.fabulas}
              groups={candidatesController.groups}
              selectedCandidateId={candidatesController.selectedCandidateId}
              signals={workspace.sourceSignals}
              topics={workspace.topics}
              onApprove={onApprovePostCandidate}
              onEdit={onEditPostCandidate}
              onReject={onRejectPostCandidate}
            />
          ) : (
            <PostCandidateRows
              candidates={candidatesController.filteredCandidates}
              fabulas={workspace.fabulas}
              selectedCandidateId={candidatesController.selectedCandidateId}
              signals={workspace.sourceSignals}
              topics={workspace.topics}
              onApprove={onApprovePostCandidate}
              onEdit={onEditPostCandidate}
              onReject={onRejectPostCandidate}
            />
          )}
        </div>
      </section>

      <SignalsSidePanel workspace={workspace} summary={controller.signalSummary} onCreateInsight={onCreateInsight} onPlan={onPlan} />
    </div>
  );
}
