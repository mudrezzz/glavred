import type { EditorDecisionMachineTraceSummary, PostDraft } from '../domain/editorialWorkspace';
import { fetchRunTrace } from './runTraceClient';

export async function loadEditorDecisionTraceSummary(draft: PostDraft): Promise<EditorDecisionMachineTraceSummary> {
  const draftRunId = draft.generation?.draftRunId ?? null;
  if (!draftRunId) {
    return unavailableTrace(null);
  }

  try {
    const bundle = await fetchRunTrace(draftRunId);
    if (bundle.kind !== 'draftRun') return unavailableTrace(draftRunId);

    const validation = stepArtifact(bundle.draftRun.steps, 'validation');
    const rankingRevision = asRecord(validation?.rankingRevision);
    const finalQualityGate = asRecord(rankingRevision?.finalQualityGate);
    const revisionLoop = asRecord(rankingRevision?.revisionLoop);
    const alternativeAngleTournament = asRecord(validation?.alternativeAngleTournament);

    return {
      draftRunId,
      traceStatus: 'available',
      finalQualityGate,
      revisionLoop,
      alternativeAngleTournament,
      validationSummary: summarizeValidation(validation),
      unresolvedRisks: collectUnresolvedRisks(finalQualityGate, revisionLoop, validation)
    };
  } catch {
    return unavailableTrace(draftRunId);
  }
}

function unavailableTrace(draftRunId: string | null): EditorDecisionMachineTraceSummary {
  return {
    draftRunId,
    traceStatus: 'unavailable',
    unresolvedRisks: []
  };
}

function stepArtifact(steps: Array<{ key: string; artifactPayload: Record<string, unknown> | null }>, key: string) {
  return steps.find((step) => step.key === key)?.artifactPayload ?? null;
}

function summarizeValidation(validation: Record<string, unknown> | null | undefined): Record<string, unknown> | null {
  if (!validation) return null;
  const candidateReports = Array.isArray(validation.candidateReports) ? validation.candidateReports : [];
  const llmReport = asRecord(validation.llmValidationReport);
  const llmReports = Array.isArray(llmReport?.candidateReports) ? llmReport.candidateReports : [];
  return {
    deterministicCandidateCount: candidateReports.length,
    llmCandidateCount: llmReports.length,
    status: validation.status ?? llmReport?.status ?? null
  };
}

function collectUnresolvedRisks(
  finalQualityGate: Record<string, unknown> | null,
  revisionLoop: Record<string, unknown> | null,
  validation: Record<string, unknown> | null | undefined
): string[] {
  const risks = [
    ...strings(finalQualityGate?.unresolvedRisks),
    ...strings(finalQualityGate?.remainingIssues),
    ...strings(revisionLoop?.unresolvedGoals),
    ...strings(validation?.warnings)
  ];
  return Array.from(new Set(risks)).slice(0, 8);
}

function asRecord(value: unknown): Record<string, unknown> | null {
  return value && typeof value === 'object' && !Array.isArray(value) ? value as Record<string, unknown> : null;
}

function strings(value: unknown): string[] {
  if (!Array.isArray(value)) return [];
  return value.map((item) => String(item).trim()).filter(Boolean);
}
