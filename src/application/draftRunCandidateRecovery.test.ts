import { describe, expect, it } from 'vitest';
import { createEditorialWorkItem, type ContentPlanItem, type PostCandidate, type WorkspaceState } from '../domain/editorialWorkspace';
import { createDemoWorkspace } from '../fixtures/demoWorkspace';
import { buildDraftRunContext } from './draftRunContext';

describe('DraftRun candidate recovery', () => {
  it('recovers approved candidate by source signal, topic and fabula', () => {
    const { workspace, candidate } = createWorkspaceWithCandidateLink({ withPostCandidateId: false });

    const context = buildDraftRunContext(workspace);

    expect(context.candidate?.id).toBe(candidate.id);
    expect(context.workItem?.postCandidateId).toBeNull();
    expect(context.missingContext).toEqual([]);
  });

  it('does not guess when several approved candidates match the same signal', () => {
    const { workspace, candidate, planSlot } = createWorkspaceWithCandidateLink({ withPostCandidateId: false });
    const ambiguous: PostCandidate = {
      ...candidate,
      id: 'candidate-ambiguous',
      topicId: 'another-topic',
      fabulaId: 'another-fabula'
    };
    const context = buildDraftRunContext({
      ...workspace,
      contentPlanItems: [{ ...planSlot, topicId: undefined, fabulaId: undefined }],
      contentPlanItem: { ...planSlot, topicId: undefined, fabulaId: undefined },
      editorialWorkItems: [{ ...workspace.editorialWorkItems[0], topicId: undefined, fabulaId: undefined }],
      postCandidates: [candidate, ambiguous]
    });

    expect(context.candidate).toBeNull();
    expect(context.missingContext).toEqual([
      expect.objectContaining({ entity: 'postCandidate', reason: 'Multiple approved candidates match source signal' })
    ]);
  });
});

function createWorkspaceWithCandidateLink(options: { withPostCandidateId: boolean }): {
  workspace: WorkspaceState;
  candidate: PostCandidate;
  planSlot: ContentPlanItem;
} {
  const workspace = createDemoWorkspace();
  const signal = workspace.sourceSignals[0];
  const topic = workspace.topics[0];
  const fabula = workspace.fabulas[0];
  const candidate: PostCandidate = {
    id: 'candidate-recovered',
    sourceSignalId: signal.id,
    topicId: topic.id,
    fabulaId: fabula.id,
    audience: 'AI PM',
    value: 'Показать разрыв между demo и adoption',
    goal: 'Собрать аудиторию AI product builders',
    platform: 'Telegram',
    title: 'AI-B2B demo не равно продукт',
    thesis: 'Сильное demo не доказывает adoption.',
    evidenceSummary: 'После пилота usage не становится регулярным.',
    confidence: 88,
    risks: ['Не звучать противником прототипов'],
    approvalStatus: 'approved'
  };
  const planSlot: ContentPlanItem = {
    id: 'slot-recovered',
    insightId: 'insight-missing-link',
    title: candidate.title,
    platform: 'Telegram',
    date: '2026-06-22',
    time: '10:00',
    priority: 'high',
    format: 'research',
    expectedEffect: 'Проверить adoption gap',
    approvalStatus: 'approved',
    sourceSignalId: signal.id,
    topicId: topic.id,
    topicTitle: topic.title,
    fabulaId: fabula.id,
    fabulaTitle: fabula.title
  };
  const workItem = createEditorialWorkItem(
    planSlot,
    { brief: null },
    options.withPostCandidateId ? candidate.id : undefined
  );
  return {
    workspace: {
      ...workspace,
      contentPlanItem: planSlot,
      contentPlanItems: [planSlot],
      postCandidate: null,
      postCandidates: [candidate],
      editorialWorkItems: [workItem],
      selectedEditorialWorkItemId: workItem.id
    },
    candidate,
    planSlot
  };
}
