import type { AiRunTrace } from '../../infrastructure/aiRunTraceClient';
import type { DraftRunTraceStep } from '../../infrastructure/runTraceClient';
import type {
  TraceChildCall,
  TraceDetail,
  TraceField,
  TraceScorecardModel,
  TraceScorecardRow,
  TraceSemanticSection
} from './runTraceViewModel';

type DraftCandidateTrace = {
  id: string;
  index: number;
  title: string;
  body: string;
  rhetoricalPlanId: string;
  source: string;
  aiRunId: string;
  fallback: string;
  rationale: string;
  risks: string;
  weaknesses: string;
  score: Record<string, unknown> | null;
  selected: boolean;
};

export type DraftCandidateTraceArtifacts = {
  childCalls: TraceChildCall[];
  details: TraceDetail[];
  semanticSections: TraceSemanticSection[];
};

export function buildDraftCandidateTraceArtifacts(
  step: DraftRunTraceStep,
  childAiRuns: AiRunTrace[]
): DraftCandidateTraceArtifacts {
  if (step.key !== 'draft') {
    return { childCalls: [], details: [], semanticSections: [] };
  }
  const payload = asRecord(step.artifactPayload) ?? {};
  const candidates = draftCandidatesFromPayload(payload);
  const selection = asRecord(payload.selection);
  const scorecard = scorecardFromSelection(selection);
  const selectedCandidateId = stringValue(selection?.selectedCandidateId);
  const candidateTraces = candidates.map((candidate, index) => {
    const id = stringValue(candidate.id) ?? `candidate-${index + 1}`;
    return candidateTraceFromPayload(candidate, index + 1, scorecard.get(id) ?? null, selectedCandidateId === id);
  });

  if (candidateTraces.length === 0 && !selection) {
    return { childCalls: [], details: [], semanticSections: [] };
  }

  const details = candidateTraces.map((candidate) => candidateDetail(candidate));
  const childCalls = candidateTraces.map((candidate) => candidateChildCall(candidate, childAiRuns));
  const semanticSections = candidateTraces.map((candidate) => candidateSemanticSection(candidate));

  if (scorecard.size > 0) {
    details.push(scorecardDetail(scorecard, candidateTraces, selectedCandidateId));
    childCalls.push(scorecardChildCall(scorecard, selectedCandidateId));
    semanticSections.push(scorecardSemanticSection(scorecard, candidateTraces, selectedCandidateId));
  }

  if (selection) {
    details.push(selectionDetail(selection, candidateTraces));
    childCalls.push(selectionChildCall(selection, candidateTraces));
    semanticSections.push(selectionSemanticSection(selection, candidateTraces));
  }

  return { childCalls, details, semanticSections };
}

export function buildDraftCandidateSemanticSections(payload: Record<string, unknown>): TraceSemanticSection[] {
  const fakeStep: DraftRunTraceStep = {
    key: 'draft',
    status: 'succeeded',
    title: 'Draft',
    artifactPayload: payload,
    error: null,
    startedAt: null,
    completedAt: null
  };
  return buildDraftCandidateTraceArtifacts(fakeStep, []).semanticSections;
}

function draftCandidatesFromPayload(payload: Record<string, unknown>): Record<string, unknown>[] {
  return (asArray(payload.candidates) ?? []).map(asRecord).filter((item): item is Record<string, unknown> => Boolean(item));
}

function candidateTraceFromPayload(
  payload: Record<string, unknown>,
  index: number,
  score: Record<string, unknown> | null,
  selected: boolean
): DraftCandidateTrace {
  const direction = asRecord(payload.direction);
  return {
    id: stringValue(payload.id) ?? `candidate-${index}`,
    index,
    title: stringValue(payload.title) ?? `Кандидат ${index}`,
    body: stringValue(payload.body) ?? '',
    rhetoricalPlanId: stringValue(payload.rhetoricalPlanId) ?? stringValue(direction?.rhetoricalPlanId) ?? stringValue(direction?.id) ?? '',
    source: stringValue(payload.source) ?? 'unknown',
    aiRunId: stringValue(payload.aiRunId) ?? '',
    fallback: payload.fallbackUsed === true ? 'yes' : payload.fallbackUsed === false ? 'no' : 'unknown',
    rationale: stringValue(payload.rationale) ?? '',
    risks: displayValue(payload.risks),
    weaknesses: displayValue(payload.weaknesses),
    score,
    selected
  };
}

function scorecardFromSelection(selection: Record<string, unknown> | null): Map<string, Record<string, unknown>> {
  const scores = new Map<string, Record<string, unknown>>();
  const rawScorecard = asArray(selection?.scorecard);
  if (rawScorecard) {
    rawScorecard.forEach((rawScore) => {
      const score = asRecord(rawScore);
      const candidateId = stringValue(score?.candidateId);
      if (score && candidateId) scores.set(candidateId, score);
    });
    return scores;
  }

  const scoreObject = asRecord(selection?.scorecard);
  const candidateId = stringValue(scoreObject?.candidateId);
  if (scoreObject && candidateId) scores.set(candidateId, scoreObject);
  return scores;
}

function candidateChildCall(candidate: DraftCandidateTrace, childAiRuns: AiRunTrace[]): TraceChildCall {
  const childRun = candidate.aiRunId ? childAiRuns.find((run) => run.id === candidate.aiRunId) : null;
  const total = displayValue(candidate.score?.total);
  return {
    id: `draft-candidate-${candidate.id}`,
    title: `${candidateLabel(candidate)}${candidate.selected ? ' · выбран' : ''}`,
    provider: childRun?.provider ?? candidate.source,
    model: childRun?.model ?? candidate.rhetoricalPlanId,
    status: candidate.selected ? 'selected' : candidate.source,
    fallback: candidate.fallback,
    detailId: candidateDetailId(candidate),
    kind: 'artifact',
    meta: compactFields([
      ['План', candidate.rhetoricalPlanId],
      ['Score', total],
      ['Source', candidate.source],
      ['AiRun', candidate.aiRunId]
    ])
  };
}

function scorecardChildCall(scorecard: Map<string, Record<string, unknown>>, selectedCandidateId: string | null): TraceChildCall {
  return {
    id: 'draft-scorecard',
    title: 'Скоринг кандидатов',
    provider: 'deterministic selector',
    model: 'scorecard',
    status: 'computed',
    fallback: 'n/a',
    detailId: 'draft-scorecard-detail',
    kind: 'artifact',
    meta: compactFields([
      ['Кандидатов', scorecard.size],
      ['Победитель', selectedCandidateId]
    ])
  };
}

function selectionChildCall(selection: Record<string, unknown>, candidates: DraftCandidateTrace[]): TraceChildCall {
  const selectedId = stringValue(selection.selectedCandidateId);
  const selected = candidates.find((candidate) => candidate.id === selectedId);
  return {
    id: 'draft-selection',
    title: 'Выбор итогового драфта',
    provider: 'deterministic selector',
    model: 'selection',
    status: selected ? 'selected' : 'computed',
    fallback: 'n/a',
    detailId: 'draft-selection-detail',
    kind: 'artifact',
    meta: compactFields([
      ['Победитель', selected ? candidateLabel(selected) : selectedId],
      ['Риски', selection.unresolvedRisks]
    ])
  };
}

function candidateDetail(candidate: DraftCandidateTrace): TraceDetail {
  return {
    id: candidateDetailId(candidate),
    title: candidateLabel(candidate),
    kicker: candidate.selected ? 'Draft candidate · выбран' : 'Draft candidate',
    summary: compactFields([
      ['Candidate ID', candidate.id],
      ['Rhetorical plan', candidate.rhetoricalPlanId],
      ['Source', candidate.source],
      ['Fallback', candidate.fallback],
      ['AiRun ID', candidate.aiRunId],
      ['Score', candidate.score?.total],
      ['Rationale', candidate.rationale],
      ['Risks', candidate.risks],
      ['Weaknesses', candidate.weaknesses]
    ]),
    sections: [candidateSemanticSection(candidate), ...(candidate.score ? [scoreSection(candidate.score, candidate.selected)] : [])],
    messages: [],
    jsonPayload: { candidate, score: candidate.score },
    rawPayload: { candidate, score: candidate.score }
  };
}

function scorecardDetail(
  scorecard: Map<string, Record<string, unknown>>,
  candidates: DraftCandidateTrace[],
  selectedCandidateId: string | null
): TraceDetail {
  return {
    id: 'draft-scorecard-detail',
    title: 'Скоринг кандидатов',
    kicker: 'Deterministic selection scorecard',
    summary: compactFields([
      ['Candidates', scorecard.size],
      ['Selected candidate', selectedCandidateId],
      ['Score spread', scoreSpread(scorecard, selectedCandidateId)]
    ]),
    sections: [scorecardSemanticSection(scorecard, candidates, selectedCandidateId)],
    messages: [],
    jsonPayload: { scorecard: Array.from(scorecard.values()), selectedCandidateId },
    rawPayload: { scorecard: Array.from(scorecard.values()), selectedCandidateId }
  };
}

function selectionDetail(selection: Record<string, unknown>, candidates: DraftCandidateTrace[]): TraceDetail {
  return {
    id: 'draft-selection-detail',
    title: 'Выбор итогового драфта',
    kicker: 'Selected draft candidate',
    summary: compactFields([
      ['Selected candidate', selection.selectedCandidateId],
      ['Selected title', candidates.find((candidate) => candidate.id === selection.selectedCandidateId)?.title],
      ['Reason', selection.reason ?? selection.rationale],
      ['Unresolved risks', selection.unresolvedRisks]
    ]),
    sections: [selectionSemanticSection(selection, candidates)],
    messages: [],
    jsonPayload: selection,
    rawPayload: { selection, candidates }
  };
}

function candidateSemanticSection(candidate: DraftCandidateTrace): TraceSemanticSection {
  return {
    id: `draft-candidate-${candidate.id}`,
    title: `${candidateLabel(candidate)}${candidate.selected ? ' · выбран' : ''}`,
    fields: compactFields([
      ['Rhetorical plan', candidate.rhetoricalPlanId],
      ['Source', candidate.source],
      ['Fallback', candidate.fallback],
      ['AiRun ID', candidate.aiRunId],
      ['Score', candidate.score?.total],
      ['Rationale', candidate.rationale],
      ['Risks', candidate.risks],
      ['Weaknesses', candidate.weaknesses]
    ]),
    body: candidate.body || undefined
  };
}

function scorecardSemanticSection(
  scorecard: Map<string, Record<string, unknown>>,
  candidates: DraftCandidateTrace[],
  selectedCandidateId: string | null
): TraceSemanticSection {
  return {
    id: 'draft-scorecard',
    title: 'Draft scorecard',
    kind: 'scorecard',
    fields: compactFields([
      ['Selected candidate', selectedCandidateId],
      ['Score spread', scoreSpread(scorecard, selectedCandidateId)]
    ]),
    scorecard: scorecardModel(scorecard, candidates, selectedCandidateId)
  };
}

function selectionSemanticSection(selection: Record<string, unknown>, candidates: DraftCandidateTrace[]): TraceSemanticSection {
  const selectedId = stringValue(selection.selectedCandidateId);
  const selected = candidates.find((candidate) => candidate.id === selectedId);
  return {
    id: 'draft-selection',
    title: 'Selected draft candidate',
    fields: compactFields([
      ['Selected candidate', selectedId],
      ['Selected title', selected?.title],
      ['Score', selected?.score?.total],
      ['Reason', selection.reason ?? selection.rationale],
      ['Unresolved risks', selection.unresolvedRisks]
    ]),
    body: selected?.body || undefined
  };
}

function scoreSection(score: Record<string, unknown>, selected: boolean): TraceSemanticSection {
  return {
    id: `score-${stringValue(score.candidateId) ?? 'candidate'}`,
    title: selected ? 'Score · selected' : 'Score',
    fields: scoreFields(score)
  };
}

function scorecardModel(
  scorecard: Map<string, Record<string, unknown>>,
  candidates: DraftCandidateTrace[],
  selectedCandidateId: string | null
): TraceScorecardModel {
  return {
    selectedCandidateId: selectedCandidateId ?? '',
    scoreSpread: scoreSpread(scorecard, selectedCandidateId),
    rows: Array.from(scorecard.values()).map((score): TraceScorecardRow => {
      const candidateId = stringValue(score.candidateId) ?? '';
      const candidate = candidates.find((item) => item.id === candidateId);
      return {
        candidateId,
        title: candidate?.title ?? candidateId,
        selected: selectedCandidateId === candidateId,
        total: displayValue(score.total),
        hardConstraintFit: displayValue(score.hardConstraintFit),
        evidenceGrounding: displayValue(score.evidenceGrounding),
        topicFit: displayValue(score.topicFit),
        fabulaFit: displayValue(score.fabulaFit),
        audienceValue: displayValue(score.audienceValue),
        riskPenalty: displayRiskPenalty(score.riskPenalty)
      };
    })
  };
}

function scoreSpread(scorecard: Map<string, Record<string, unknown>>, selectedCandidateId: string | null): string {
  if (!selectedCandidateId) return '';
  const selectedTotal = numericValue(scorecard.get(selectedCandidateId)?.total);
  if (selectedTotal == null) return '';
  const nextBest = Array.from(scorecard.entries())
    .filter(([candidateId]) => candidateId !== selectedCandidateId)
    .map(([, score]) => numericValue(score.total))
    .filter((value): value is number => value != null)
    .sort((left, right) => right - left)[0];
  if (nextBest == null) return 'no comparison';
  const spread = selectedTotal - nextBest;
  return spread >= 0 ? `+${spread}` : String(spread);
}

function displayRiskPenalty(value: unknown): string {
  const numeric = numericValue(value);
  if (numeric == null) return displayValue(value);
  return numeric === 0 ? '0' : `-${numeric}`;
}

function numericValue(value: unknown): number | null {
  return typeof value === 'number' && Number.isFinite(value) ? value : null;
}

function scoreFields(score: Record<string, unknown>): TraceField[] {
  return compactFields([
    ['Candidate ID', score.candidateId],
    ['Hard constraints', score.hardConstraintFit],
    ['Evidence grounding', score.evidenceGrounding],
    ['Topic fit', score.topicFit],
    ['Fabula fit', score.fabulaFit],
    ['Audience value', score.audienceValue],
    ['Risk penalty', score.riskPenalty],
    ['Total', score.total]
  ]);
}

function candidateDetailId(candidate: DraftCandidateTrace): string {
  return `draft-candidate-detail-${candidate.id}`;
}

function candidateLabel(candidate: DraftCandidateTrace): string {
  return `Кандидат ${candidate.index}: ${candidate.title}`;
}

function compactFields(entries: Array<[string, unknown]>): TraceField[] {
  return entries
    .map(([label, value]) => ({ label, value: displayValue(value) }))
    .filter((field) => field.value.length > 0);
}

function displayValue(value: unknown): string {
  if (value == null) return '';
  if (typeof value === 'string') return value;
  if (typeof value === 'number' || typeof value === 'boolean') return String(value);
  if (Array.isArray(value)) return value.map((item) => displayValue(item)).filter(Boolean).join('\n');
  return JSON.stringify(value, null, 2);
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
