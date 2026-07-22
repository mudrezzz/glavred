import type {
  PostCandidate,
  PostCandidateEditPatch,
  RadarDefinition,
  SourceSignal,
  WorkspaceState
} from '../../domain/editorialWorkspace';
import type { BlogProject } from '../../domain/portfolio/types';
import { FoundSignalsTab } from './FoundSignalsTab';
import { PostCandidatesPreviewTab } from './PostCandidatesPreviewTab';
import { RadarsTab } from './RadarsTab';
import { SignalsHeader } from './SignalsHeader';
import { SignalsTabs } from './SignalsTabs';
import { useSignalsController } from './useSignalsController';

export function SignalsView({
  project,
  workspace,
  onSaveRadar,
  onDeleteRadar,
  onRunRadar,
  onToggleRadarStatus,
  onApproveSignal,
  onRejectSignal,
  onArchiveSignal,
  onReopenSignal,
  onRestoreSignal,
  onRescoreSignal,
  onCorrectSignal,
  onApprovePostCandidate,
  onEditPostCandidate,
  onRejectPostCandidate,
  onCreateInsight,
  onPlan
}: {
  project: BlogProject;
  workspace: WorkspaceState;
  onSaveRadar: (radar: RadarDefinition, isNew: boolean) => void;
  onDeleteRadar: (radar: RadarDefinition) => void;
  onRunRadar: (radar: RadarDefinition) => void;
  onToggleRadarStatus: (radar: RadarDefinition) => void;
  onApproveSignal: (signal: SourceSignal) => void;
  onRejectSignal: (signal: SourceSignal) => void;
  onArchiveSignal: (signal: SourceSignal) => void;
  onReopenSignal: (signal: SourceSignal) => void;
  onRestoreSignal: (signal: SourceSignal) => void;
  onRescoreSignal: (signal: SourceSignal) => void;
  onCorrectSignal: (signal: SourceSignal, patch: Partial<SourceSignal>) => void;
  onApprovePostCandidate: (candidate: PostCandidate) => void;
  onEditPostCandidate: (candidate: PostCandidate, patch: PostCandidateEditPatch) => void;
  onRejectPostCandidate: (candidate: PostCandidate) => void;
  onCreateInsight: () => void;
  onPlan: () => void;
}) {
  const controller = useSignalsController({ workspace, onSaveRadar, onCorrectSignal });

  return (
    <div className="page wide signals-page fade-up">
      <SignalsHeader workspace={workspace} signalSummary={controller.signalSummary} />
      <SignalsTabs tab={controller.tab} newCount={controller.signalSummary.new} onChange={controller.setTab} />

      {controller.tab === 'radars' && (
        <RadarsTab
          workspace={workspace}
          controller={controller}
          onDeleteRadar={onDeleteRadar}
          onRunRadar={onRunRadar}
          onToggleRadarStatus={onToggleRadarStatus}
          onCreateInsight={onCreateInsight}
          onPlan={onPlan}
        />
      )}

      {controller.tab === 'signals' && (
        <FoundSignalsTab
          projectId={project.id}
          workspace={workspace}
          controller={controller}
          onApproveSignal={onApproveSignal}
          onRejectSignal={onRejectSignal}
          onArchiveSignal={onArchiveSignal}
          onReopenSignal={onReopenSignal}
          onRestoreSignal={onRestoreSignal}
          onRescoreSignal={onRescoreSignal}
          onCreateInsight={onCreateInsight}
          onPlan={onPlan}
        />
      )}

      {controller.tab === 'candidates' && (
        <PostCandidatesPreviewTab
          workspace={workspace}
          controller={controller}
          onApprovePostCandidate={onApprovePostCandidate}
          onEditPostCandidate={onEditPostCandidate}
          onRejectPostCandidate={onRejectPostCandidate}
          onCreateInsight={onCreateInsight}
          onPlan={onPlan}
        />
      )}
    </div>
  );
}
