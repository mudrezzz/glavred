import type { AiRunTrace } from '../../infrastructure/aiRunTraceClient';
import type { DraftRunTrace, DraftRunTraceStep, RunTraceBundle } from '../../infrastructure/runTraceClient';
import {
  buildDraftCandidateSemanticSections,
  buildDraftCandidateTraceArtifacts
} from './draftCandidateTraceViewModel';

export type TraceRole = 'system' | 'user' | 'assistant' | 'tool' | 'unknown';

export type TraceField = {
  label: string;
  value: string;
};

export type TraceMessage = {
  id: string;
  index: number;
  role: TraceRole;
  preview: string;
  content: string;
};

export type TraceSemanticSection = {
  id: string;
  title: string;
  fields: TraceField[];
  body?: string;
  kind?: 'fields' | 'scorecard';
  scorecard?: TraceScorecardModel;
};

export type TraceScorecardModel = {
  selectedCandidateId: string;
  scoreSpread: string;
  rows: TraceScorecardRow[];
};

export type TraceScorecardRow = {
  candidateId: string;
  title: string;
  selected: boolean;
  publishable: string;
  selectionStatus: string;
  selectionPenalty: string;
  selectionReasons: string;
  total: string;
  hardConstraintFit: string;
  evidenceGrounding: string;
  topicFit: string;
  fabulaFit: string;
  audienceValue: string;
  riskPenalty: string;
};

export type TraceChildCall = {
  id: string;
  title: string;
  provider: string;
  model: string;
  status: string;
  fallback: string;
  detailId: string;
  kind?: 'llm' | 'artifact';
  meta?: TraceField[];
};

export type TraceStepOperation = {
  id: string;
  kind: string;
  label: string;
  status: string;
  startedAt: string;
  completedAt: string;
  aiRunId: string;
  target: string;
  error: string;
  notes: string;
};

export type TraceTimelineStep = {
  id: string;
  key: string;
  title: string;
  status: string;
  error: string | null;
  detailId: string;
  operations: TraceStepOperation[];
  childCalls: TraceChildCall[];
};

export type TraceDetail = {
  id: string;
  title: string;
  kicker: string;
  summary: TraceField[];
  sections: TraceSemanticSection[];
  messages: TraceMessage[];
  jsonPayload: unknown;
  rawPayload: unknown;
};

export type RunTraceViewModel = {
  mode: 'draftRun' | 'aiRun';
  id: string;
  title: string;
  summary: TraceField[];
  timeline: TraceTimelineStep[];
  semanticSections: TraceSemanticSection[];
  details: TraceDetail[];
  initialDetailId: string;
};

export function buildRunTraceViewModel(bundle: RunTraceBundle): RunTraceViewModel {
  if (bundle.kind === 'aiRun') return buildSingleAiRunViewModel(bundle.aiRun);
  return buildDraftRunViewModel(bundle.draftRun, bundle.childAiRuns, bundle.missingAiRunIds);
}

export function prettyTraceValue(value: unknown): string {
  if (typeof value === 'string') {
    const trimmed = value.trim();
    if ((trimmed.startsWith('{') && trimmed.endsWith('}')) || (trimmed.startsWith('[') && trimmed.endsWith(']'))) {
      try {
        return JSON.stringify(JSON.parse(trimmed), null, 2);
      } catch {
        return value;
      }
    }
    return value;
  }
  return displayValue(value);
}

function buildDraftRunViewModel(
  draftRun: DraftRunTrace,
  childAiRuns: AiRunTrace[],
  missingAiRunIds: string[]
): RunTraceViewModel {
  const details: TraceDetail[] = [];
  const timeline = draftRun.steps.map((step) => {
    const stepDetail = buildStepDetail(step);
    details.push(stepDetail);
    const childCalls = childAiRuns
      .filter((run) => parentStepForAiRun(run) === step.key)
      .map((run) => {
        const detail = buildAiRunDetail(run);
        details.push(detail);
        return {
          id: run.id,
          title: aiRunStepLabel(run),
          provider: run.provider,
          model: run.model ?? 'none',
          status: run.status,
          fallback: run.fallbackUsed ? 'yes' : 'no',
          detailId: detail.id,
          meta: modelSelectionFields(run)
        };
      });
    const draftCandidateTrace = buildDraftCandidateTraceArtifacts(step, childAiRuns);
    details.push(...draftCandidateTrace.details);
    return {
      id: `step-${step.key}`,
      key: step.key,
      title: step.title || stepLabel(step.key),
      status: traceStepStatus(draftRun, step),
      error: step.error,
      detailId: stepDetail.id,
      operations: progressOperations(step),
      childCalls: [...childCalls, ...draftCandidateTrace.childCalls]
    };
  });

  missingAiRunIds.forEach((aiRunId) => {
    const missingDetail = {
      id: `missing-${aiRunId}`,
      title: `Missing AiRun ${aiRunId}`,
      kicker: 'Child LLM call',
      summary: [{ label: 'AiRun ID', value: aiRunId }, { label: 'Status', value: 'missing' }],
      sections: [{ id: 'missing', title: 'Warning', fields: [{ label: 'Missing child', value: 'AI run record could not be loaded.' }] }],
      messages: [],
      jsonPayload: { aiRunId, missing: true },
      rawPayload: { aiRunId, missing: true }
    };
    details.push(missingDetail);
    const draftStep = timeline.find((step) => step.key === 'draft') ?? timeline[timeline.length - 1];
    draftStep?.childCalls.push({
      id: aiRunId,
      title: 'Missing child run',
      provider: 'unknown',
      model: 'unknown',
      status: 'missing',
      fallback: 'unknown',
      detailId: missingDetail.id
    });
  });

  const semanticSections = buildDraftRunSemanticSections(draftRun);
  const firstDetailId = timeline[0]?.detailId ?? details[0]?.id ?? '';
  return {
    mode: 'draftRun',
    id: draftRun.id,
    title: 'DraftRun trace',
    summary: [
      { label: 'Run type', value: 'DraftRun' },
      { label: 'Status', value: draftRun.isStale ? 'stale-running' : draftRun.status },
      { label: 'Steps', value: String(draftRun.steps.length) },
      { label: 'LLM calls', value: String(childAiRuns.length) },
      { label: 'Missing calls', value: String(missingAiRunIds.length) },
      { label: 'Last progress', value: draftRun.lastProgressAt ?? draftRun.updatedAt },
      { label: 'Created', value: draftRun.createdAt },
      { label: 'Updated', value: draftRun.updatedAt }
    ],
    timeline,
    semanticSections,
    details,
    initialDetailId: firstDetailId
  };
}

function parentStepForAiRun(run: AiRunTrace): string | undefined {
  const step = stepKeyForAiRun(run);
  return step === 'llmValidation' || step === 'editorialCritique' ? 'validation' : step;
}

function traceStepStatus(draftRun: DraftRunTrace, step: DraftRunTraceStep): string {
  if (!draftRun.isStale) return step.status;
  if (step.status === 'running') return 'stale-running';
  const hasRunningStep = draftRun.steps.some((item) => item.status === 'running');
  if (!hasRunningStep && step.status === 'pending') {
    const firstPending = draftRun.steps.find((item) => item.status === 'pending');
    return firstPending?.key === step.key ? 'stale-running' : step.status;
  }
  return step.status;
}

function buildSingleAiRunViewModel(aiRun: AiRunTrace): RunTraceViewModel {
  const detail = buildAiRunDetail(aiRun);
  const step = stepKeyForAiRun(aiRun);
  const title = aiRunStepLabel(aiRun);
  return {
    mode: 'aiRun',
    id: aiRun.id,
    title: 'AiRun trace',
    summary: [
      { label: 'Run type', value: 'AiRun' },
      { label: 'Step', value: title },
      { label: 'Status', value: aiRun.status },
      { label: 'Provider', value: aiRun.provider },
      { label: 'Model', value: aiRun.model ?? 'none' },
      ...modelSelectionFields(aiRun),
      { label: 'Fallback', value: aiRun.fallbackUsed ? 'yes' : 'no' }
    ],
    timeline: [{
      id: `step-${step}`,
      key: step,
      title,
      status: aiRun.status,
      error: aiRun.error,
      detailId: detail.id,
      operations: [],
      childCalls: [{
        id: aiRun.id,
        title,
        provider: aiRun.provider,
        model: aiRun.model ?? 'none',
        status: aiRun.status,
        fallback: aiRun.fallbackUsed ? 'yes' : 'no',
        detailId: detail.id
      }]
    }],
    semanticSections: buildAiRunSemanticSections(aiRun),
    details: [detail],
    initialDetailId: detail.id
  };
}

function buildStepDetail(step: DraftRunTraceStep): TraceDetail {
  const progress = asRecord(step.artifactPayload?.progress);
  return {
    id: `step-detail-${step.key}`,
    title: step.title || stepLabel(step.key),
    kicker: 'Logical step',
    summary: [
      { label: 'Step', value: step.key },
      { label: 'Status', value: step.status },
      { label: 'Started', value: step.startedAt ?? 'not started' },
      { label: 'Completed', value: step.completedAt ?? 'not completed' },
      { label: 'Current operation', value: stringValue(progress?.currentOperationId) ?? 'none' }
    ],
    sections: sectionsFromPayload(step.key, step.artifactPayload ?? {}),
    messages: [],
    jsonPayload: step.artifactPayload ?? {},
    rawPayload: step
  };
}

function progressOperations(step: DraftRunTraceStep): TraceStepOperation[] {
  const progress = asRecord(step.artifactPayload?.progress);
  const operations = asArray(progress?.operations) ?? [];
  return operations.flatMap((item) => {
    const operation = asRecord(item);
    if (!operation) return [];
    return [{
      id: stringValue(operation.id) ?? 'operation',
      kind: stringValue(operation.kind) ?? 'operation',
      label: stringValue(operation.label) ?? stringValue(operation.id) ?? 'Operation',
      status: stringValue(operation.status) ?? 'unknown',
      startedAt: stringValue(operation.startedAt) ?? '',
      completedAt: stringValue(operation.completedAt) ?? '',
      aiRunId: stringValue(operation.aiRunId) ?? '',
      target: stringValue(operation.target) ?? '',
      error: stringValue(operation.error) ?? '',
      notes: displayValue(operation.notes)
    }];
  });
}

function buildAiRunDetail(aiRun: AiRunTrace): TraceDetail {
  const requestPayload = aiRun.requestPayload ?? {};
  const resultPayload = aiRun.resultPayload ?? {};
  const messages = extractMessages(requestPayload);
  return {
    id: `ai-detail-${aiRun.id}`,
    title: `${aiRunStepLabel(aiRun)} · ${aiRun.id}`,
    kicker: 'LLM call',
    summary: [
      { label: 'AiRun ID', value: aiRun.id },
      { label: 'Provider', value: aiRun.provider },
      { label: 'Model', value: aiRun.model ?? 'none' },
      ...modelSelectionFields(aiRun),
      { label: 'Status', value: aiRun.status },
      { label: 'Fallback', value: aiRun.fallbackUsed ? 'yes' : 'no' },
      { label: 'Error', value: aiRun.error ?? 'none' }
    ],
    sections: buildAiRunSemanticSections(aiRun),
    messages,
    jsonPayload: {
      requestPayload,
      resultPayload
    },
    rawPayload: aiRun
  };
}

function buildDraftRunSemanticSections(draftRun: DraftRunTrace): TraceSemanticSection[] {
  const sections = draftRun.steps.flatMap((step) => sectionsFromPayload(step.key, step.artifactPayload ?? {}));
  if (draftRun.finalDraft) {
    sections.push({
      id: 'finalDraft',
      title: 'Selected draft',
      fields: compactFields([
        ['Title', draftRun.finalDraft.title],
        ['Version', draftRun.finalDraft.version],
        ['Status', draftRun.finalDraft.status]
      ]),
      body: stringValue(draftRun.finalDraft.body) ?? undefined
    });
  }
  return sections.length > 0 ? sections : [{ id: 'empty', title: 'No semantic artifacts', fields: [] }];
}

function buildAiRunSemanticSections(aiRun: AiRunTrace): TraceSemanticSection[] {
  const requestPayload = aiRun.requestPayload ?? {};
  const resultPayload = aiRun.resultPayload ?? {};
  const capabilityInput = asRecord(requestPayload.capabilityInput);
  const contextPack = asRecord(requestPayload.contextPack) ?? asRecord(capabilityInput?.contextPack);
  if (rawStepKeyForAiRun(aiRun) === 'publicEvidenceSearch') {
    return [
      ...(contextPack ? [contextPacksSection({ [stringValue(contextPack.role) ?? 'role']: contextPack })] : []),
      publicEvidenceSearchSection(requestPayload, resultPayload),
      ...sectionsFromPayload('publicEvidence', resultPayload)
    ];
  }
  return [
    ...(contextPack ? [contextPacksSection({ [stringValue(contextPack.role) ?? 'role']: contextPack })] : []),
    ...sectionsFromPayload(rawStepKeyForAiRun(aiRun) ?? stepKeyForAiRun(aiRun), resultPayload)
  ];
}

function modelSelectionFields(aiRun: AiRunTrace): TraceField[] {
  const payload = { ...(aiRun.resultPayload ?? {}), ...(aiRun.requestPayload ?? {}) };
  return compactFields([
    ['Model role', payload.modelRole],
    ['Selected model', payload.selectedModel],
    ['Selection source', payload.modelSelectionSource]
  ]);
}

function sectionsFromPayload(step: string, payload: Record<string, unknown>): TraceSemanticSection[] {
  const sections: TraceSemanticSection[] = [];
  const materialPlan = asRecord(payload.materialPlan) ?? (step === 'materialPlan' ? asRecord(payload.result) : null);
  const sourceIntent = asRecord(payload.sourceIntent);
  const researchPlan = asRecord(payload.researchPlan);
  const publicEvidence = asRecord(payload.publicEvidence) ?? (step === 'publicEvidence' ? payload : null);
  const evidenceSynthesis = asRecord(payload.evidenceSynthesis);
  const evidenceInterpretation = asRecord(payload.evidenceInterpretation) ?? (step === 'evidenceInterpretation' ? asRecord(payload.result) : null);
  const sourceLedger = asRecord(payload.enrichedSourceLedger) ?? asRecord(payload.sourceLedger);
  const feasibility = asRecord(payload.feasibilityReport) ?? (step === 'feasibility' ? payload : null);
  const postContract = asRecord(payload.postContract) ?? (step === 'postContract' ? payload : null);
  const ruleRegistry = asRecord(payload.ruleRegistrySnapshot);
  const strategy = asRecord(payload.draftStrategy) ?? (step === 'strategy' ? asRecord(payload.result) : null);
  const rhetoricalPlanSet = asRecord(payload.rhetoricalPlanSet);
  const candidate = asRecord(payload.candidate);
  const candidates = asArray(payload.candidates);
  const selection = asRecord(payload.selection);
  const draft = asRecord(payload.draft);
  const validation = step === 'validation' ? payload : asRecord(payload.validationReport);
  const editorialCritique = asRecord(payload.editorialCritiqueReport);
  const alternativeAngleTournament = asRecord(payload.alternativeAngleTournament);
  const rankingRevision = asRecord(payload.rankingRevision);
  const articleDossier = asRecord(payload.articleDossier);
  const contextPacks = asRecord(payload.contextPacks);
  const draftRunBudget = asRecord(payload.draftRunBudget) ?? asRecord(asRecord(payload.metadata)?.draftRunBudget);

  if (draftRunBudget) sections.push(draftRunBudgetSection(draftRunBudget, payload));
  if (articleDossier) sections.push(articleDossierSection(articleDossier));
  if (contextPacks) sections.push(contextPacksSection(contextPacks));
  if (sourceIntent) sections.push(sourceIntentSection(sourceIntent, stringValue(payload.sourcesOrigin) ?? undefined));
  if (researchPlan) sections.push(researchPlanSection(researchPlan));
  if (publicEvidence) sections.push(publicEvidenceSection(publicEvidence));
  if (evidenceSynthesis) sections.push(evidenceSynthesisSection(evidenceSynthesis));
  if (evidenceInterpretation) sections.push(evidenceInterpretationSection(evidenceInterpretation, payload));
  if (sourceLedger) sections.push(sourceLedgerSection(sourceLedger));
  if (feasibility) sections.push(feasibilitySection(feasibility));
  if (postContract) {
    sections.push(postContractSection(postContract));
    const sizeContract = asRecord(postContract.publicationSizeContract);
    if (sizeContract) sections.push(publicationSizeSection(sizeContract));
  }
  if (ruleRegistry) sections.push(ruleRegistrySection(ruleRegistry));
  if (materialPlan) sections.push(materialPlanSection(materialPlan, payload));
  if (strategy) sections.push(strategySection(strategy));
  if (rhetoricalPlanSet && asArray(payload.attempts)) sections.push(rhetoricalPlanAttemptsSection(payload));
  if (rhetoricalPlanSet) sections.push(...rhetoricalPlanSections(rhetoricalPlanSet));
  if (candidate) sections.push(candidateSection(candidate, 'Draft candidate'));
  if (candidates || selection) sections.push(...buildDraftCandidateSemanticSections(payload));
  if (alternativeAngleTournament) sections.push(alternativeAngleTournamentSection(alternativeAngleTournament));
  if (validation) sections.push(validationSection(validation));
  if (editorialCritique) sections.push(editorialCritiqueSection(editorialCritique));
  if (rankingRevision) sections.push(...rankingRevisionSections(rankingRevision));
  if (draft) {
    sections.push({
      id: 'draft',
      title: 'Draft',
      fields: compactFields([
        ['Title', draft.title],
        ['Version', draft.version],
        ['Status', draft.status]
      ]),
      body: stringValue(draft.body) ?? undefined
    });
  }
  if (sections.length === 0 && Object.keys(payload).length > 0) {
    sections.push({ id: `${step}-raw`, title: stepLabel(step), fields: objectToFields(payload) });
  }
  return sections;
}

function rankingRevisionSections(payload: Record<string, unknown>): TraceSemanticSection[] {
  const pairwise = asRecord(payload.pairwiseRanking);
  const decision = asRecord(pairwise?.decision);
  const instruction = asRecord(payload.revisionInstruction);
  const revised = asRecord(payload.revisedCandidate);
  const regression = asRecord(payload.revisionRegression);
  const loop = asRecord(payload.revisionLoop);
  const finalQualityGate = asRecord(payload.finalQualityGate);
  const finalDecision = asRecord(payload.finalDecision);
  const sections: TraceSemanticSection[] = [];
  if (loop) {
    sections.push({
      id: 'revision-loop',
      title: 'Revision loop',
      fields: compactFields([
        ['Status', loop.status],
        ['Max iterations', loop.maxIterations],
        ['Stop reason', loop.stopReason],
        ['Final candidate', loop.finalCandidateId],
        ['Final source', loop.finalSource],
        ['Unresolved goals', loop.unresolvedGoals],
        ['Constraints', loop.constraints],
        ['Editorial goals', asArray(loop.cycles)?.flatMap(revisionLoopEditorialGoals).map(editorialGoalValue)],
        ['Editorial dimension scores', asArray(loop.cycles)?.flatMap(revisionLoopDimensionScores).map(editorialDimensionScoreValue)],
        ['Rejected moves', asArray(loop.cycles)?.flatMap(revisionLoopRejectedMoves).map(rejectedMoveValue)],
        ['Cycles', asArray(loop.cycles)?.map(revisionLoopCycleValue)]
      ])
    });
  }
  return [
    ...sections,
    {
      id: 'pairwise-ranking',
      title: 'Pairwise ranking',
      fields: compactFields([
        ['Winner', decision?.winnerCandidateId],
        ['Reason', decision?.reason],
        ['Source', decision?.source],
        ['Fallback', decision?.fallbackUsed],
        ['Warnings', decision?.warnings],
        ['Attempts', asArray(pairwise?.attempts)?.map(attemptValue)],
        ['Comparisons', asArray(pairwise?.comparisons)?.map(pairwiseComparisonValue)]
      ])
    },
    {
      id: 'directed-revision',
      title: 'Directed revision',
      fields: compactFields([
        ['Status', instruction?.status],
        ['Candidate', instruction?.candidateId],
        ['Reason', instruction?.reason],
        ['Repair goals', instruction?.repairGoals],
        ['Revision status', asRecord(payload.revision)?.status],
        ['Revision reason', asRecord(payload.revision)?.reason],
        ['Revision attempts', asArray(asRecord(payload.revision)?.attempts)?.map(attemptValue)]
      ]),
      body: revised ? stringValue(revised.body) ?? undefined : undefined
    },
    {
      id: 'revision-regression',
      title: 'Revision regression',
      fields: compactFields([
        ['Accepted', regression?.accepted],
        ['Reasons', regression?.reasons],
        ['Original counts', regression?.originalCounts],
        ['Revised counts', regression?.revisedCounts]
      ])
    },
    ...(finalQualityGate ? [finalQualityGateSection(finalQualityGate)] : []),
    {
      id: 'ranking-final-decision',
      title: 'Final draft decision',
      fields: compactFields([
        ['Final candidate', finalDecision?.finalCandidateId],
        ['Base candidate', finalDecision?.baseCandidateId],
        ['Source', finalDecision?.source],
        ['Reason', finalDecision?.reason]
      ])
    }
  ];
}

function finalQualityGateSection(payload: Record<string, unknown>): TraceSemanticSection {
  const repair = asRecord(payload.repair);
  const repairDecision = asRecord(payload.finalDecision);
  const contract = asRecord(payload.finalQualityContract);
  const independent = asRecord(payload.independentReview);
  return {
    id: 'final-quality-gate',
    title: 'Final quality gate',
    fields: compactFields([
      ['Status', payload.status],
      ['Contract', finalQualityContractValue(contract)],
      ['Model independence', payload.modelIndependence],
      ['Independent review status', independent?.status],
      ['Independent findings', asArray(independent?.findings)?.map(finalQualityFindingValue)],
      ['Independent observations', asArray(independent?.observations)?.map(finalQualityFindingValue)],
      ['Independent attempts', asArray(independent?.attempts)?.map(attemptValue)],
      ['Final draft status', payload.finalDraftStatus],
      ['Public prose', payload.publicProseStatus],
      ['Source integration', payload.sourceIntegrationStatus],
      ['Internal jargon leaks', asArray(payload.internalJargonLeaks)?.map(finalQualityLeakValue)],
      ['Source dump risk', payload.sourceDumpRisk],
      ['Author voice', payload.authorVoiceStrength],
      ['Reader value', payload.readerValueClarity],
      ['Repair goals', payload.finalRepairGoals],
      ['Max repair iterations', payload.maxRepairIterations],
      ['Repair cycles', asArray(payload.repairCycles)?.map(finalQualityRepairCycleValue)],
      ['Repair status', repair?.status],
      ['Repair decision', repair?.decisionStatus],
      ['Accepted repair', payload.acceptedRepair],
      ['Repair rejection reasons', repair?.rejectionReasons],
      ['Final source', repairDecision?.source],
      ['Final reason', repairDecision?.reason]
    ])
  };
}

function finalQualityContractValue(contract: Record<string, unknown> | null): string | undefined {
  if (!contract) return undefined;
  return [
    `depth ${contract.researchDepth ?? 'unknown'}`,
    `kind ${contract.publicationKind ?? 'unknown'}`,
    `source ${contract.sourceIntegrationPolicy ?? 'unknown'}`,
    `voice ${contract.authorVoicePolicy ?? 'unknown'}`
  ].join(' В· ');
}

function finalQualityFindingValue(value: unknown): string {
  const finding = asRecord(value);
  if (!finding) return displayValue(value);
  return `${finding.severity ?? finding.status ?? 'info'} В· ${finding.message ?? finding.summary ?? finding.id ?? ''}${finding.repairGuidance ? ` В· ${finding.repairGuidance}` : ''}`;
}

function finalQualityRepairCycleValue(value: unknown): string {
  const cycle = asRecord(value);
  if (!cycle) return displayValue(value);
  return [
    `cycle ${cycle.cycleNumber ?? '?'}`,
    `status ${cycle.status ?? cycle.decisionStatus ?? 'unknown'}`,
    `accepted ${cycle.accepted}`,
    `reasons ${displayValue(cycle.rejectionReasons).replace(/\n/g, '; ') || 'none'}`
  ].join(' В· ');
}

function finalQualityLeakValue(value: unknown): string {
  const leak = asRecord(value);
  if (!leak) return displayValue(value);
  return `${leak.term ?? 'term'}${leak.excerpt ? ` · ${leak.excerpt}` : ''}`;
}

function revisionLoopCycleValue(value: unknown): string {
  const cycle = asRecord(value);
  if (!cycle) return displayValue(value);
  return [
    `cycle ${cycle.cycleNumber}`,
    `base ${cycle.baseCandidateId}`,
    `accepted ${cycle.accepted}`,
    `resolved ${displayValue(cycle.resolvedGoals).replace(/\n/g, '; ') || 'none'}`,
    `unresolved ${displayValue(cycle.unresolvedGoals).replace(/\n/g, '; ') || 'none'}`,
    `rejection ${displayValue(cycle.rejectionReasons).replace(/\n/g, '; ') || 'none'}`
  ].join(' · ');
}

function revisionLoopEditorialGoals(value: unknown): unknown[] {
  return asArray(asRecord(value)?.editorialGoals) ?? [];
}

function revisionLoopDimensionScores(value: unknown): unknown[] {
  return asArray(asRecord(value)?.editorialDimensionScores) ?? [];
}

function revisionLoopRejectedMoves(value: unknown): unknown[] {
  return asArray(asRecord(value)?.newRejectedMoves) ?? [];
}

function editorialGoalValue(value: unknown): string {
  const goal = asRecord(value);
  if (!goal) return displayValue(value);
  return `${goal.dimension ?? 'editorial'} В· ${goal.source ?? 'unknown'} В· ${goal.message ?? goal.id ?? ''}`;
}

function editorialDimensionScoreValue(value: unknown): string {
  const score = asRecord(value);
  if (!score) return displayValue(value);
  return `${score.dimension ?? 'dimension'} -> ${score.winnerCandidateId ?? 'unknown'}: ${score.reason ?? ''}`;
}

function rejectedMoveValue(value: unknown): string {
  const move = asRecord(value);
  if (!move) return displayValue(value);
  return `${move.id ?? 'rejected'} В· ${move.reason ?? ''}${move.constraint ? ` В· ${move.constraint}` : ''}`;
}

function pairwiseComparisonValue(value: unknown): string {
  const comparison = asRecord(value);
  if (!comparison) return displayValue(value);
  return `${comparison.leftCandidateId} vs ${comparison.rightCandidateId} -> ${comparison.winnerCandidateId}: ${comparison.reason}`;
}

function attemptValue(value: unknown): string {
  const attempt = asRecord(value);
  if (!attempt) return displayValue(value);
  return `${attempt.label ?? 'attempt'} · ${attempt.status ?? 'unknown'} · ${attempt.model ?? ''}${attempt.backup ? ' · backup' : ''}${attempt.validation ? ` · ${attempt.validation}` : ''}`;
}

function validationSection(payload: Record<string, unknown>): TraceSemanticSection {
  const summary = asRecord(payload.summary);
  const reports = asArray(payload.candidateReports) ?? [];
  const llmReport = asRecord(payload.llmValidationReport);
  if (reports.length === 0) {
    return {
      id: 'validation',
      title: 'Validation report',
      fields: compactFields([
        ['Status', payload.status],
        ['Reason', asRecord(payload.metadata)?.reason],
        ['Checks', payload.checks],
        ['Metadata', payload.metadata]
      ])
    };
  }
  return {
    id: 'validation',
    title: 'Validation report',
    fields: compactFields([
      ['Status', payload.status],
      ['Selected candidate', payload.selectedCandidateId],
      ['Candidates', summary?.candidateCount ?? reports.length],
      ['Critical findings', summary?.criticalCount],
      ['Warnings', summary?.warningCount],
      ['Selected status', summary?.selectedStatus],
      ['Candidate quality', reports.map(validationCandidateValue)],
      ['Size findings', validationFindings(reports, 'size.')],
      ['Source attribution findings', validationFindings(reports, 'evidence.attribution')],
      ['Attribution markers', attributionMarkerFindings(reports)],
      ['Publishability findings', validationFindings(reports, 'publishability.')],
      ['Rule findings', validationFindings(reports, 'rules.')],
      ['LLM validation status', llmReport?.status],
      ['LLM validation observations', llmValidationObservationCount(llmReport)],
      ['LLM validation attempts', llmValidationAttempts(llmReport)],
      ['LLM actionable findings', llmValidationFindings(llmReport)],
      ['LLM observations', llmValidationObservations(llmReport)]
    ])
  };
}

function validationCandidateValue(item: unknown): unknown {
  const report = asRecord(item);
  if (!report) return item;
  return `${report.selected ? 'selected · ' : ''}${report.candidateId}: ${report.status} · critical ${report.criticalCount ?? 0} · warnings ${report.warningCount ?? 0}`;
}

function alternativeAngleTournamentSection(payload: Record<string, unknown>): TraceSemanticSection {
  const route = asRecord(payload.route);
  const candidate = asRecord(payload.candidate);
  const critique = asRecord(payload.inputCritiqueSummary);
  return {
    id: 'alternative-angle-tournament',
    title: 'Alternative angle tournament',
    fields: compactFields([
      ['Status', payload.status],
      ['Reason', payload.reason],
      ['Route', route ? `${route.id ?? 'route'} - ${route.title ?? ''}` : null],
      ['Why different', route?.whyDifferent],
      ['Critique inputs', route?.critiqueInputs],
      ['Weakest moves', critique?.weakestMoves],
      ['Recommended moves', critique?.recommendedMoves],
      ['Candidate', candidate?.id],
      ['Candidate title', candidate?.title],
      ['Candidate source', candidate?.source],
      ['Attempts', asArray(payload.attempts)?.map(attemptValue)],
      ['AiRun IDs', payload.aiRunIds]
    ]),
    body: stringValue(candidate?.body) ?? undefined
  };
}

function validationFindings(reports: unknown[], prefix: string): unknown[] {
  return reports.flatMap((item) => {
    const report = asRecord(item);
    const candidateId = stringValue(report?.candidateId) ?? 'candidate';
    return (asArray(report?.findings) ?? []).flatMap((findingItem) => {
      const finding = asRecord(findingItem);
      const validatorId = stringValue(finding?.validatorId) ?? '';
      if (!validatorId.startsWith(prefix)) return [];
      return `${candidateId} · ${finding?.severity}: ${finding?.message}\n${finding?.repairGuidance ?? ''}`;
    });
  });
}

function attributionMarkerFindings(reports: unknown[]): unknown[] {
  return reports.flatMap((item) => {
    const report = asRecord(item);
    const candidateId = stringValue(report?.candidateId) ?? 'candidate';
    return (asArray(report?.findings) ?? []).flatMap((findingItem) => {
      const finding = asRecord(findingItem);
      if (finding?.validatorId !== 'evidence.attribution') return [];
      const metadata = asRecord(finding.metadata);
      const missing = asArray(metadata?.missingClaimIds) ?? [];
      const matched = asRecord(metadata?.matchedAttributionMarkers);
      const expected = asRecord(metadata?.expectedAttributionMarkers);
      if (!metadata || (missing.length === 0 && !matched && !expected)) return [];
      return `${candidateId} · missing ${formatList(missing)}\nmatched: ${formatMarkerMap(matched)}\nexpected: ${formatMarkerMap(expected)}`;
    });
  });
}

function llmValidationAttempts(report: Record<string, unknown> | null | undefined): unknown[] {
  if (!report) return [];
  return (asArray(report.candidateReports) ?? []).flatMap((item) => {
    const candidateReport = asRecord(item);
    const candidateId = stringValue(candidateReport?.candidateId) ?? 'candidate';
    return (asArray(candidateReport?.attempts) ?? []).map((attemptItem) => {
      const attempt = asRecord(attemptItem);
      if (!attempt) return attemptItem;
      const validation = attempt.validation ? `\n${displayValue(attempt.validation)}` : '';
      return `${candidateId} · ${attempt.label}: ${attempt.status} · ${attempt.model ?? 'no model'}${attempt.backup ? ' · backup' : ''}${validation}`;
    });
  });
}

function llmValidationFindings(report: Record<string, unknown> | null | undefined): unknown[] {
  if (!report) return [];
  return (asArray(report.candidateReports) ?? []).flatMap((item) => {
    const candidateReport = asRecord(item);
    const candidateId = stringValue(candidateReport?.candidateId) ?? 'candidate';
    return (asArray(candidateReport?.findings) ?? []).map((findingItem) => {
      const finding = asRecord(findingItem);
      if (!finding) return findingItem;
      return `${candidateId} · ${finding.severity}: ${finding.validatorId}\n${finding.message}\n${finding.repairGuidance ?? ''}`;
    });
  });
}

function llmValidationObservations(report: Record<string, unknown> | null | undefined): unknown[] {
  if (!report) return [];
  return (asArray(report.candidateReports) ?? []).flatMap((item) => {
    const candidateReport = asRecord(item);
    const candidateId = stringValue(candidateReport?.candidateId) ?? 'candidate';
    return (asArray(candidateReport?.observations) ?? []).map((observationItem) => {
      const observation = asRecord(observationItem);
      if (!observation) return observationItem;
      const repair = observation.repairGuidance ? `\n${observation.repairGuidance}` : '';
      return `${candidateId} - ${observation.validatorId}\n${observation.message}${repair}`;
    });
  });
}

function llmValidationObservationCount(report: Record<string, unknown> | null | undefined): string {
  if (!report) return '';
  const summary = asRecord(report.summary);
  if (summary?.observationCount != null) return displayValue(summary.observationCount);
  const count = (asArray(report.candidateReports) ?? []).reduce<number>((total, item) => {
    const candidateReport = asRecord(item);
    return total + (asArray(candidateReport?.observations)?.length ?? 0);
  }, 0);
  return count > 0 ? String(count) : '';
}

function editorialCritiqueSection(report: Record<string, unknown>): TraceSemanticSection {
  const summary = asRecord(report.summary);
  const candidateReports = asArray(report.candidateReports) ?? [];
  return {
    id: 'editorial-critique',
    title: 'Editorial critique',
    fields: compactFields([
      ['Status', report.status],
      ['Candidates', summary?.candidateCount ?? candidateReports.length],
      ['Findings', summary?.findingCount],
      ['Observations', summary?.observationCount],
      ['High-risk candidates', summary?.highRiskCandidateCount],
      ['Candidate risks', candidateReports.map(editorialCritiqueCandidateValue)],
      ['Actionable critique', editorialCritiqueFindings(candidateReports)],
      ['Editorial observations', editorialCritiqueObservations(candidateReports)],
      ['Attempts', editorialCritiqueAttempts(candidateReports)]
    ])
  };
}

function editorialCritiqueCandidateValue(item: unknown): unknown {
  const report = asRecord(item);
  if (!report) return item;
  return `${report.candidateId}: ${report.status} - risk ${report.editorialRisk ?? 'unknown'} - weakest ${shortValue(report.weakestMove) || 'none'} - move ${shortValue(report.recommendedEditorialMove) || 'none'}`;
}

function editorialCritiqueFindings(reports: unknown[]): unknown[] {
  return reports.flatMap((item) => {
    const report = asRecord(item);
    const candidateId = stringValue(report?.candidateId) ?? 'candidate';
    return (asArray(report?.findings) ?? []).map((findingItem) => {
      const finding = asRecord(findingItem);
      if (!finding) return findingItem;
      const id = stringValue(finding.validatorId) ?? stringValue(finding.criticId) ?? 'critic';
      return `${candidateId} - ${finding.severity ?? 'warning'}: ${id}\n${finding.message ?? ''}\n${finding.repairGuidance ?? ''}`;
    });
  });
}

function editorialCritiqueObservations(reports: unknown[]): unknown[] {
  return reports.flatMap((item) => {
    const report = asRecord(item);
    const candidateId = stringValue(report?.candidateId) ?? 'candidate';
    return (asArray(report?.observations) ?? []).map((observationItem) => {
      const observation = asRecord(observationItem);
      if (!observation) return observationItem;
      const id = stringValue(observation.criticId) ?? 'critic';
      return `${candidateId} - ${id}\n${observation.message ?? ''}`;
    });
  });
}

function editorialCritiqueAttempts(reports: unknown[]): unknown[] {
  return reports.flatMap((item) => {
    const report = asRecord(item);
    const candidateId = stringValue(report?.candidateId) ?? 'candidate';
    return (asArray(report?.attempts) ?? []).map((attemptItem) => {
      const attempt = asRecord(attemptItem);
      if (!attempt) return attemptItem;
      return `${candidateId} - ${attempt.label ?? 'attempt'}: ${attempt.status ?? 'unknown'} - ${attempt.model ?? 'no model'}${attempt.backup ? ' - backup' : ''}`;
    });
  });
}

function articleDossierSection(payload: Record<string, unknown>): TraceSemanticSection {
  const cards = asArray(payload.cards) ?? [];
  const metadata = asRecord(payload.metadata);
  const byType = asRecord(metadata?.byType);
  const cardValues = cards.flatMap((item) => {
    const card = asRecord(item);
    if (!card) return [];
    return `${stringValue(card.type) ?? 'card'} - ${stringValue(card.title) ?? stringValue(card.id) ?? 'untitled'}: ${shortValue(card.summary)}`;
  });
  return {
    id: 'article-dossier',
    title: 'Article dossier',
    fields: compactFields([
      ['Cards', metadata?.cardCount ?? cards.length],
      ['By type', byType],
      ['Key cards', cardValues.slice(0, 10)],
      ['Unresolved risks/questions', cardValues.filter((value) => value.includes('risk') || value.includes('openQuestion')).slice(0, 6)]
    ])
  };
}

function contextPacksSection(payload: Record<string, unknown>): TraceSemanticSection {
  const roleValues = Object.entries(payload).flatMap(([role, value]) => {
    const pack = asRecord(value);
    if (!pack) return [];
    const items = asArray(pack.items) ?? [];
    return `${role}: ${items.length} items`;
  });
  const itemValues = Object.entries(payload).flatMap(([role, value]) => {
    const pack = asRecord(value);
    return (asArray(pack?.items) ?? []).slice(0, 6).flatMap((item) => {
      const record = asRecord(item);
      if (!record) return [];
      return `${role} - ${stringValue(record.cardId) ?? 'card'}: ${shortValue(record.reason)} / ${shortValue(record.title)}`;
    });
  });
  return {
    id: 'context-packs',
    title: 'Context packs',
    fields: compactFields([
      ['Roles', roleValues],
      ['Included cards', itemValues.slice(0, 18)]
    ])
  };
}

function sourceIntentSection(payload: Record<string, unknown>, sourcesOrigin?: string): TraceSemanticSection {
  const items = asArray(payload.items) ?? [];
  return {
    id: 'sourceIntent',
    title: 'Source intent',
    fields: compactFields([
      ['Sources origin', sourcesOrigin],
      ['Items', items.length],
      ['URLs', items.filter((item) => asRecord(item)?.kind === 'url').map(sourceIntentValue)],
      ['Research requests', items.filter((item) => asRecord(item)?.kind === 'researchRequest').map(sourceIntentValue)],
      ['Proof needs', items.filter((item) => asRecord(item)?.kind === 'proofNeed').map(sourceIntentValue)],
      ['Exclusions', items.filter((item) => asRecord(item)?.kind === 'exclusion').map(sourceIntentValue)],
      ['Warnings', payload.warnings]
    ])
  };
}

function draftRunBudgetSection(payload: Record<string, unknown>, envelope: Record<string, unknown>): TraceSemanticSection {
  const caps = asRecord(payload.caps);
  const budgetTrace = asRecord(envelope.budgetTrace) ?? asRecord(asRecord(envelope.metadata)?.budgetTrace);
  return {
    id: 'draftRunBudget',
    title: 'DraftRun budget',
    fields: compactFields([
      ['Research depth', payload.researchDepth],
      ['Execution mode', payload.executionMode],
      ['Caps', caps ? Object.entries(caps).map(([key, value]) => `${key}: ${value}`) : null],
      ['Used counts', asRecord(budgetTrace?.usedCounts) ? Object.entries(asRecord(budgetTrace?.usedCounts) ?? {}).map(([key, value]) => `${key}: ${value}`) : null],
      ['Cap hits', asRecord(budgetTrace?.capHits) ? Object.entries(asRecord(budgetTrace?.capHits) ?? {}).map(([key, value]) => `${key}: ${value}`) : null],
      ['Budget skipped', asArray(budgetTrace?.budgetSkipped)?.map(publicEvidenceAttemptValue)],
      ['Trimmed evidence', asArray(asRecord(envelope.metadata)?.trimmedEvidenceItems)?.map(publicEvidenceItemValue)],
      ['Trimmed external claims', asArray(envelope.budgetTrimmedExternalClaims)?.map(sourceLedgerExternalClaimValue)]
    ])
  };
}

function sourceIntentValue(item: unknown): unknown {
  const record = asRecord(item);
  return record?.instruction ?? record?.value ?? record?.raw;
}

function researchPlanSection(payload: Record<string, unknown>): TraceSemanticSection {
  return {
    id: 'researchPlan',
    title: 'Research plan',
    fields: compactFields([
      ['Questions', payload.researchQuestions],
      ['Source targets', payload.sourceTargets],
      ['Verification tasks', asArray(payload.verificationTasks)?.map((item) => {
        const task = asRecord(item);
        return task ? `${task.kind}: ${task.instruction}` : null;
      })],
      ['Query candidates', payload.queryCandidates],
      ['Exclusions', payload.exclusions],
      ['Warnings', payload.warnings]
    ])
  };
}

function publicEvidenceSection(payload: Record<string, unknown>): TraceSemanticSection {
  const attempts = asArray(payload.attempts) ?? [];
  const items = asArray(payload.items) ?? [];
  const warnings = asArray(payload.warnings) ?? [];
  const rejected = attempts.flatMap((item) => asArray(asRecord(asRecord(item)?.metadata)?.rejectedCitations) ?? []);
  const enrichedLedger = asRecord(payload.enrichedSourceLedger);
  const ledgerMetadata = asRecord(enrichedLedger?.metadata);
  const synthesis = asRecord(payload.evidenceSynthesis);
  const synthesisMetadata = asRecord(synthesis?.metadata);
  return {
    id: 'publicEvidence',
    title: 'Public evidence',
    fields: compactFields([
      ['Evidence items', items.length],
      ['Internal ledger claims', ledgerMetadata?.internalClaimCount],
      ['External ledger claims', ledgerMetadata?.externalClaimCount],
      ['Synthesis external claims', synthesisMetadata?.externalClaimCount],
      ['Synthesis warnings', synthesisMetadata?.warningCount],
      ['Attempts', attempts.map(publicEvidenceAttemptValue)],
      ['Extracted evidence', items.map(publicEvidenceItemValue)],
      ['Rejected citations', rejected.map(publicEvidenceRejectedCitationValue)],
      ['Warnings', warnings.map(publicEvidenceWarningValue)],
      ['Budget skipped', asArray(asRecord(asRecord(payload.metadata)?.budgetTrace)?.budgetSkipped)?.map(publicEvidenceAttemptValue)],
      ['Trimmed evidence', asArray(asRecord(payload.metadata)?.trimmedEvidenceItems)?.map(publicEvidenceItemValue)],
      ['Search provider', asRecord(payload.metadata)?.searchProvider],
      ['Search model', asRecord(payload.metadata)?.model],
      ['Search AiRun IDs', payload.aiRunIds]
    ])
  };
}

function publicEvidenceAttemptValue(item: unknown): unknown {
  const attempt = asRecord(item);
  if (!attempt) return item;
  const metadata = asRecord(attempt.metadata);
  const query = stringValue(metadata?.builtQuery);
  return `${attempt.kind}: ${attempt.status} · target ${attempt.target}${query ? `\nquery: ${query}` : ''}`;
}

function publicEvidenceItemValue(item: unknown): unknown {
  const evidence = asRecord(item);
  if (!evidence) return item;
  return `${evidence.sourceTitle} · ${evidence.allowedUse} · ${evidence.snippet}`;
}

function publicEvidenceWarningValue(item: unknown): unknown {
  const warning = asRecord(item);
  if (!warning) return item;
  return `${warning.code}: ${warning.message}`;
}

function publicEvidenceRejectedCitationValue(item: unknown): unknown {
  const citation = asRecord(item);
  if (!citation) return item;
  return `${citation.reason}: ${citation.title} · ${citation.url}`;
}

function publicEvidenceSearchSection(
  requestPayload: Record<string, unknown>,
  resultPayload: Record<string, unknown>
): TraceSemanticSection {
  const providerRequest = asRecord(requestPayload.providerRequest);
  const originalTask = asRecord(requestPayload.originalTask);
  return {
    id: 'publicEvidenceSearch',
    title: 'Public evidence search',
    fields: compactFields([
      ['Built query', requestPayload.builtQuery],
      ['Task instruction', originalTask?.instruction],
      ['Technical target', requestPayload.target],
      ['Source target', requestPayload.sourceTarget],
      ['Exclusions', requestPayload.exclusions],
      ['Accepted citations', asArray(resultPayload.acceptedCitations)?.map(publicEvidenceCitationValue)],
      ['Rejected citations', asArray(resultPayload.rejectedCitations)?.map(publicEvidenceRejectedCitationValue)],
      ['Evidence items', asArray(resultPayload.evidenceItems)?.map(publicEvidenceItemValue)],
      ['Provider model', providerRequest?.model]
    ])
  };
}

function evidenceSynthesisSection(payload: Record<string, unknown>): TraceSemanticSection {
  const claims = asArray(payload.externalClaims) ?? [];
  const warnings = asArray(payload.warnings) ?? [];
  return {
    id: 'evidenceSynthesis',
    title: 'Evidence synthesis',
    fields: compactFields([
      ['Source', payload.source],
      ['External claims', claims.map(externalEvidenceClaimValue)],
      ['Warnings', warnings.map(publicEvidenceWarningValue)],
      ['Decisions', payload.decisions],
      ['Claim count', asRecord(payload.metadata)?.externalClaimCount],
      ['Warning count', asRecord(payload.metadata)?.warningCount]
    ])
  };
}

function evidenceInterpretationSection(payload: Record<string, unknown>, envelope: Record<string, unknown>): TraceSemanticSection {
  const metadata = asRecord(payload.metadata);
  return {
    id: 'evidenceInterpretation',
    title: 'Evidence interpretation',
    fields: compactFields([
      ['Source', envelope.source],
      ['Fallback', envelope.fallbackUsed === true ? 'yes' : 'no'],
      ['Attempts', asArray(envelope.attempts)?.map(jsonStepAttemptValue)],
      ['Implications', asArray(payload.implications)?.map(evidenceInterpretationItemValue)],
      ['Tensions', asArray(payload.tensions)?.map(evidenceInterpretationItemValue)],
      ['Usable examples', asArray(payload.usableExamples)?.map(evidenceInterpretationItemValue)],
      ['Limits', asArray(payload.limits)?.map(evidenceInterpretationItemValue)],
      ['Forbidden overclaims', asArray(payload.forbiddenOverclaims)?.map(evidenceInterpretationItemValue)],
      ['Reader value hooks', asArray(payload.readerValueHooks)?.map(evidenceInterpretationItemValue)],
      ['Rejected evidence uses', asArray(payload.rejectedEvidenceUses)?.map(evidenceInterpretationItemValue)],
      ['Warnings', asArray(payload.warnings)?.map(publicEvidenceWarningValue)],
      ['Counts', metadata ? `implications ${metadata.implicationCount ?? 0}; examples ${metadata.usableExampleCount ?? 0}; limits ${metadata.limitCount ?? 0}; warnings ${metadata.warningCount ?? 0}` : null]
    ])
  };
}

function evidenceInterpretationItemValue(item: unknown): unknown {
  const record = asRecord(item);
  if (!record) return item;
  return [
    `${record.id} - ${record.allowedUse} - ${record.confidence}`,
    record.title,
    record.summary,
    asArray(record.claimIds)?.length ? `claims: ${formatList(asArray(record.claimIds) ?? [])}` : '',
    asArray(record.publicEvidenceItemIds)?.length ? `evidence: ${formatList(asArray(record.publicEvidenceItemIds) ?? [])}` : '',
    asArray(record.ruleIds)?.length ? `rules: ${formatList(asArray(record.ruleIds) ?? [])}` : '',
    record.reason ? `reason: ${record.reason}` : ''
  ].filter(Boolean).join('\n');
}

function sourceLedgerSection(payload: Record<string, unknown>): TraceSemanticSection {
  const metadata = asRecord(payload.metadata);
  const claims = asArray(payload.claims) ?? [];
  const externalClaims = claims.filter((item) => asRecord(item)?.type === 'externalEvidenceClaim');
  return {
    id: 'sourceLedger',
    title: metadata?.externalClaimCount ? 'Enriched source ledger' : 'Source ledger',
    fields: compactFields([
      ['Claims', metadata?.claimCount ?? claims.length],
      ['Internal claims', metadata?.internalClaimCount],
      ['External claims', metadata?.externalClaimCount ?? externalClaims.length],
      ['Warnings', metadata?.warningCount],
      ['External claim list', externalClaims.map(sourceLedgerExternalClaimValue)]
    ])
  };
}

function externalEvidenceClaimValue(item: unknown): unknown {
  const claim = asRecord(item);
  if (!claim) return item;
  return `${claim.publicEvidenceItemId} В· ${claim.allowedUse} В· ${claim.statement}`;
}

function sourceLedgerExternalClaimValue(item: unknown): unknown {
  const claim = asRecord(item);
  const provenance = asRecord(claim?.provenance);
  if (!claim) return item;
  return `${claim.id} В· ${claim.allowedUse} В· ${provenance?.sourceTitle ?? 'public source'}\n${claim.statement}`;
}

function publicEvidenceCitationValue(item: unknown): unknown {
  const citation = asRecord(item);
  if (!citation) return item;
  return `${citation.title} · ${citation.url}`;
}

function rhetoricalPlanAttemptsSection(payload: Record<string, unknown>): TraceSemanticSection {
  return {
    id: 'rhetorical-plan-attempts',
    title: 'Rhetorical plan attempts',
    fields: compactFields([
      ['Source', payload.source],
      ['Fallback', payload.fallbackUsed === true ? 'yes' : 'no'],
      ['Error', payload.error],
      ['Attempts', asArray(payload.attempts)?.map(jsonStepAttemptValue)]
    ])
  };
}

function rhetoricalPlanSections(payload: Record<string, unknown>): TraceSemanticSection[] {
  const plans = asArray(payload.plans) ?? [];
  if (plans.length === 0) {
    return [{ id: 'rhetoricalPlans', title: 'Rhetorical plans', fields: objectToFields(payload) }];
  }
  return plans.map((item, index) => {
    const plan = asRecord(item) ?? {};
    return {
      id: `rhetorical-plan-${stringValue(plan.id) ?? index + 1}`,
      title: `Rhetorical plan ${index + 1}`,
      fields: compactFields([
        ['Plan ID', plan.id],
        ['Title', plan.title],
        ['Angle', plan.angle],
        ['Opening move', plan.openingMove],
        ['Moves', plan.moves],
        ['Claims to use', plan.claimsToUse],
        ['Claims to avoid', plan.claimIdsToAvoid],
        ['Required rules', plan.requiredRuleIds],
        ['Size intent', plan.sizeIntent],
        ['CTA route', plan.ctaRoute],
        ['Risks', plan.risks],
        ['Why this plan', plan.whyThisPlan]
      ])
    };
  });
}

function ruleRegistrySection(payload: Record<string, unknown>): TraceSemanticSection {
  const metadata = asRecord(payload.metadata);
  const rules = asArray(payload.rules) ?? [];
  return {
    id: 'ruleRegistry',
    title: 'Rule registry',
    fields: compactFields([
      ['Version', payload.version],
      ['Rules', metadata?.ruleCount ?? rules.length],
      ['By severity', metadata?.bySeverity],
      ['By category', metadata?.byCategory],
      ['Validator bindings', metadata?.byValidatorType],
      ['Feasibility', metadata?.feasibilityStatus],
      ['Post contract', metadata?.postContractStatus],
      ['Key rules', rules.slice(0, 8).map((item) => {
        const rule = asRecord(item);
        if (!rule) return null;
        const binding = asRecord(rule.binding);
        return `${rule.id} · ${rule.severity} · ${binding?.validatorType}: ${rule.title}`;
      }).filter(Boolean)]
    ])
  };
}

function publicationSizeSection(payload: Record<string, unknown>): TraceSemanticSection {
  return {
    id: 'publicationSizeContract',
    title: 'Publication size contract',
    fields: compactFields([
      ['Profile', payload.title ?? payload.profileId],
      ['Platform', payload.platform],
      ['Kind', payload.publicationKind],
      ['Chars', `${payload.minChars}-${payload.maxChars} target ${payload.targetChars}`],
      ['Hard max', payload.hardMaxChars],
      ['Paragraphs', payload.paragraphRange],
      ['Sections', payload.sectionRange],
      ['Density', payload.density],
      ['Fabula scale', payload.fabulaSizeIntent],
      ['Source', payload.source]
    ])
  };
}

function feasibilitySection(payload: Record<string, unknown>): TraceSemanticSection {
  return {
    id: 'feasibility',
    title: 'Feasibility report',
    fields: compactFields([
      ['Status', payload.status],
      ['Summary', payload.summary],
      ['Blocked', payload.blocked],
      ['Allowed claims', payload.allowedClaimIds],
      ['Qualified claims', payload.qualifiedClaimIds],
      ['Findings', asArray(payload.findings)?.map((item) => asRecord(item)?.detail ?? asRecord(item)?.title)]
    ])
  };
}

function postContractSection(payload: Record<string, unknown>): TraceSemanticSection {
  const topic = asRecord(payload.topic);
  const fabula = asRecord(payload.fabula);
  return {
    id: 'postContract',
    title: 'Post contract',
    fields: compactFields([
      ['Status', payload.status],
      ['Title', payload.title],
      ['Thesis', payload.thesis],
      ['Audience', payload.audience],
      ['Value', payload.value],
      ['Goal', payload.goal],
      ['CTA', payload.cta],
      ['Platform', payload.platform],
      ['Publication', [payload.date, payload.time].filter(Boolean).join(' · ')],
      ['Topic', topic?.title ?? topic?.id],
      ['Fabula', fabula?.title ?? fabula?.id],
      ['Claims', payload.claims],
      ['Forbidden moves', payload.forbiddenMoves],
      ['Evidence obligations', payload.evidenceObligations],
      ['Fabula obligations', payload.fabulaObligations],
      ['Risk notes', payload.riskNotes],
      ['Reason', payload.reason]
    ])
  };
}

function jsonStepAttemptValue(item: unknown): unknown {
  const attempt = asRecord(item);
  if (!attempt) return item;
  const validation = attempt.validation ? `\n${displayValue(attempt.validation)}` : '';
  return `${attempt.label}: ${attempt.status} · ${attempt.model}${attempt.backup ? ' · backup' : ''}${validation}`;
}

function materialPlanSection(payload: Record<string, unknown>, envelope: Record<string, unknown>): TraceSemanticSection {
  const accountability = asRecord(envelope.evidenceAccountability) ?? asRecord(payload.evidenceAccountability);
  const source = {
    availableEvidence: payload.availableEvidence ?? envelope.availableEvidence,
    rejectedEvidence: payload.rejectedEvidence ?? envelope.rejectedEvidence,
    rejectionReasons: payload.rejectionReasons ?? envelope.rejectionReasons,
    claimsRequiringAttribution: payload.claimsRequiringAttribution ?? envelope.claimsRequiringAttribution,
    qualifiedClaims: payload.qualifiedClaims ?? envelope.qualifiedClaims,
    missingEvidence: payload.missingEvidence ?? envelope.missingEvidence,
    riskyClaims: payload.riskyClaims ?? envelope.riskyClaims,
    groundingPlan: payload.groundingPlan ?? envelope.groundingPlan,
    sourceNotes: payload.sourceNotes ?? envelope.sourceNotes,
    openQuestions: payload.openQuestions ?? envelope.openQuestions
  };
  return {
    id: 'materialPlan',
    title: 'Material plan',
    fields: compactFields([
      ['Attempts', asArray(envelope.attempts)?.map(materialPlanAttemptValue) ?? asArray(payload.attempts)?.map(materialPlanAttemptValue)],
      ['Usable evidence candidates', asArray(envelope.usableEvidenceCandidates)?.map(materialPlanEvidenceCandidateValue) ?? asArray(payload.usableEvidenceCandidates)?.map(materialPlanEvidenceCandidateValue)],
      ['Available evidence', source.availableEvidence],
      ['Rejected evidence', source.rejectedEvidence],
      ['Rejection reasons', source.rejectionReasons],
      ['Claims requiring attribution', source.claimsRequiringAttribution],
      ['Qualified claims', source.qualifiedClaims],
      ['Accountability', accountability ? materialPlanAccountabilityValue(accountability) : null],
      ['Missing evidence', source.missingEvidence],
      ['Risky claims', source.riskyClaims],
      ['Grounding plan', source.groundingPlan],
      ['Source notes', source.sourceNotes],
      ['Open questions', source.openQuestions]
    ])
  };
}

function materialPlanAttemptValue(item: unknown): unknown {
  const attempt = asRecord(item);
  if (!attempt) return item;
  const validation = asRecord(attempt.validation);
  const invalidReasons = asArray(validation?.invalidReasons)?.join('; ');
  return `${attempt.label}: ${attempt.status} · ${attempt.model}${attempt.backup ? ' · backup' : ''}${invalidReasons ? `\n${invalidReasons}` : ''}`;
}

function materialPlanEvidenceCandidateValue(item: unknown): unknown {
  const candidate = asRecord(item);
  if (!candidate) return item;
  return `${candidate.claimId} · ${candidate.allowedUse} · ${candidate.sourceTitle || candidate.source}\n${candidate.statement}`;
}

function materialPlanAccountabilityValue(payload: Record<string, unknown>): string {
  return [
    `valid: ${payload.valid}`,
    `accepted: ${displayValue(payload.acceptedEvidence)}`,
    `rejected: ${displayValue(payload.rejectedEvidence)}`,
    `invalid: ${displayValue(payload.invalidReasons)}`
  ].filter((item) => !item.endsWith(': ')).join('\n');
}

function strategySection(payload: Record<string, unknown>): TraceSemanticSection {
  return {
    id: 'strategy',
    title: 'Draft strategy',
    fields: compactFields([
      ['Thesis angle', payload.thesisAngle],
      ['Opening move', payload.openingMove],
      ['Argument sequence', payload.argumentSequence],
      ['Fabula usage', payload.fabulaUsage],
      ['CTA plan', payload.ctaPlan],
      ['Forbidden moves', payload.forbiddenMoves],
      ['Tone notes', payload.toneNotes]
    ])
  };
}

function candidateSection(payload: Record<string, unknown>, title: string): TraceSemanticSection {
  return {
    id: `candidate-${stringValue(payload.id) ?? title}`,
    title,
    fields: compactFields([
      ['Direction', asRecord(payload.direction)?.label ?? asRecord(payload.direction)?.id],
      ['Rhetorical plan', payload.rhetoricalPlanId ?? asRecord(payload.direction)?.rhetoricalPlanId],
      ['Title', payload.title],
      ['Rationale', payload.rationale],
      ['Used evidence', payload.usedEvidence],
      ['Rule coverage', payload.ruleCoverage],
      ['Risks', payload.risks],
      ['Weaknesses', payload.weaknesses],
      ['Source', payload.source],
      ['AiRun ID', payload.aiRunId]
    ]),
    body: stringValue(payload.body) ?? undefined
  };
}

function selectionSection(payload: Record<string, unknown>): TraceSemanticSection {
  return {
    id: 'selection',
    title: 'Candidate selection',
    fields: compactFields([
      ['Selected candidate', payload.selectedCandidateId],
      ['Rationale', payload.rationale],
      ['Unresolved risks', payload.unresolvedRisks],
      ['Scorecard', payload.scorecard]
    ])
  };
}

function extractMessages(requestPayload: Record<string, unknown>): TraceMessage[] {
  const providerRequest = asRecord(requestPayload.providerRequest);
  const rawMessages =
    asArray(providerRequest?.messages) ??
    asArray(requestPayload.promptMessages) ??
    asArray(requestPayload.messages) ??
    [];

  return rawMessages.map((rawMessage, index) => {
    const message = asRecord(rawMessage);
    const role = normalizeRole(stringValue(message?.role));
    const content = prettyTraceValue(message?.content ?? rawMessage);
    return {
      id: `message-${index}`,
      index: index + 1,
      role,
      preview: createPreview(content),
      content
    };
  });
}

function stepKeyForAiRun(aiRun: AiRunTrace): string {
  const step = rawStepKeyForAiRun(aiRun);
  if (step === 'draftCandidate') return 'draft';
  if (step === 'sourceIntentResearchPlan') return 'sourceIntent';
  if (step === 'publicEvidenceSearch') return 'publicEvidence';
  if (step === 'externalEvidenceSynthesis') return 'publicEvidence';
  if (step === 'evidenceInterpretation') return 'rulePack';
  if (step === 'editorialCritique') return 'validation';
  if (step === 'alternativeAngleRoute') return 'validation';
  if (step === 'alternativeAngleCandidate') return 'validation';
  return step ?? 'unknown';
}

function rawStepKeyForAiRun(aiRun: AiRunTrace): string | null {
  const requestPayload = aiRun.requestPayload ?? {};
  const resultPayload = aiRun.resultPayload ?? {};
  return stringValue(requestPayload.draftRunStep) ?? stringValue(resultPayload.draftRunStep);
}

function aiRunStepLabel(aiRun: AiRunTrace): string {
  return stepLabel(rawStepKeyForAiRun(aiRun) ?? stepKeyForAiRun(aiRun));
}

function stepLabel(step: string): string {
  const labels: Record<string, string> = {
    context: 'Context',
    sourceIntent: 'Source intent',
    sourceIntentResearchPlan: 'Source research plan',
    publicEvidence: 'Public evidence',
    publicEvidenceSearch: 'Public evidence search',
    externalEvidenceSynthesis: 'External evidence synthesis',
    evidenceInterpretation: 'Evidence interpretation',
    feasibility: 'Feasibility',
    postContract: 'Post contract',
    rulePack: 'Rule pack',
    materialPlan: 'Material plan',
    strategy: 'Draft strategy',
    rhetoricalPlans: 'Rhetorical plans',
    draft: 'Draft candidates',
    draftCandidate: 'Draft candidate',
    validation: 'Validation',
    editorialCritique: 'Editorial critique',
    alternativeAngleRoute: 'Alternative angle route',
    alternativeAngleCandidate: 'Alternative angle candidate',
    complete: 'Complete',
    draftGeneration: 'Draft generation',
    unknown: 'Unknown step'
  };
  return labels[step] ?? step;
}

function compactFields(entries: Array<[string, unknown]>): TraceField[] {
  return entries
    .map(([label, value]) => ({ label, value: displayValue(value) }))
    .filter((field) => field.value.length > 0);
}

function objectToFields(payload: Record<string, unknown>): TraceField[] {
  return Object.entries(payload).map(([label, value]) => ({ label, value: displayValue(value) }));
}

function formatList(values: unknown[]): string {
  return values.map((value) => displayValue(value)).filter(Boolean).join(', ') || 'none';
}

function formatMarkerMap(value: Record<string, unknown> | null): string {
  if (!value) return 'none';
  const rows = Object.entries(value)
    .map(([claimId, markers]) => `${claimId}: ${displayValue(markers).replace(/\n/g, ', ')}`)
    .filter((row) => !row.endsWith(': '));
  return rows.join('\n') || 'none';
}

function displayValue(value: unknown): string {
  if (value == null) return '';
  if (typeof value === 'string') return value;
  if (typeof value === 'number' || typeof value === 'boolean') return String(value);
  if (Array.isArray(value)) return value.map((item) => displayValue(item)).filter(Boolean).join('\n');
  return JSON.stringify(value, null, 2);
}

function shortValue(value: unknown, limit = 140): string {
  const text = displayValue(value).replace(/\s+/g, ' ').trim();
  return text.length > limit ? `${text.slice(0, limit)}...` : text;
}

function createPreview(content: string): string {
  const compact = content.replace(/\s+/g, ' ').trim();
  return compact.length > 140 ? `${compact.slice(0, 140)}...` : compact;
}

function normalizeRole(role: string | null): TraceRole {
  if (role === 'system' || role === 'user' || role === 'assistant' || role === 'tool') return role;
  return 'unknown';
}

function asRecord(value: unknown): Record<string, unknown> | null {
  return value && typeof value === 'object' && !Array.isArray(value) ? value as Record<string, unknown> : null;
}

function asArray(value: unknown): unknown[] | null {
  return Array.isArray(value) ? value : null;
}

function stringValue(value: unknown): string | null {
  return typeof value === 'string' && value.trim().length > 0 ? value : null;
}
