import { describe, expect, it, vi } from 'vitest';
import { createPostCandidates, createWorkspaceInsightCard } from '../application/editorialServices';
import { createDemoWorkspace } from '../fixtures/demoWorkspace';
import { usePostCandidateWorkspaceActions } from './usePostCandidateWorkspaceActions';
import type { WorkspaceSetter } from './useWorkspacePersistence';
import type { WorkspaceState } from '../domain/editorialWorkspace';

describe('usePostCandidateWorkspaceActions', () => {
  it('selects a candidate and clears stale downstream artifacts', () => {
    const workspace = createDemoWorkspace();
    const candidate = createPostCandidates(workspace)[0];
    let current: WorkspaceState = {
      ...workspace,
      insightCard: createWorkspaceInsightCard(workspace),
      contentPlanItem: workspace.contentPlanItems[0],
      editorialWorkItems: [{}] as WorkspaceState['editorialWorkItems'],
      selectedEditorialWorkItemId: 'editorial-work-old',
      postBrief: {} as WorkspaceState['postBrief'],
      postDraft: {} as WorkspaceState['postDraft'],
      editorialChecks: [{}] as WorkspaceState['editorialChecks'],
      editorNotes: [{}] as WorkspaceState['editorNotes'],
      finalText: {} as WorkspaceState['finalText'],
      releasePackage: {} as WorkspaceState['releasePackage'],
      editorialLearningNote: {} as WorkspaceState['editorialLearningNote']
    };
    const setWorkspace: WorkspaceSetter = (next) => {
      current = typeof next === 'function' ? next(current) : next;
    };

    const actions = usePostCandidateWorkspaceActions({ setToast: vi.fn(), setWorkspace });
    actions.approveCandidate(candidate);

    expect(current.postCandidate?.id).toBe(candidate.id);
    expect(current.postCandidate?.approvalStatus).toBe('approved');
    expect(current.sourceSignal.id).toBe(candidate.sourceSignalId);
    expect(current.insightCard).toBeNull();
    expect(current.contentPlanItem).toBeNull();
    expect(current.editorialWorkItems).toEqual([]);
    expect(current.selectedEditorialWorkItemId).toBeNull();
    expect(current.postBrief).toBeNull();
    expect(current.postDraft).toBeNull();
    expect(current.editorialChecks).toEqual([]);
    expect(current.editorNotes).toEqual([]);
    expect(current.finalText).toBeNull();
    expect(current.releasePackage).toBeNull();
    expect(current.editorialLearningNote).toBeNull();
  });

  it('rejects and edits candidates without creating downstream artifacts', () => {
    const workspace = createDemoWorkspace();
    const candidate = createPostCandidates(workspace)[0];
    let current: WorkspaceState = {
      ...workspace,
      insightCard: createWorkspaceInsightCard(workspace),
      contentPlanItem: workspace.contentPlanItems[0],
      postCandidates: [candidate],
      postCandidate: candidate
    };
    const setWorkspace: WorkspaceSetter = (next) => {
      current = typeof next === 'function' ? next(current) : next;
    };

    const actions = usePostCandidateWorkspaceActions({ setToast: vi.fn(), setWorkspace });
    actions.editCandidate(candidate, {
      fabulaId: candidate.fabulaId,
      title: 'Edited title',
      thesis: candidate.thesis,
      audience: candidate.audience,
      value: candidate.value,
      goal: candidate.goal,
      platform: candidate.platform,
      evidenceSummary: candidate.evidenceSummary,
      risks: ['Edited risk']
    });

    expect(current.postCandidates[0].title).toBe('Edited title');
    expect(current.postCandidates[0].approvalStatus).toBe('draft');
    expect(current.insightCard).not.toBeNull();
    expect(current.contentPlanItem).not.toBeNull();

    actions.rejectCandidate(current.postCandidates[0]);

    expect(current.postCandidates[0].approvalStatus).toBe('rejected');
    expect(current.postCandidate).toBeNull();
    expect(current.insightCard).not.toBeNull();
    expect(current.contentPlanItem).not.toBeNull();
  });

  it('does not approve a rejected candidate', () => {
    const workspace = createDemoWorkspace();
    const candidate = { ...createPostCandidates(workspace)[0], approvalStatus: 'rejected' as const };
    let current: WorkspaceState = { ...workspace, postCandidates: [candidate], postCandidate: null };
    const setToast = vi.fn();
    const setWorkspace: WorkspaceSetter = (next) => {
      current = typeof next === 'function' ? next(current) : next;
    };

    const actions = usePostCandidateWorkspaceActions({ setToast, setWorkspace });
    actions.approveCandidate(candidate);

    expect(current.postCandidate).toBeNull();
    expect(current.postCandidates[0].approvalStatus).toBe('rejected');
    expect(setToast).toHaveBeenCalledWith('Отклоненный кандидат нельзя утвердить');
  });
});
