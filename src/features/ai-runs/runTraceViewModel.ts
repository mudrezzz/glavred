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

export type TraceTimelineStep = {
  id: string;
  key: string;
  title: string;
  status: string;
  error: string | null;
  detailId: string;
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
      .filter((run) => stepKeyForAiRun(run) === step.key)
      .map((run) => {
        const detail = buildAiRunDetail(run);
        details.push(detail);
        return {
          id: run.id,
          title: stepLabel(stepKeyForAiRun(run)),
          provider: run.provider,
          model: run.model ?? 'none',
          status: run.status,
          fallback: run.fallbackUsed ? 'yes' : 'no',
          detailId: detail.id
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
  return {
    mode: 'aiRun',
    id: aiRun.id,
    title: 'AiRun trace',
    summary: [
      { label: 'Run type', value: 'AiRun' },
      { label: 'Step', value: stepLabel(step) },
      { label: 'Status', value: aiRun.status },
      { label: 'Provider', value: aiRun.provider },
      { label: 'Model', value: aiRun.model ?? 'none' },
      { label: 'Fallback', value: aiRun.fallbackUsed ? 'yes' : 'no' }
    ],
    timeline: [{
      id: `step-${step}`,
      key: step,
      title: stepLabel(step),
      status: aiRun.status,
      error: aiRun.error,
      detailId: detail.id,
      childCalls: [{
        id: aiRun.id,
        title: stepLabel(step),
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
  return {
    id: `step-detail-${step.key}`,
    title: step.title || stepLabel(step.key),
    kicker: 'Logical step',
    summary: [
      { label: 'Step', value: step.key },
      { label: 'Status', value: step.status },
      { label: 'Started', value: step.startedAt ?? 'not started' },
      { label: 'Completed', value: step.completedAt ?? 'not completed' }
    ],
    sections: sectionsFromPayload(step.key, step.artifactPayload ?? {}),
    messages: [],
    jsonPayload: step.artifactPayload ?? {},
    rawPayload: step
  };
}

function buildAiRunDetail(aiRun: AiRunTrace): TraceDetail {
  const requestPayload = aiRun.requestPayload ?? {};
  const resultPayload = aiRun.resultPayload ?? {};
  const messages = extractMessages(requestPayload);
  const step = stepKeyForAiRun(aiRun);
  return {
    id: `ai-detail-${aiRun.id}`,
    title: `${stepLabel(step)} · ${aiRun.id}`,
    kicker: 'LLM call',
    summary: [
      { label: 'AiRun ID', value: aiRun.id },
      { label: 'Provider', value: aiRun.provider },
      { label: 'Model', value: aiRun.model ?? 'none' },
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
  return sectionsFromPayload(stepKeyForAiRun(aiRun), aiRun.resultPayload ?? {});
}

function sectionsFromPayload(step: string, payload: Record<string, unknown>): TraceSemanticSection[] {
  const sections: TraceSemanticSection[] = [];
  const materialPlan = asRecord(payload.materialPlan) ?? (step === 'materialPlan' ? asRecord(payload.result) : null);
  const feasibility = asRecord(payload.feasibilityReport) ?? (step === 'feasibility' ? payload : null);
  const postContract = asRecord(payload.postContract) ?? (step === 'postContract' ? payload : null);
  const ruleRegistry = asRecord(payload.ruleRegistrySnapshot);
  const strategy = asRecord(payload.draftStrategy) ?? (step === 'strategy' ? asRecord(payload.result) : null);
  const rhetoricalPlanSet = asRecord(payload.rhetoricalPlanSet);
  const candidate = asRecord(payload.candidate);
  const candidates = asArray(payload.candidates);
  const selection = asRecord(payload.selection);
  const draft = asRecord(payload.draft);

  if (feasibility) sections.push(feasibilitySection(feasibility));
  if (postContract) {
    sections.push(postContractSection(postContract));
    const sizeContract = asRecord(postContract.publicationSizeContract);
    if (sizeContract) sections.push(publicationSizeSection(sizeContract));
  }
  if (ruleRegistry) sections.push(ruleRegistrySection(ruleRegistry));
  if (materialPlan) sections.push(materialPlanSection(materialPlan));
  if (strategy) sections.push(strategySection(strategy));
  if (rhetoricalPlanSet) sections.push(...rhetoricalPlanSections(rhetoricalPlanSet));
  if (candidate) sections.push(candidateSection(candidate, 'Draft candidate'));
  if (candidates || selection) sections.push(...buildDraftCandidateSemanticSections(payload));
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

function materialPlanSection(payload: Record<string, unknown>): TraceSemanticSection {
  return {
    id: 'materialPlan',
    title: 'Material plan',
    fields: compactFields([
      ['Available evidence', payload.availableEvidence],
      ['Missing evidence', payload.missingEvidence],
      ['Risky claims', payload.riskyClaims],
      ['Grounding plan', payload.groundingPlan],
      ['Source notes', payload.sourceNotes],
      ['Open questions', payload.openQuestions]
    ])
  };
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
  const requestPayload = aiRun.requestPayload ?? {};
  const resultPayload = aiRun.resultPayload ?? {};
  const step = stringValue(requestPayload.draftRunStep) ?? stringValue(resultPayload.draftRunStep);
  if (step === 'draftCandidate') return 'draft';
  return step ?? 'unknown';
}

function stepLabel(step: string): string {
  const labels: Record<string, string> = {
    context: 'Context',
    feasibility: 'Feasibility',
    postContract: 'Post contract',
    rulePack: 'Rule pack',
    materialPlan: 'Material plan',
    strategy: 'Draft strategy',
    rhetoricalPlans: 'Rhetorical plans',
    draft: 'Draft candidates',
    draftCandidate: 'Draft candidate',
    validation: 'Validation',
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

function displayValue(value: unknown): string {
  if (value == null) return '';
  if (typeof value === 'string') return value;
  if (typeof value === 'number' || typeof value === 'boolean') return String(value);
  if (Array.isArray(value)) return value.map((item) => displayValue(item)).filter(Boolean).join('\n');
  return JSON.stringify(value, null, 2);
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
