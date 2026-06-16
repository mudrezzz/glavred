import { approvePostCandidate, editPostCandidate, rejectPostCandidate, replacePostCandidate } from '../domain/editorialWorkspace';
import type { PostCandidate, PostCandidateEditPatch } from '../domain/editorialWorkspace';
import type { WorkspaceSetter } from './useWorkspacePersistence';

type PostCandidateWorkspaceActionsParams = {
  setToast: (message: string) => void;
  setWorkspace: WorkspaceSetter;
};

export function usePostCandidateWorkspaceActions({ setToast, setWorkspace }: PostCandidateWorkspaceActionsParams) {
  function approveCandidate(candidate: PostCandidate) {
    if (candidate.approvalStatus === 'rejected') {
      setToast('Отклоненный кандидат нельзя утвердить');
      return;
    }

    setWorkspace((current) => {
      const postCandidate = approvePostCandidate(candidate);
      const sourceSignal =
        current.sourceSignals.find((signal) => signal.id === postCandidate.sourceSignalId) ?? current.sourceSignal;
      const currentList = current.postCandidates.length > 0 ? current.postCandidates : [candidate];

      return {
        ...current,
        sourceSignal,
        postCandidates: replacePostCandidate(currentList, postCandidate),
        postCandidate,
        insightCard: null,
        contentPlanItem: null,
        postBrief: null,
        postDraft: null,
        editorialChecks: [],
        editorNotes: [],
        finalText: null,
        releasePackage: null,
        editorialLearningNote: null,
        updatedAt: new Date().toISOString()
      };
    });
    setToast('Кандидат утвержден для сборки инсайта');
  }

  function rejectCandidate(candidate: PostCandidate) {
    setWorkspace((current) => {
      const postCandidate = rejectPostCandidate(candidate);
      const selectedCandidate = current.postCandidate?.id === postCandidate.id ? null : current.postCandidate;

      return {
        ...current,
        postCandidates: replacePostCandidate(current.postCandidates, postCandidate),
        postCandidate: selectedCandidate,
        updatedAt: new Date().toISOString()
      };
    });
    setToast('Кандидат отклонен');
  }

  function editCandidate(candidate: PostCandidate, patch: PostCandidateEditPatch) {
    setWorkspace((current) => {
      const postCandidate = editPostCandidate(candidate, patch);
      const selectedCandidate = current.postCandidate?.id === postCandidate.id ? postCandidate : current.postCandidate;

      return {
        ...current,
        postCandidates: replacePostCandidate(current.postCandidates, postCandidate),
        postCandidate: selectedCandidate,
        updatedAt: new Date().toISOString()
      };
    });
    setToast('Кандидат сохранен');
  }

  return { approveCandidate, editCandidate, rejectCandidate };
}
