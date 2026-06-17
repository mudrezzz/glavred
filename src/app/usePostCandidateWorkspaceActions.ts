import type { PostCandidate, PostCandidateEditPatch } from '../domain/editorialWorkspace';
import {
  buildApproveCandidatePatch,
  buildEditCandidatePatch,
  buildRejectCandidatePatch
} from './postCandidateWorkspacePatches';
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

    setWorkspace((current) => ({
      ...current,
      ...buildApproveCandidatePatch(current, candidate),
      updatedAt: new Date().toISOString()
    }));
    setToast('Кандидат утвержден для сборки инсайта');
  }

  function rejectCandidate(candidate: PostCandidate) {
    setWorkspace((current) => ({
      ...current,
      ...buildRejectCandidatePatch(current, candidate),
      updatedAt: new Date().toISOString()
    }));
    setToast('Кандидат отклонен');
  }

  function editCandidate(candidate: PostCandidate, patch: PostCandidateEditPatch) {
    setWorkspace((current) => ({
      ...current,
      ...buildEditCandidatePatch(current, candidate, patch),
      updatedAt: new Date().toISOString()
    }));
    setToast('Кандидат сохранен');
  }

  return { approveCandidate, editCandidate, rejectCandidate };
}
