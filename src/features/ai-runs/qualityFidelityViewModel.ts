import type { DraftRunTrace, RunTraceBundle } from '../../infrastructure/runTraceClient';
import type { TraceField } from './runTraceViewModel';

export type QualityFidelityViewModel = {
  technicalStatus: string;
  providerRecoveryStatus: string;
  evidenceCoverage: string;
  editorialStatus: string;
  overallVerdict: string;
  tone: 'ok' | 'warn' | 'danger' | 'neutral';
  providerFields: TraceField[];
  evidenceFields: TraceField[];
  editorialFields: TraceField[];
};

export function buildQualityFidelityViewModel(bundle: RunTraceBundle): QualityFidelityViewModel | null {
  if (bundle.kind !== 'draftRun') return null;
  const report = qualityFidelityPayload(bundle.draftRun.steps);
  if (!report) return null;
  const evidence = asRecord(report.evidenceFidelity) ?? {};
  const lifecycle = asRecord(report.issueLifecycle) ?? {};
  const providerStatus = stringValue(report.providerRecoveryStatus) ?? 'unknown';
  const editorialStatus = stringValue(report.editorialStatus) ?? 'unknown';
  const overallVerdict = stringValue(report.overallVerdict) ?? 'unknown';
  return {
    technicalStatus: stringValue(report.technicalStatus) ?? 'unknown',
    providerRecoveryStatus: providerStatus,
    evidenceCoverage: stringValue(evidence.coverageVerdict) ?? 'unknown',
    editorialStatus,
    overallVerdict,
    tone: verdictTone(overallVerdict, editorialStatus, providerStatus),
    providerFields: compactFields([
      ['Recovery', providerStatus],
      ['Operations', asArray(report.stageSummaries)?.length],
      ['Fallbacks', countStageImpact(report, 'fallbackRecovered')],
      ['Degraded', countStageImpact(report, 'stepDegraded')]
    ]),
    evidenceFields: compactFields([
      ['Coverage', evidence.coverageVerdict],
      ['Found', evidence.foundEvidenceCount],
      ['Accepted', evidence.acceptedEvidenceCount],
      ['Interpreted', evidence.interpretedEvidenceCount],
      ['Fallback interpreted', evidence.fallbackInterpretedEvidenceCount],
      ['Rejected', evidence.rejectedEvidenceCount]
    ]),
    editorialFields: compactFields([
      ['Editorial', editorialStatus],
      ['Open critical', lifecycle.openCriticalCount],
      ['Open warning', lifecycle.openWarningCount],
      ['Suppressed', lifecycle.suppressedCount],
      ['Accepted risk', lifecycle.acceptedRiskCount]
    ])
  };
}

function qualityFidelityPayload(steps: DraftRunTrace['steps']): Record<string, unknown> | null {
  const complete = stepPayload(steps, 'complete');
  const completeReport = asRecord(complete?.qualityFidelity);
  if (completeReport) return completeReport;
  const validation = stepPayload(steps, 'validation');
  const ranking = asRecord(validation?.rankingRevision);
  return asRecord(ranking?.qualityFidelity);
}

function stepPayload(steps: DraftRunTrace['steps'], key: string): Record<string, unknown> | null {
  return asRecord(steps.find((step) => step.key === key)?.artifactPayload);
}

function verdictTone(overall: string, editorial: string, provider: string): QualityFidelityViewModel['tone'] {
  if (overall === 'failed' || editorial === 'blocked' || editorial === 'needsHumanReview') return 'danger';
  if (overall === 'needsAttention' || overall === 'degradedSuccess' || provider === 'degraded') return 'warn';
  if (overall === 'cleanSuccess' || overall === 'recoveredSuccess') return 'ok';
  return 'neutral';
}

function countStageImpact(report: Record<string, unknown>, target: string): number {
  return (asArray(report.stageSummaries) ?? []).filter((item) => {
    const stage = asRecord(item);
    return stage?.retryPath === target || stage?.resultImpact === target;
  }).length;
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
