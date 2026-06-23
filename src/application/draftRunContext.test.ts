import { describe, expect, it } from 'vitest';
import { buildDraftRunContext } from './draftRunContext';
import { createDemoWorkspace } from '../fixtures/demoWorkspace';
import type { WorkspaceState } from '../domain/editorialWorkspace';

describe('buildDraftRunContext', () => {
  it('resolves selected work item to slot, candidate, signal, topic, fabula, rules and evidence', () => {
    const workspace = createWorkspaceWithSelectedWorkItem();

    const context = buildDraftRunContext(workspace);

    expect(context.workItem?.id).toBe('work-item-1');
    expect(context.planSlot?.id).toBe('plan-1');
    expect(context.candidate?.id).toBe('candidate-1');
    expect(context.sourceSignal?.id).toBe(workspace.sourceSignals[0].id);
    expect(context.topic?.id).toBe(workspace.topics[0].id);
    expect(context.fabula?.id).toBe(workspace.fabulas[0].id);
    expect(context.fabula?.researchStrategy).toEqual(workspace.fabulas[0].researchStrategy);
    expect(context.sourceIntentDefaults.sourcesOrigin).toBe('userOverride');
    expect(context.publisherRules.length).toBeGreaterThan(0);
    expect(context.authorPositionEvidence.length).toBeGreaterThan(0);
    expect(context.authorPositionEvidence[0].status).toBe('confirmed');
    expect(context.missingContext).toEqual([]);
  });

  it('reports missing linked entities without throwing', () => {
    const workspace = createWorkspaceWithSelectedWorkItem();
    const broken: WorkspaceState = {
      ...workspace,
      postCandidates: [],
      topics: [],
      fabulas: [],
      sourceSignals: [],
      editorialWorkItems: [
        {
          ...workspace.editorialWorkItems[0],
          postCandidateId: 'missing-candidate',
          sourceSignalId: 'missing-signal',
          topicId: 'missing-topic',
          fabulaId: 'missing-fabula'
        }
      ]
    };

    const context = buildDraftRunContext(broken);

    expect(context.candidate).toBeNull();
    expect(context.sourceSignal).toBeNull();
    expect(context.topic).toBeNull();
    expect(context.fabula).toBeNull();
    expect(context.missingContext.map((item) => item.entity)).toEqual(
      expect.arrayContaining(['postCandidate', 'sourceSignal', 'topic', 'fabula'])
    );
  });
});

function createWorkspaceWithSelectedWorkItem(): WorkspaceState {
  const workspace = createDemoWorkspace();
  const topic = workspace.topics[0];
  const fabula = workspace.fabulas[0];
  const signal = workspace.sourceSignals[0];
  const planSlot = {
    ...workspace.contentPlanItems[0],
    id: 'plan-1',
    sourceSignalId: signal.id,
    topicId: topic.id,
    topicTitle: topic.title,
    fabulaId: fabula.id,
    fabulaTitle: fabula.title,
    approvalStatus: 'approved' as const
  };
  const candidate = {
    id: 'candidate-1',
    sourceSignalId: signal.id,
    topicId: topic.id,
    fabulaId: fabula.id,
    audience: 'AI PM',
    value: 'Explain adoption gap',
    goal: 'Show rollout criteria',
    platform: 'Telegram',
    title: 'AI-B2B demo is not productization',
    thesis: 'Strong demo is not enough for adoption.',
    evidenceSummary: 'Pilot usage does not become regular usage.',
    confidence: 88,
    risks: ['Do not sound anti-prototype'],
    approvalStatus: 'approved' as const
  };
  const brief = {
    id: 'brief-1',
    planItemId: planSlot.id,
    title: candidate.title,
    rubric: topic.title,
    audience: candidate.audience,
    thesis: candidate.thesis,
    conflict: 'Demo looks strong, rollout remains weak.',
    authorPosition: 'Workflow before model choice.',
    evidence: ['Usage does not grow after pilot.'],
    examples: ['No evals'],
    structure: ['Conflict', 'Position'],
    cta: 'Check rollout loop.',
    risks: candidate.risks,
    sources: ['author note'],
    approvalStatus: 'approved' as const,
    topicId: topic.id,
    topicTitle: topic.title,
    fabulaId: fabula.id,
    fabulaTitle: fabula.title
  };
  const confirmedAssertions = workspace.authorPositionAssertions.map((assertion, index) => ({
    ...assertion,
    status: index === 0 ? 'confirmed' as const : assertion.status
  }));

  return {
    ...workspace,
    authorPositionAssertions: confirmedAssertions,
    contentPlanItem: planSlot,
    contentPlanItems: [planSlot],
    postCandidate: candidate,
    postCandidates: [candidate],
    postBrief: brief,
    editorialWorkItems: [
      {
        id: 'work-item-1',
        contentPlanItemId: planSlot.id,
        postCandidateId: candidate.id,
        sourceSignalId: signal.id,
        title: candidate.title,
        platform: 'Telegram',
        date: planSlot.date,
        time: planSlot.time,
        topicId: topic.id,
        topicTitle: topic.title,
        fabulaId: fabula.id,
        fabulaTitle: fabula.title,
        stage: 'brief',
        status: 'inProgress',
        brief,
        draft: null,
        editorialChecks: [],
        editorNotes: [],
        finalText: null,
        visual: null
      }
    ],
    selectedEditorialWorkItemId: 'work-item-1'
  };
}
