import { describe, expect, it } from 'vitest';
import type { RunTraceBundle } from '../../infrastructure/runTraceClient';
import { buildRunTraceViewModel, prettyTraceValue } from './runTraceViewModel';

describe('buildRunTraceViewModel', () => {
  it('builds a DraftRun timeline with child LLM calls', () => {
    const viewModel = buildRunTraceViewModel(makeDraftRunBundle());

    expect(viewModel.mode).toBe('draftRun');
    expect(viewModel.timeline.map((step) => step.key)).toEqual(['context', 'sourceIntent', 'publicEvidence', 'feasibility', 'postContract', 'rulePack', 'materialPlan', 'rhetoricalPlans', 'draft', 'validation']);
    expect(traceStep(viewModel, 'sourceIntent')?.childCalls[0].id).toBe('ai-source');
    expect(traceStep(viewModel, 'materialPlan')?.childCalls[0].id).toBe('ai-material');
    expect(traceStep(viewModel, 'rhetoricalPlans')?.childCalls[0].id).toBe('ai-plans');
    expect(traceStep(viewModel, 'draft')?.childCalls[0].id).toBe('ai-candidate');
    expect(traceStep(viewModel, 'validation')?.childCalls[0].id).toBe('ai-validation-1');
    expect(traceStep(viewModel, 'validation')?.childCalls.map((call) => call.id)).toContain('ai-critic-1');
    expect(traceStep(viewModel, 'validation')?.childCalls.map((call) => call.id)).toContain('ai-alt-route');
    expect(traceStep(viewModel, 'validation')?.childCalls.map((call) => call.id)).toContain('ai-alt-candidate');
    expect(traceStep(viewModel, 'draft')?.childCalls[0].meta).toContainEqual({ label: 'Model role', value: 'writer' });
    expect(traceStep(viewModel, 'validation')?.childCalls[0].meta).toContainEqual({ label: 'Selection source', value: 'role' });
    expect(traceStep(viewModel, 'draft')!.childCalls.map((call) => call.title)).toContain('Скоринг кандидатов');
    expect(traceStep(viewModel, 'draft')!.childCalls.map((call) => call.title)).toContain('Выбор итогового драфта');
    expect(traceStep(viewModel, 'draft')?.operations[0]).toEqual(expect.objectContaining({
      kind: 'draftCandidate',
      label: 'Generate candidate: research',
      status: 'succeeded',
      aiRunId: 'ai-candidate'
    }));
    expect(viewModel.summary.find((field) => field.label === 'LLM calls')?.value).toBe('14');
  });

  it('expands draft candidates, scoring and selection as readable trace nodes', () => {
    const viewModel = buildRunTraceViewModel(makeDraftRunBundle());
    const draftStep = viewModel.timeline.find((step) => step.key === 'draft');

    expect(draftStep?.childCalls.map((call) => call.title)).toEqual([
      'Draft candidate',
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
        expect.objectContaining({ candidateId: 'candidate-1', selected: true, selectionStatus: 'eligible', total: '80', riskPenalty: '-2' }),
        expect.objectContaining({ candidateId: 'candidate-2', selected: false, selectionStatus: 'excluded', selectionPenalty: '500', total: '66', riskPenalty: '-8' })
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
    expect(titles).toContain('Public evidence');
    expect(titles).toContain('Feasibility report');
    expect(titles).toContain('Post contract');
    expect(titles).toContain('Rule registry');
    expect(titles).toContain('Rhetorical plan attempts');
    expect(titles).toContain('Rhetorical plan 1');
    expect(titles).toContain('Кандидат 1: Candidate · выбран');
    expect(titles).toContain('Draft scorecard');
    expect(titles).toContain('Validation report');
    expect(titles).toContain('Editorial critique');
    expect(titles).toContain('Alternative angle tournament');
    expect(titles).toContain('Selected draft candidate');
    expect(titles).toContain('Selected draft');
  });

  it('shows deterministic validation findings as readable semantic trace', () => {
    const viewModel = buildRunTraceViewModel(makeDraftRunBundle());
    const validation = viewModel.semanticSections.find((section) => section.id === 'validation');

    expect(validation?.fields).toContainEqual({ label: 'Status', value: 'warning' });
    expect(validation?.fields).toContainEqual({ label: 'Critical findings', value: '0' });
    expect(validation?.fields.find((field) => field.label === 'Candidate quality')?.value).toContain('candidate-1: warning');
    expect(validation?.fields.find((field) => field.label === 'Source attribution findings')?.value).toContain('Source-backed public claim needs visible attribution');
    expect(validation?.fields.find((field) => field.label === 'Attribution markers')?.value).toContain('expected: external-claim-1: Tian Pan, tianpan.co');
    expect(validation?.fields.find((field) => field.label === 'LLM validation attempts')?.value).toContain('candidate-1 · primary: accepted');
    expect(validation?.fields.find((field) => field.label === 'LLM actionable findings')?.value).toContain('llm.audience-value');
    expect(validation?.fields.find((field) => field.label === 'LLM observations')?.value).toContain('llm.coherence');
  });

  it('shows editorial critique separately from validation findings', () => {
    const viewModel = buildRunTraceViewModel(makeDraftRunBundle());
    const critique = viewModel.semanticSections.find((section) => section.id === 'editorial-critique');

    expect(critique?.fields).toContainEqual({ label: 'Status', value: 'warning' });
    expect(critique?.fields.find((field) => field.label === 'Candidate risks')?.value).toContain('risk high');
    expect(critique?.fields.find((field) => field.label === 'Actionable critique')?.value).toContain('critic.genericAiProse');
    expect(critique?.fields.find((field) => field.label === 'Editorial observations')?.value).toContain('critic.tension');
    expect(critique?.fields.find((field) => field.label === 'Attempts')?.value).toContain('candidate-1 - primary: accepted');
  });

  it('shows alternative angle tournament as readable semantic trace', () => {
    const viewModel = buildRunTraceViewModel(makeDraftRunBundle());
    const tournament = viewModel.semanticSections.find((section) => section.id === 'alternative-angle-tournament');

    expect(tournament?.fields).toContainEqual({ label: 'Status', value: 'succeeded' });
    expect(tournament?.fields.find((field) => field.label === 'Why different')?.value).toContain('attacks the generic opening');
    expect(tournament?.fields.find((field) => field.label === 'Candidate')?.value).toBe('alternative-angle-1-brief-demo');
    expect(tournament?.fields.find((field) => field.label === 'Attempts')?.value).toContain('primary');
  });

  it('shows pairwise ranking and directed revision as validation semantic trace', () => {
    const viewModel = buildRunTraceViewModel(makeDraftRunBundle());
    const titles = viewModel.semanticSections.map((section) => section.title);

    expect(titles).toContain('Pairwise ranking');
    expect(titles).toContain('Revision loop');
    expect(titles).toContain('Directed revision');
    expect(titles).toContain('Revision regression');
    expect(titles).toContain('Final quality gate');
    expect(titles).toContain('Final draft decision');
    expect(viewModel.semanticSections.find((section) => section.id === 'revision-loop')?.fields).toContainEqual({ label: 'Stop reason', value: 'quality-threshold' });
    expect(viewModel.semanticSections.find((section) => section.id === 'revision-loop')?.fields.find((field) => field.label === 'Cycles')?.value).toContain('cycle 1');
    expect(viewModel.semanticSections.find((section) => section.id === 'revision-loop')?.fields.find((field) => field.label === 'Editorial goals')?.value).toContain('readerValue');
    expect(viewModel.semanticSections.find((section) => section.id === 'revision-loop')?.fields.find((field) => field.label === 'Editorial dimension scores')?.value).toContain('revised-candidate-1');
    expect(viewModel.semanticSections.find((section) => section.id === 'revision-loop')?.fields.find((field) => field.label === 'Rejected moves')?.value).toContain('Do not shorten below previous best');
    expect(viewModel.semanticSections.find((section) => section.id === 'pairwise-ranking')?.fields.find((field) => field.label === 'Comparisons')?.value).toContain('candidate-1 vs candidate-2 -> candidate-1');
    expect(viewModel.semanticSections.find((section) => section.id === 'directed-revision')?.fields.find((field) => field.label === 'Candidate')?.value).toBe('candidate-1');
    expect(viewModel.semanticSections.find((section) => section.id === 'revision-regression')?.fields.find((field) => field.label === 'Accepted')?.value).toBe('true');
    expect(viewModel.semanticSections.find((section) => section.id === 'final-quality-gate')?.fields.find((field) => field.label === 'Public prose')?.value).toBe('warning');
    expect(viewModel.semanticSections.find((section) => section.id === 'final-quality-gate')?.fields.find((field) => field.label === 'Contract')?.value).toContain('depth deep');
    expect(viewModel.semanticSections.find((section) => section.id === 'final-quality-gate')?.fields.find((field) => field.label === 'Independent review status')?.value).toBe('warning');
    expect(viewModel.semanticSections.find((section) => section.id === 'final-quality-gate')?.fields.find((field) => field.label === 'Independent attempts')?.value).toContain('primary');
    expect(viewModel.semanticSections.find((section) => section.id === 'final-quality-gate')?.fields.find((field) => field.label === 'Attribution review')?.value).toContain('diagnostic closed');
    expect(viewModel.semanticSections.find((section) => section.id === 'final-quality-gate')?.fields.find((field) => field.label === 'Diagnostic attribution noise')?.value).toContain('empty-attribution-markers');
    expect(viewModel.semanticSections.find((section) => section.id === 'final-quality-gate')?.fields.find((field) => field.label === 'Repair goals')?.value).toContain('reader-facing prose');
    expect(viewModel.semanticSections.find((section) => section.id === 'final-quality-gate')?.fields.find((field) => field.label === 'Repair cycles')?.value).toContain('cycle 1');
    expect(viewModel.semanticSections.find((section) => section.id === 'ranking-final-decision')?.fields).toContainEqual({ label: 'Source', value: 'revisionLoop' });
  });

  it('shows rhetorical plan retry attempts in semantic trace', () => {
    const viewModel = buildRunTraceViewModel(makeDraftRunBundle());
    const attempts = viewModel.semanticSections.find((section) => section.id === 'rhetorical-plan-attempts');

    expect(attempts?.fields.find((field) => field.label === 'Attempts')?.value).toContain('primary: error');
    expect(attempts?.fields.find((field) => field.label === 'Attempts')?.value).toContain('backup: accepted');
    expect(attempts?.fields.find((field) => field.label === 'Attempts')?.value).toContain('backup');
  });

  it('shows material plan evidence accountability and retry attempts', () => {
    const viewModel = buildRunTraceViewModel(makeDraftRunBundle());
    const materialPlan = viewModel.semanticSections.find((section) => section.id === 'materialPlan');

    expect(materialPlan?.fields.find((field) => field.label === 'Attempts')?.value).toContain('primary: rejected');
    expect(materialPlan?.fields.find((field) => field.label === 'Attempts')?.value).toContain('primary-repair: accepted');
    expect(materialPlan?.fields.find((field) => field.label === 'Usable evidence candidates')?.value).toContain('external-claim-1');
    expect(materialPlan?.fields.find((field) => field.label === 'Rejected evidence')?.value).toContain('weak-claim');
    expect(materialPlan?.fields.find((field) => field.label === 'Claims requiring attribution')?.value).toContain('external-claim-1');
    expect(materialPlan?.fields.find((field) => field.label === 'Accountability')?.value).toContain('valid: true');
  });

  it('keeps a single AiRun trace compatible', () => {
    const viewModel = buildRunTraceViewModel({ kind: 'aiRun', aiRun: makeAiRun('ai-only', 'strategy') });

    expect(viewModel.mode).toBe('aiRun');
    expect(viewModel.timeline[0].childCalls[0].id).toBe('ai-only');
    expect(viewModel.summary).toContainEqual({ label: 'Model role', value: 'strategy' });
    expect(viewModel.details[0].messages).toHaveLength(2);
  });

  it('pretty prints JSON strings for readable message detail', () => {
    expect(prettyTraceValue('{"brief":{"title":"Debug"}}')).toContain('\n  "brief"');
  });

  it('shows source origin in source intent semantic section', () => {
    const viewModel = buildRunTraceViewModel(makeDraftRunBundle());
    const sourceIntent = viewModel.semanticSections.find((section) => section.id === 'sourceIntent');

    expect(sourceIntent?.fields).toContainEqual({ label: 'Sources origin', value: 'fabulaManual' });
  });

  it('shows public evidence attempts and skipped search tasks', () => {
    const viewModel = buildRunTraceViewModel(makeDraftRunBundle());
    const publicEvidence = viewModel.semanticSections.find((section) => section.id === 'publicEvidence');
    const budget = viewModel.semanticSections.find((section) => section.id === 'draftRunBudget');

    expect(budget?.fields).toContainEqual({ label: 'Research depth', value: 'marketResearch' });
    expect(budget?.fields.find((field) => field.label === 'Caps')?.value).toContain('maxSearchTasks: 8');
    expect(publicEvidence?.fields).toContainEqual({ label: 'Evidence items', value: '1' });
    expect(publicEvidence?.fields).toContainEqual({ label: 'External ledger claims', value: '1' });
    expect(publicEvidence?.fields).toContainEqual({ label: 'Synthesis external claims', value: '1' });
    expect(publicEvidence?.fields.find((field) => field.label === 'Attempts')?.value).toContain('readUrl: succeeded');
    expect(publicEvidence?.fields.find((field) => field.label === 'Attempts')?.value).toContain('search: succeeded');
    expect(publicEvidence?.fields.find((field) => field.label === 'Attempts')?.value).toContain('query: Find public commentary about AI product trust');
    expect(publicEvidence?.fields.find((field) => field.label === 'Extracted evidence')?.value).toContain('Independent report');
    expect(publicEvidence?.fields.find((field) => field.label === 'Rejected citations')?.value).toContain('TARGET Services');
    expect(publicEvidence?.fields.find((field) => field.label === 'Search AiRun IDs')?.value).toContain('search-run-1');
    const publicEvidenceStep = viewModel.timeline.find((step) => step.key === 'publicEvidence');
    expect(publicEvidenceStep?.childCalls.map((call) => call.id)).toContain('search-run-1');
    expect(publicEvidenceStep?.childCalls.map((call) => call.id)).toContain('synthesis-run-1');
    const searchDetail = viewModel.details.find((detail) => detail.id === 'ai-detail-search-run-1');
    expect(searchDetail?.sections[0].fields).toContainEqual({ label: 'Built query', value: 'Find public commentary about AI product trust' });
    expect(searchDetail?.sections[0].fields.find((field) => field.label === 'Rejected citations')?.value).toContain('TARGET Services');
  });

  it('shows evidence synthesis and enriched ledger as readable semantic sections', () => {
    const viewModel = buildRunTraceViewModel(makeDraftRunBundle());
    const synthesis = viewModel.semanticSections.find((section) => section.id === 'evidenceSynthesis');
    const ledger = viewModel.semanticSections.find((section) => section.id === 'sourceLedger');

    expect(synthesis?.fields).toContainEqual({ label: 'Claim count', value: '1' });
    expect(synthesis?.fields.find((field) => field.label === 'External claims')?.value).toContain('public-evidence-url-task-1');
    expect(ledger?.title).toBe('Enriched source ledger');
    expect(ledger?.fields).toContainEqual({ label: 'External claims', value: '1' });
    expect(ledger?.fields.find((field) => field.label === 'External claim list')?.value).toContain('Independent report');
  });

  it('shows evidence interpretation as readable semantic trace', () => {
    const viewModel = buildRunTraceViewModel(makeDraftRunBundle());
    const interpretation = viewModel.semanticSections.find((section) => section.id === 'evidenceInterpretation');
    const childDetail = viewModel.details.find((detail) => detail.id === 'ai-detail-ai-interpretation');

    expect(interpretation?.fields.find((field) => field.label === 'Implications')?.value).toContain('Workflow proof');
    expect(interpretation?.fields.find((field) => field.label === 'Limits')?.value).toContain('Do not overclaim');
    expect(interpretation?.fields.find((field) => field.label === 'Forbidden overclaims')?.value).toContain('No universal claim');
    expect(childDetail?.sections.find((section) => section.id === 'evidenceInterpretation')?.fields.find((field) => field.label === 'Implications')?.value).toContain('Workflow proof');
  });

  it('shows article dossier and role context packs in DraftRun and child AiRun traces', () => {
    const viewModel = buildRunTraceViewModel(makeDraftRunBundle());
    const dossier = viewModel.semanticSections.find((section) => section.id === 'article-dossier');
    const packs = viewModel.semanticSections.find((section) => section.id === 'context-packs');
    const candidateDetail = viewModel.details.find((detail) => detail.id === 'ai-detail-ai-candidate');

    expect(dossier?.fields).toContainEqual({ label: 'Cards', value: '2' });
    expect(dossier?.fields.find((field) => field.label === 'Key cards')?.value).toContain('Signal claim');
    expect(packs?.fields.find((field) => field.label === 'Roles')?.value).toContain('writer: 2 items');
    expect(candidateDetail?.sections.find((section) => section.id === 'context-packs')?.fields.find((field) => field.label === 'Roles')?.value).toContain('writer: 2 items');
    expect(viewModel.details.find((detail) => detail.id === 'ai-detail-ai-material')?.sections.find((section) => section.id === 'context-packs')?.fields.find((field) => field.label === 'Roles')?.value).toContain('strategy: 1 items');
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
          artifactPayload: { workItem: { title: 'Post' }, draftRunBudget: draftRunBudgetFixture() },
          error: null,
          startedAt: null,
          completedAt: null
        },
        {
          key: 'sourceIntent',
          status: 'succeeded',
          title: 'Source Intent',
          artifactPayload: {
            sourcesOrigin: 'fabulaManual',
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
          key: 'publicEvidence',
          status: 'succeeded',
          title: 'Public Evidence',
          artifactPayload: {
            source: 'publicEvidenceRetrievalV1',
            attempts: [
              {
                id: 'url-task-1',
                kind: 'readUrl',
                target: 'https://example.com/report',
                status: 'succeeded'
              },
              {
                id: 'search-task-2',
                kind: 'search',
                target: 'target-1',
                status: 'succeeded',
                metadata: {
                  builtQuery: 'Find public commentary about AI product trust',
                  rejectedCitations: [{
                    title: 'TARGET Services',
                    url: 'https://example.com/target',
                    reason: 'search-result-drift'
                  }]
                }
              }
            ],
            items: [
              {
                id: 'public-evidence-url-task-1',
                sourceTitle: 'Independent report',
                sourceUrl: 'https://example.com/report',
                snippet: 'Adoption depends on workflow integration.',
                allowedUse: 'needsQualification'
              }
            ],
            warnings: [],
            metadata: { searchProvider: 'openrouter:web_search', model: 'test-model', budgetTrace: { draftRunBudget: draftRunBudgetFixture(), budgetSkipped: [], usedCounts: { searchTasks: 1 }, capHits: { searchTasks: false } } },
            aiRunIds: ['search-run-1'],
            articleDossier: articleDossierFixture(),
            contextPacks: contextPacksFixture(),
            evidenceSynthesis: {
              source: 'openrouter',
              externalClaims: [{
                publicEvidenceItemId: 'public-evidence-url-task-1',
                statement: 'Independent report qualifies AI trust and adoption claims.',
                allowedUse: 'needsQualification',
                confidence: 'medium'
              }],
              warnings: [],
              metadata: { externalClaimCount: 1, warningCount: 0 }
            },
            enrichedSourceLedger: {
              claims: [{
                id: 'external-evidence-public-evidence-url-task-1',
                type: 'externalEvidenceClaim',
                statement: 'Independent report qualifies AI trust and adoption claims.',
                allowedUse: 'needsQualification',
                provenance: { sourceTitle: 'Independent report', sourceUrl: 'https://example.com/report' }
              }],
              warnings: [],
              metadata: { claimCount: 1, internalClaimCount: 0, externalClaimCount: 1, warningCount: 0 }
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
            source: 'openrouter',
            aiRunId: 'ai-interpretation',
            fallbackUsed: false,
            attempts: [{ label: 'primary', model: 'deepseek/deepseek-v3.2', status: 'accepted', aiRunId: 'ai-interpretation' }],
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
            },
            evidenceInterpretation: evidenceInterpretationFixture()
          },
          error: null,
          startedAt: null,
          completedAt: null
        },
        {
          key: 'materialPlan',
          status: 'succeeded',
          title: 'Material Plan',
          artifactPayload: {
            source: 'openrouter',
            attempts: [
              {
                label: 'primary',
                model: 'deepseek/deepseek-v3.2',
                status: 'rejected',
                aiRunId: 'ai-material-1',
                validation: {
                  valid: false,
                  invalidReasons: ['materialPlan ignored usable evidence candidates without enough rejection reasons']
                }
              },
              {
                label: 'primary-repair',
                model: 'deepseek/deepseek-v3.2',
                status: 'accepted',
                aiRunId: 'ai-material',
                validation: { valid: true, invalidReasons: [] }
              }
            ],
            usableEvidenceCandidates: [{
              claimId: 'external-claim-1',
              statement: 'Independent report qualifies AI trust and adoption claims.',
              allowedUse: 'needsQualification',
              sourceTitle: 'Independent report'
            }],
            evidenceAccountability: {
              valid: true,
              acceptedEvidence: ['external-claim-1'],
              rejectedEvidence: ['weak-claim'],
              rejectionReasons: ['weak-claim is only framing'],
              claimsRequiringAttribution: ['external-claim-1'],
              qualifiedClaims: ['external-claim-1']
            },
            materialPlan: {
              availableEvidence: ['external-claim-1'],
              rejectedEvidence: ['weak-claim'],
              rejectionReasons: ['weak-claim is only framing'],
              claimsRequiringAttribution: ['external-claim-1'],
              qualifiedClaims: ['external-claim-1']
            }
          },
          error: null,
          startedAt: null,
          completedAt: null
        },
        {
          key: 'rhetoricalPlans',
          status: 'succeeded',
          title: 'Rhetorical Plans',
          artifactPayload: {
            source: 'openrouter',
            fallbackUsed: false,
            attempts: [
              { label: 'primary', model: 'deepseek/deepseek-v3.2', status: 'error', aiRunId: 'ai-plans-primary', backup: false, validation: 'ValueError: JSON is not an object' },
              { label: 'backup', model: 'openai/gpt-4.1-mini', status: 'accepted', aiRunId: 'ai-plans', backup: true }
            ],
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
            progress: {
              status: 'succeeded',
              currentOperationId: null,
              operations: [{
                id: 'draft-candidate-research',
                kind: 'draftCandidate',
                label: 'Generate candidate: research',
                status: 'succeeded',
                startedAt: '2026-06-19T00:00:00+00:00',
                completedAt: '2026-06-19T00:00:01+00:00',
                aiRunId: 'ai-candidate',
                target: 'research'
              }]
            },
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
                  publishable: true,
                  selectionStatus: 'eligible',
                  selectionPenalty: 0,
                  selectionReasons: [],
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
                  publishable: false,
                  selectionStatus: 'excluded',
                  selectionPenalty: 500,
                  selectionReasons: ['fallback-candidate-provider-alternative'],
                  total: 66
                }
              ],
              unresolvedRisks: []
            }
          },
          error: null,
          startedAt: null,
          completedAt: null
        },
        {
          key: 'validation',
          status: 'succeeded',
          title: 'Validation',
          artifactPayload: {
            status: 'warning',
            selectedCandidateId: 'candidate-1',
            summary: {
              candidateCount: 2,
              criticalCount: 0,
              warningCount: 1,
              selectedStatus: 'warning'
            },
            candidateReports: [
              {
                candidateId: 'candidate-1',
                selected: true,
                status: 'warning',
                criticalCount: 0,
                warningCount: 1,
                findings: [
                  {
                    validatorId: 'evidence.attribution',
                    severity: 'warning',
                    candidateId: 'candidate-1',
                    ruleIds: [],
                    claimIds: ['external-claim-1'],
                    message: 'Source-backed public claim needs visible attribution.',
                    evidenceExcerpt: 'external-claim-1',
                    repairGuidance: 'Name the source.',
                    metadata: {
                      expectedAttributionMarkers: { 'external-claim-1': ['Tian Pan', 'tianpan.co'] },
                      matchedAttributionMarkers: {},
                      matchedClaimIds: [],
                      missingClaimIds: ['external-claim-1']
                    }
                  }
                ]
              },
              {
                candidateId: 'candidate-2',
                selected: false,
                status: 'passed',
                criticalCount: 0,
                warningCount: 0,
                findings: []
              }
            ],
            metadata: { version: 'draft-validation-v1', reportOnly: true },
            llmValidationReport: {
              status: 'warning',
              summary: { candidateCount: 1, criticalCount: 0, warningCount: 1, observationCount: 1 },
              candidateReports: [
                {
                  candidateId: 'candidate-1',
                  status: 'warning',
                  criticalCount: 0,
                  warningCount: 1,
                  observationCount: 1,
                  attempts: [
                    {
                      label: 'primary',
                      model: 'test-model',
                      status: 'accepted',
                      candidateId: 'candidate-1',
                      aiRunId: 'ai-validation-1',
                      backup: false
                    }
                  ],
                  findings: [
                    {
                      validatorId: 'llm.audience-value',
                      severity: 'warning',
                      candidateId: 'candidate-1',
                      ruleIds: ['rule-audience'],
                      claimIds: [],
                      message: 'Audience value is too implicit.',
                      evidenceExcerpt: 'Selected body',
                      repairGuidance: 'Make the reader value explicit.',
                      metadata: {}
                    }
                  ],
                  observations: [
                    {
                      validatorId: 'llm.coherence',
                      candidateId: 'candidate-1',
                      message: 'The draft is coherent.',
                      repairGuidance: 'No repair needed',
                      metadata: {}
                    }
                  ]
                }
              ],
              metadata: { version: 'llm-draft-validation-v1', reportOnly: true }
            },
            editorialCritiqueReport: {
              status: 'warning',
              summary: { candidateCount: 1, findingCount: 1, observationCount: 1, highRiskCandidateCount: 1 },
              candidateReports: [
                {
                  candidateId: 'candidate-1',
                  status: 'warning',
                  editorialRisk: 'high',
                  overallJudgment: 'Safe but generic.',
                  strongestMove: 'Workflow framing.',
                  weakestMove: 'Sounds like generic AI prose.',
                  recommendedEditorialMove: 'Open with the uncomfortable product trade-off.',
                  attempts: [
                    {
                      label: 'primary',
                      model: 'critic-model',
                      status: 'accepted',
                      candidateId: 'candidate-1',
                      aiRunId: 'ai-critic-1',
                      backup: false
                    }
                  ],
                  findings: [
                    {
                      validatorId: 'critic.genericAiProse',
                      severity: 'warning',
                      candidateId: 'candidate-1',
                      message: 'The draft can be swapped with many generic AI posts.',
                      evidenceExcerpt: 'Selected body',
                      repairGuidance: 'Add a sharper author stance.',
                      metadata: { editorialDimension: 'genericAiProse' }
                    }
                  ],
                  observations: [
                    {
                      criticId: 'critic.tension',
                      candidateId: 'candidate-1',
                      message: 'There is a usable workflow tension.',
                      evidenceExcerpt: 'workflow',
                      editorialDimension: 'tension',
                      metadata: {}
                    }
                  ]
                }
              ],
              metadata: { version: 'editorial-critique-v1', reportOnly: true }
            },
            alternativeAngleTournament: {
              status: 'succeeded',
              route: {
                id: 'challenger',
                title: 'Author stance challenger',
                angle: 'Open from the author stance instead of a source recap.',
                openingMove: 'Start with the uncomfortable trade-off.',
                whyDifferent: 'It attacks the generic opening instead of polishing the same route.',
                critiqueInputs: ['critic.genericAiProse'],
                claimsToUse: ['external-claim-1'],
                claimsToAvoid: [],
                rulesToStress: ['rule-audience'],
                risks: ['May overcorrect the tone']
              },
              inputCritiqueSummary: {
                status: 'warning',
                highRiskCandidates: ['candidate-1'],
                weakestMoves: ['Sounds like generic AI prose.'],
                recommendedMoves: ['Open with the uncomfortable product trade-off.']
              },
              candidate: {
                id: 'alternative-angle-1-brief-demo',
                title: 'Alternative challenger',
                body: 'Alternative challenger body.',
                source: 'openrouter',
                routeType: 'alternativeAngle',
                aiRunId: 'ai-alt-candidate'
              },
              attempts: [
                { label: 'primary', model: 'qwen/qwen3.7-max', status: 'accepted', aiRunId: 'ai-alt-route', backup: false }
              ],
              aiRunIds: ['ai-alt-route', 'ai-alt-candidate']
            },
            rankingRevision: {
              status: 'succeeded',
              pairwiseRanking: {
                decision: {
                  winnerCandidateId: 'candidate-1',
                  reason: 'Best validation result.',
                  source: 'openrouter',
                  fallbackUsed: false,
                  warnings: []
                },
                comparisons: [
                  {
                    leftCandidateId: 'candidate-1',
                    rightCandidateId: 'candidate-2',
                    winnerCandidateId: 'candidate-1',
                    reason: 'Candidate 1 has fewer validation findings.'
                  }
                ],
                attempts: [
                  { label: 'primary', model: 'deepseek/deepseek-v3.2', status: 'accepted', aiRunId: 'ai-ranking-1' }
                ]
              },
              revisionInstruction: {
                status: 'created',
                candidateId: 'candidate-1',
                repairGoals: ['Make the reader value explicit.'],
                constraintsToPreserve: ['Keep source-backed claims attributed.']
              },
              revisedCandidate: {
                id: 'revised-candidate-1',
                baseCandidateId: 'candidate-1',
                title: 'Revised candidate',
                body: 'Revised body',
                changeLog: ['Added explicit reader value.']
              },
              revision: {
                status: 'succeeded',
                source: 'openrouter',
                aiRunIds: ['ai-revision-1']
              },
              revisionRegression: {
                accepted: true,
                reasons: ['No deterministic regression.'],
                original: { criticalCount: 0, warningCount: 1, missingAttributionCount: 1 },
                revised: { criticalCount: 0, warningCount: 0, missingAttributionCount: 0 }
              },
              revisionLoop: {
                status: 'succeeded',
                maxIterations: 3,
                finalCandidateId: 'revised-candidate-1',
                finalSource: 'revisionLoop',
                stopReason: 'quality-threshold',
                unresolvedGoals: [],
                constraints: [],
                cycles: [
                  {
                    cycleNumber: 1,
                    baseCandidateId: 'candidate-1',
                    repairGoals: ['Make the reader value explicit.'],
                    constraints: [],
                    revisedCandidate: {
                      id: 'revised-candidate-1',
                      baseCandidateId: 'candidate-1',
                      title: 'Revised candidate',
                      body: 'Revised body'
                    },
                    validationBefore: {},
                    validationAfter: {},
                    pairwiseComparison: {
                      decision: {
                        winnerCandidateId: 'revised-candidate-1',
                        reason: 'Revision closes the targeted finding.'
                      }
                    },
                    resolvedGoals: ['Make the reader value explicit.'],
                    unresolvedGoals: [],
                    editorialGoals: [
                      {
                        id: 'critique-recommended-candidate-1',
                        dimension: 'readerValue',
                        source: 'editorialCritique',
                        message: 'Make reader value explicit.'
                      }
                    ],
                    editorialDimensionScores: [
                      {
                        dimension: 'readerValue',
                        winnerCandidateId: 'revised-candidate-1',
                        reason: 'Revision gives the reader a clearer payoff.'
                      }
                    ],
                    resolvedEditorialGoals: [
                      {
                        id: 'critique-recommended-candidate-1',
                        dimension: 'readerValue',
                        source: 'editorialCritique',
                        message: 'Make reader value explicit.'
                      }
                    ],
                    unresolvedEditorialGoals: [],
                    newRejectedMoves: [
                      {
                        id: 'rejected-cycle-1-1',
                        reason: 'Do not shorten below previous best',
                        constraint: 'Do not shorten below previous best'
                      }
                    ],
                    acceptanceDecision: { accepted: true, reasons: [] },
                    stopReason: 'editorially-improved',
                    accepted: true,
                    rejectionReasons: [],
                    aiRunIds: ['ai-revision-1', 'ai-ranking-2']
                  }
                ]
              },
              finalQualityGate: {
                status: 'warning',
                finalQualityContract: {
                  version: 'final-quality-contract-v1',
                  researchDepth: 'deep',
                  publicationKind: 'linkedin-post',
                  sourceIntegrationPolicy: 'interpret-public-evidence',
                  authorVoicePolicy: 'explicit-author-position'
                },
                modelIndependence: 'independent',
                independentReview: {
                  status: 'warning',
                  findings: [{ severity: 'warning', message: 'Still sounds like an internal report.', repairGuidance: 'Translate evidence into a public argument.' }],
                  observations: [{ status: 'info', summary: 'Thesis is visible.' }],
                  attempts: [{ label: 'primary', status: 'accepted', model: 'gate-model' }]
                },
                finalDraftStatus: 'passed',
                publicProseStatus: 'warning',
                sourceIntegrationStatus: 'passed',
                attributionReview: {
                  actionableCount: 0,
                  diagnosticCount: 1,
                  independentSourceIntegrationStatus: 'passed',
                  independentClosedDiagnosticNoise: true
                },
                actionableAttributionFindings: [],
                diagnosticAttributionNoise: [
                  {
                    severity: 'not-run',
                    message: 'Attribution requirement could not be resolved.',
                    metadata: { suppressedReason: 'empty-attribution-markers' }
                  }
                ],
                internalJargonLeaks: [{ term: 'SourceLedger', excerpt: 'SourceLedger appears in public prose.' }],
                sourceDumpRisk: { status: 'passed', sourceSentenceCount: 2, interpretationSentenceCount: 2 },
                authorVoiceStrength: 'passed',
                readerValueClarity: 'warning',
                finalRepairGoals: ['Remove or translate internal pipeline jargon into reader-facing prose.'],
                maxRepairIterations: 2,
                repairCycles: [
                  {
                    cycleNumber: 1,
                    status: 'rejected',
                    accepted: false,
                    rejectionReasons: ['internal-jargon-not-improved']
                  }
                ],
                acceptedRepair: false,
                repair: {
                  status: 'rejected',
                  decisionStatus: 'rejected',
                  rejectionReasons: ['internal-jargon-not-improved']
                },
                finalDecision: {
                  finalCandidateId: 'revised-candidate-1',
                  source: 'revisionLoop',
                  reason: 'internal-jargon-not-improved'
                }
              },
              finalDecision: {
                finalCandidateId: 'revised-candidate-1',
                baseCandidateId: 'candidate-1',
                source: 'revisionLoop',
                stopReason: 'quality-threshold',
                reason: 'Accepted best candidate from revision loop. Stop reason: quality-threshold.'
              }
            }
          },
          error: null,
          startedAt: null,
          completedAt: null
        }
      ],
      finalDraft: { title: 'Selected', body: 'Selected body' },
      error: null,
      aiRunIds: ['ai-source', 'search-run-1', 'synthesis-run-1', 'ai-interpretation', 'ai-material', 'ai-plans', 'ai-candidate', 'ai-validation-1', 'ai-critic-1', 'ai-alt-route', 'ai-alt-candidate', 'ai-ranking-1', 'ai-revision-1', 'ai-ranking-2'],
      createdAt: '2026-06-19T00:00:00+00:00',
      updatedAt: '2026-06-19T00:00:01+00:00'
    },
    childAiRuns: [
      makeAiRun('ai-source', 'sourceIntentResearchPlan'),
      makeAiRun('search-run-1', 'publicEvidenceSearch'),
      makeAiRun('synthesis-run-1', 'externalEvidenceSynthesis'),
      makeAiRun('ai-interpretation', 'evidenceInterpretation'),
      makeAiRun('ai-material', 'materialPlan'),
      makeAiRun('ai-plans', 'rhetoricalPlans'),
      makeAiRun('ai-candidate', 'draftCandidate'),
      makeAiRun('ai-validation-1', 'llmValidation'),
      makeAiRun('ai-critic-1', 'editorialCritique'),
      makeAiRun('ai-alt-route', 'alternativeAngleRoute'),
      makeAiRun('ai-alt-candidate', 'alternativeAngleCandidate'),
      makeAiRun('ai-ranking-1', 'pairwiseRanking'),
      makeAiRun('ai-revision-1', 'directedRevision'),
      makeAiRun('ai-ranking-2', 'pairwiseRanking')
    ],
    missingAiRunIds: []
  };
}

function makeAiRun(id: string, step: string) {
  const publicEvidenceRequest = {
    draftRunStep: step,
    builtQuery: 'Find public commentary about AI product trust',
    target: 'target-1',
    originalTask: { instruction: 'Find public commentary about AI product trust', target: 'target-1' },
    providerRequest: {
      model: 'deepseek/deepseek-v3.2',
      messages: [
        { role: 'system', content: 'Return JSON' },
        { role: 'user', content: 'Find public commentary about AI product trust' }
      ]
    }
  };
  const publicEvidenceResult = {
    draftRunStep: step,
    acceptedCitations: [{ title: 'AI product trust report', url: 'https://example.com/trust' }],
    rejectedCitations: [{ title: 'TARGET Services', url: 'https://example.com/target', reason: 'search-result-drift' }],
    evidenceItems: [{ sourceTitle: 'AI product trust report', sourceUrl: 'https://example.com/trust', snippet: 'AI trust depends on evals.' }]
  };
  const synthesisResult = {
    draftRunStep: step,
    evidenceSynthesis: {
      source: 'openrouter',
      externalClaims: [{
        publicEvidenceItemId: 'public-evidence-url-task-1',
        statement: 'AI trust depends on evals.',
        allowedUse: 'needsQualification'
      }],
      warnings: [],
      metadata: { externalClaimCount: 1 }
    }
  };
  const interpretationResult = {
    draftRunStep: step,
    result: evidenceInterpretationFixture()
  };
  return {
    id,
    capability: 'draftGeneration',
    status: 'succeeded',
    provider: 'openrouter',
    model: 'deepseek/deepseek-v3.2',
    requestPayload: step === 'publicEvidenceSearch' ? publicEvidenceRequest : {
      draftRunStep: step,
      modelRole: step === 'draftCandidate' ? 'writer' : step === 'llmValidation' || step === 'pairwiseRanking' ? 'review' : 'strategy',
      selectedModel: 'deepseek/deepseek-v3.2',
      modelSelectionSource: 'role',
      capabilityInput: step === 'materialPlan' ? { contextPack: contextPacksFixture().strategy } : undefined,
      contextPack: step === 'draftCandidate' ? contextPacksFixture().writer : undefined,
      providerRequest: {
        messages: [
          { role: 'system', content: 'Return JSON' },
          { role: 'user', content: `${step} payload` }
        ]
      }
    },
    resultPayload: step === 'publicEvidenceSearch'
      ? publicEvidenceResult
      : step === 'externalEvidenceSynthesis'
        ? synthesisResult
        : step === 'evidenceInterpretation'
          ? interpretationResult
        : { draftRunStep: step, result: { thesisAngle: 'angle' } },
    error: null,
    fallbackUsed: false,
    createdAt: '2026-06-19T00:00:00+00:00',
    updatedAt: '2026-06-19T00:00:01+00:00'
  };
}

function draftRunBudgetFixture() {
  return {
    researchDepth: 'marketResearch',
    executionMode: 'standard',
    caps: {
      maxResearchTasks: 12,
      maxSearchTasks: 8,
      maxUrlReads: 6,
      maxSearchResultsPerTask: 8,
      maxAcceptedEvidenceItems: 40,
      maxExternalClaims: 60,
      maxUsableEvidenceCandidates: 24,
      maxDraftCandidates: 3,
      maxRevisionIterations: 3
    },
    source: 'fabula+executionMode'
  };
}

function evidenceInterpretationFixture() {
  return {
    version: 'evidence-interpretation-v1',
    implications: [{
      id: 'implication-1',
      title: 'Workflow proof',
      summary: 'Use source to sharpen the workflow adoption argument.',
      publicEvidenceItemIds: ['public-evidence-url-task-1'],
      claimIds: ['external-evidence-public-evidence-url-task-1'],
      ruleIds: ['rule-grounding'],
      confidence: 'medium',
      allowedUse: 'needsQualification',
      reason: 'Accepted source claim'
    }],
    tensions: [],
    usableExamples: [{
      id: 'example-1',
      title: 'Independent report example',
      summary: 'Adoption depends on workflow integration.',
      publicEvidenceItemIds: ['public-evidence-url-task-1'],
      claimIds: ['external-evidence-public-evidence-url-task-1'],
      confidence: 'medium',
      allowedUse: 'canUseAsFraming'
    }],
    limits: [{
      id: 'limit-1',
      title: 'Do not overclaim',
      summary: 'This source qualifies the claim but does not prove every AI rollout fails.',
      claimIds: ['external-evidence-public-evidence-url-task-1'],
      confidence: 'medium',
      allowedUse: 'needsQualification'
    }],
    forbiddenOverclaims: [{
      id: 'overclaim-1',
      title: 'No universal claim',
      summary: 'Do not say every AI rollout fails.',
      claimIds: ['external-evidence-public-evidence-url-task-1'],
      confidence: 'medium',
      allowedUse: 'doNotState'
    }],
    authorPositionLinks: [],
    readerValueHooks: [],
    recommendedUseByPlan: [],
    rejectedEvidenceUses: [],
    warnings: [],
    metadata: { implicationCount: 1, usableExampleCount: 1, limitCount: 1, warningCount: 0 }
  };
}

function articleDossierFixture() {
  return {
    version: 'article-dossier-v1',
    metadata: { cardCount: 2, byType: { claim: 1, evidence: 1 } },
    cards: [
      { id: 'claim-signal', type: 'claim', title: 'Signal claim', summary: 'Demo adoption needs workflow proof.', source: 'sourceLedger', relatedIds: ['signal-summary'], priority: 'high', metadata: {} },
      { id: 'public-report', type: 'evidence', title: 'Independent report', summary: 'Adoption depends on workflow integration.', source: 'publicEvidence', relatedIds: ['public-evidence-url-task-1'], priority: 'high', metadata: {} }
    ]
  };
}

function contextPacksFixture() {
  return {
    writer: {
      version: 'context-pack-v1',
      role: 'writer',
      metadata: { itemCount: 2 },
      items: [
        { cardId: 'claim-signal', title: 'Signal claim', summary: 'Demo adoption needs workflow proof.', reason: 'Keep usable claims explicit.', source: 'sourceLedger', priority: 'high', metadata: { type: 'claim' } },
        { cardId: 'public-report', title: 'Independent report', summary: 'Adoption depends on workflow integration.', reason: 'Ground the step in accepted evidence.', source: 'publicEvidence', priority: 'high', metadata: { type: 'evidence' } }
      ]
    },
    review: {
      version: 'context-pack-v1',
      role: 'review',
      metadata: { itemCount: 1 },
      items: [
        { cardId: 'claim-signal', title: 'Signal claim', summary: 'Demo adoption needs workflow proof.', reason: 'Keep usable claims explicit.', source: 'sourceLedger', priority: 'high', metadata: { type: 'claim' } }
      ]
    },
    strategy: {
      version: 'context-pack-v1',
      role: 'strategy',
      metadata: { itemCount: 1 },
      items: [
        { cardId: 'claim-signal', title: 'Signal claim', summary: 'Demo adoption needs workflow proof.', reason: 'Keep usable claims explicit.', source: 'sourceLedger', priority: 'high', metadata: { type: 'claim' } }
      ]
    }
  };
}

function traceStep(viewModel: ReturnType<typeof buildRunTraceViewModel>, key: string) {
  return viewModel.timeline.find((item) => item.key === key);
}
