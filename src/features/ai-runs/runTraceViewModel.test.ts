import { describe, expect, it } from 'vitest';
import type { RunTraceBundle } from '../../infrastructure/runTraceClient';
import { buildRunTraceViewModel, prettyTraceValue } from './runTraceViewModel';

describe('buildRunTraceViewModel', () => {
  it('builds a DraftRun timeline with child LLM calls', () => {
    const viewModel = buildRunTraceViewModel(makeDraftRunBundle());

    expect(viewModel.mode).toBe('draftRun');
    expect(viewModel.timeline.map((step) => step.key)).toEqual(['context', 'feasibility', 'postContract', 'materialPlan', 'draft']);
    expect(viewModel.timeline[3].childCalls[0].id).toBe('ai-material');
    expect(viewModel.timeline[4].childCalls[0].id).toBe('ai-candidate');
    expect(viewModel.summary.find((field) => field.label === 'LLM calls')?.value).toBe('2');
  });

  it('moves material plan, strategy candidates and selected draft into semantic sections', () => {
    const viewModel = buildRunTraceViewModel(makeDraftRunBundle());
    const titles = viewModel.semanticSections.map((section) => section.title);

    expect(titles).toContain('Material plan');
    expect(titles).toContain('Feasibility report');
    expect(titles).toContain('Post contract');
    expect(titles).toContain('Draft candidate 1');
    expect(titles).toContain('Candidate selection');
    expect(titles).toContain('Selected draft');
  });

  it('keeps a single AiRun trace compatible', () => {
    const viewModel = buildRunTraceViewModel({ kind: 'aiRun', aiRun: makeAiRun('ai-only', 'strategy') });

    expect(viewModel.mode).toBe('aiRun');
    expect(viewModel.timeline[0].childCalls[0].id).toBe('ai-only');
    expect(viewModel.details[0].messages).toHaveLength(2);
  });

  it('pretty prints JSON strings for readable message detail', () => {
    expect(prettyTraceValue('{"brief":{"title":"Debug"}}')).toContain('\n  "brief"');
  });
});

function makeDraftRunBundle(): RunTraceBundle {
  return {
    kind: 'draftRun',
    draftRun: {
      id: 'draft-run',
      status: 'succeeded',
      inputSummary: {},
      steps: [
        {
          key: 'context',
          status: 'succeeded',
          title: 'Context',
          artifactPayload: { workItem: { title: 'Post' } },
          error: null,
          startedAt: null,
          completedAt: null
        },
        {
          key: 'feasibility',
          status: 'succeeded',
          title: 'Feasibility',
          artifactPayload: {
            status: 'feasible_with_constraints',
            summary: 'Can write with constraints',
            findings: [{ detail: 'Use qualified claims' }]
          },
          error: null,
          startedAt: null,
          completedAt: null
        },
        {
          key: 'postContract',
          status: 'succeeded',
          title: 'Post Contract',
          artifactPayload: {
            status: 'created',
            title: 'Post',
            thesis: 'Thesis',
            claims: [{ id: 'signal-summary' }],
            forbiddenMoves: ['Do not invent facts']
          },
          error: null,
          startedAt: null,
          completedAt: null
        },
        {
          key: 'materialPlan',
          status: 'succeeded',
          title: 'Material Plan',
          artifactPayload: { materialPlan: { availableEvidence: ['signal'] } },
          error: null,
          startedAt: null,
          completedAt: null
        },
        {
          key: 'draft',
          status: 'succeeded',
          title: 'Draft',
          artifactPayload: {
            candidates: [{
              id: 'candidate-1',
              title: 'Candidate',
              body: 'Body',
              aiRunId: 'ai-candidate'
            }],
            selection: { selectedCandidateId: 'candidate-1', rationale: 'Best' }
          },
          error: null,
          startedAt: null,
          completedAt: null
        }
      ],
      finalDraft: { title: 'Selected', body: 'Selected body' },
      error: null,
      aiRunIds: ['ai-material', 'ai-candidate'],
      createdAt: '2026-06-19T00:00:00+00:00',
      updatedAt: '2026-06-19T00:00:01+00:00'
    },
    childAiRuns: [makeAiRun('ai-material', 'materialPlan'), makeAiRun('ai-candidate', 'draftCandidate')],
    missingAiRunIds: []
  };
}

function makeAiRun(id: string, step: string) {
  return {
    id,
    capability: 'draftGeneration',
    status: 'succeeded',
    provider: 'openrouter',
    model: 'deepseek/deepseek-v3.2',
    requestPayload: {
      draftRunStep: step,
      providerRequest: {
        messages: [
          { role: 'system', content: 'Return JSON' },
          { role: 'user', content: `${step} payload` }
        ]
      }
    },
    resultPayload: { draftRunStep: step, result: { thesisAngle: 'angle' } },
    error: null,
    fallbackUsed: false,
    createdAt: '2026-06-19T00:00:00+00:00',
    updatedAt: '2026-06-19T00:00:01+00:00'
  };
}
