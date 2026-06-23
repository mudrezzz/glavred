import { describe, expect, it } from 'vitest';
import type { RunTraceBundle } from '../../infrastructure/runTraceClient';
import { buildRunTraceViewModel, prettyTraceValue } from './runTraceViewModel';

describe('buildRunTraceViewModel', () => {
  it('builds a DraftRun timeline with child LLM calls', () => {
    const viewModel = buildRunTraceViewModel(makeDraftRunBundle());

    expect(viewModel.mode).toBe('draftRun');
    expect(viewModel.timeline.map((step) => step.key)).toEqual(['context', 'sourceIntent', 'feasibility', 'postContract', 'rulePack', 'materialPlan', 'rhetoricalPlans', 'draft']);
    expect(viewModel.timeline[1].childCalls[0].id).toBe('ai-source');
    expect(viewModel.timeline[5].childCalls[0].id).toBe('ai-material');
    expect(viewModel.timeline[6].childCalls[0].id).toBe('ai-plans');
    expect(viewModel.timeline[7].childCalls[0].id).toBe('ai-candidate');
    expect(viewModel.timeline[7].childCalls.map((call) => call.title)).toContain('Скоринг кандидатов');
    expect(viewModel.timeline[7].childCalls.map((call) => call.title)).toContain('Выбор итогового драфта');
    expect(viewModel.summary.find((field) => field.label === 'LLM calls')?.value).toBe('4');
  });

  it('expands draft candidates, scoring and selection as readable trace nodes', () => {
    const viewModel = buildRunTraceViewModel(makeDraftRunBundle());
    const draftStep = viewModel.timeline.find((step) => step.key === 'draft');

    expect(draftStep?.childCalls.map((call) => call.title)).toEqual([
      'Draft candidates',
      'Кандидат 1: Candidate · выбран',
      'Кандидат 2: Alternative',
      'Скоринг кандидатов',
      'Выбор итогового драфта'
    ]);
    expect(viewModel.details.find((detail) => detail.id === 'draft-scorecard-detail')?.summary).toEqual(
      expect.arrayContaining([
        expect.objectContaining({ label: 'Selected candidate', value: 'candidate-1' }),
        expect.objectContaining({ label: 'Score spread', value: '+14' })
      ])
    );
    expect(viewModel.details.find((detail) => detail.id === 'draft-scorecard-detail')?.summary).not.toEqual(
      expect.arrayContaining([
        expect.objectContaining({ label: 'Rows' })
      ])
    );
    const scorecardSection = viewModel.semanticSections.find((section) => section.id === 'draft-scorecard');
    expect(scorecardSection?.kind).toBe('scorecard');
    expect(scorecardSection?.scorecard?.rows).toEqual(
      expect.arrayContaining([
        expect.objectContaining({ candidateId: 'candidate-1', selected: true, total: '80', riskPenalty: '-2' }),
        expect.objectContaining({ candidateId: 'candidate-2', selected: false, total: '66', riskPenalty: '-8' })
      ])
    );
    expect(viewModel.details.find((detail) => detail.id === 'draft-selection-detail')?.summary).toEqual(
      expect.arrayContaining([
        expect.objectContaining({ label: 'Selected title', value: 'Candidate' })
      ])
    );
  });

  it('moves material plan, strategy candidates and selected draft into semantic sections', () => {
    const viewModel = buildRunTraceViewModel(makeDraftRunBundle());
    const titles = viewModel.semanticSections.map((section) => section.title);

    expect(titles).toContain('Material plan');
    expect(titles).toContain('Source intent');
    expect(titles).toContain('Research plan');
    expect(titles).toContain('Feasibility report');
    expect(titles).toContain('Post contract');
    expect(titles).toContain('Rule registry');
    expect(titles).toContain('Rhetorical plan 1');
    expect(titles).toContain('Кандидат 1: Candidate · выбран');
    expect(titles).toContain('Draft scorecard');
    expect(titles).toContain('Selected draft candidate');
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
          key: 'sourceIntent',
          status: 'succeeded',
          title: 'Source Intent',
          artifactPayload: {
            sourceIntent: {
              items: [
                { id: 'source-intent-1', kind: 'researchRequest', value: 'мнение лидеров мнений' },
                { id: 'source-intent-2', kind: 'exclusion', value: 'vendor blogs' }
              ]
            },
            researchPlan: {
              researchQuestions: ['What do opinion leaders say?'],
              sourceTargets: ['independent analysts'],
              verificationTasks: [{ kind: 'findPublicSources', instruction: 'Find public commentary' }],
              exclusions: ['vendor blogs']
            }
          },
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
          key: 'rulePack',
          status: 'succeeded',
          title: 'Rule Pack',
          artifactPayload: {
            ruleRegistrySnapshot: {
              version: 'rule-registry-v2',
              metadata: {
                ruleCount: 2,
                bySeverity: { hard: 1, soft: 1 },
                byCategory: { hardConstraints: 1, evidenceRequirements: 1 },
                byValidatorType: { deterministic: 1, llm: 1 },
                feasibilityStatus: 'feasible_with_constraints',
                postContractStatus: 'created'
              },
              rules: [
                {
                  id: 'contract:thesis',
                  title: 'Locked thesis',
                  severity: 'hard',
                  binding: { validatorType: 'deterministic' }
                },
                {
                  id: 'ledger:claim:signal-summary',
                  title: 'Source claim use',
                  severity: 'soft',
                  binding: { validatorType: 'llm' }
                }
              ]
            }
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
          key: 'rhetoricalPlans',
          status: 'succeeded',
          title: 'Rhetorical Plans',
          artifactPayload: {
            rhetoricalPlanSet: {
              plans: [{
                id: 'research',
                title: 'Research route',
                angle: 'Explain through evidence',
                openingMove: 'Start from the signal',
                claimIdsToAvoid: [],
                requiredRuleIds: ['contract:thesis'],
                risks: ['Overclaiming']
              }]
            }
          },
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
              rhetoricalPlanId: 'research',
              title: 'Candidate',
              body: 'Body',
              rationale: 'Best grounded draft',
              source: 'openrouter',
              fallbackUsed: false,
              aiRunId: 'ai-candidate'
            }, {
              id: 'candidate-2',
              rhetoricalPlanId: 'contrast',
              title: 'Alternative',
              body: 'Alternative body',
              rationale: 'Sharper but riskier',
              risks: ['overclaiming'],
              source: 'openrouter',
              fallbackUsed: false,
              aiRunId: null
            }],
            selection: {
              selectedCandidateId: 'candidate-1',
              reason: 'Best',
              scorecard: [
                {
                  candidateId: 'candidate-1',
                  hardConstraintFit: 20,
                  evidenceGrounding: 20,
                  topicFit: 15,
                  fabulaFit: 15,
                  audienceValue: 12,
                  riskPenalty: 2,
                  total: 80
                },
                {
                  candidateId: 'candidate-2',
                  hardConstraintFit: 19,
                  evidenceGrounding: 16,
                  topicFit: 15,
                  fabulaFit: 12,
                  audienceValue: 12,
                  riskPenalty: 8,
                  total: 66
                }
              ],
              unresolvedRisks: []
            }
          },
          error: null,
          startedAt: null,
          completedAt: null
        }
      ],
      finalDraft: { title: 'Selected', body: 'Selected body' },
      error: null,
      aiRunIds: ['ai-source', 'ai-material', 'ai-plans', 'ai-candidate'],
      createdAt: '2026-06-19T00:00:00+00:00',
      updatedAt: '2026-06-19T00:00:01+00:00'
    },
    childAiRuns: [
      makeAiRun('ai-source', 'sourceIntentResearchPlan'),
      makeAiRun('ai-material', 'materialPlan'),
      makeAiRun('ai-plans', 'rhetoricalPlans'),
      makeAiRun('ai-candidate', 'draftCandidate')
    ],
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
