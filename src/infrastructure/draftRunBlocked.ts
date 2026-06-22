import type { DraftRunResponse } from './draftRunClient';

export type DraftRunBlockedInfo = {
  runId: string;
  feasibilityStatus: string;
  reason: string;
  findings: string[];
};

export function blockedInfoFromCompletedRun(run: DraftRunResponse): DraftRunBlockedInfo | null {
  const complete = run.steps.find((step) => step.key === 'complete')?.artifactPayload ?? {};
  if (complete.status !== 'blocked') return null;
  const feasibility = run.steps.find((step) => step.key === 'feasibility')?.artifactPayload ?? {};
  return {
    runId: run.id,
    feasibilityStatus: valueAsString(feasibility.status) ?? valueAsString(complete.feasibilityStatus) ?? 'blocked',
    reason: valueAsString(feasibility.summary) ?? valueAsString(complete.reason) ?? 'DraftRun was blocked before generation.',
    findings: findingsFromFeasibility(feasibility)
  };
}

function findingsFromFeasibility(payload: Record<string, unknown>): string[] {
  const findings = Array.isArray(payload.findings) ? payload.findings : [];
  return findings
    .map((item) => {
      if (!item || typeof item !== 'object') return null;
      const record = item as Record<string, unknown>;
      return valueAsString(record.detail) ?? valueAsString(record.title);
    })
    .filter((item): item is string => Boolean(item));
}

function valueAsString(value: unknown): string | null {
  return typeof value === 'string' && value.trim().length > 0 ? value : null;
}
