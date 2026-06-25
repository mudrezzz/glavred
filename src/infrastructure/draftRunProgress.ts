import type { DraftRunStepResponse } from './draftRunClient';

export type DraftRunStepOperationResponse = {
  id: string;
  kind: string;
  label: string;
  status: string;
  startedAt: string | null;
  completedAt: string | null;
  aiRunId?: string | null;
  target?: string | null;
  error?: string | null;
  notes?: string[];
};

export function currentDraftRunOperation(step: DraftRunStepResponse | null): DraftRunStepOperationResponse | null {
  const progress = step?.artifactPayload?.progress;
  if (!isRecord(progress)) return null;
  const operations = Array.isArray(progress.operations)
    ? progress.operations.filter(isRecord)
    : [];
  const currentId = typeof progress.currentOperationId === 'string' ? progress.currentOperationId : null;
  const operation = operations.find((item) => item.id === currentId)
    ?? [...operations].reverse().find((item) => item.status === 'running')
    ?? [...operations].reverse()[0];
  if (!operation) return null;
  return {
    id: stringValue(operation.id),
    kind: stringValue(operation.kind),
    label: stringValue(operation.label),
    status: stringValue(operation.status),
    startedAt: nullableString(operation.startedAt),
    completedAt: nullableString(operation.completedAt),
    aiRunId: nullableString(operation.aiRunId),
    target: nullableString(operation.target),
    error: nullableString(operation.error),
    notes: Array.isArray(operation.notes) ? operation.notes.map((item) => String(item)) : undefined
  };
}

export function draftRunStepDisplayLabel(step: DraftRunStepResponse | null): string | null {
  if (!step) return null;
  const operation = currentDraftRunOperation(step);
  return operation ? `${step.title}: ${operation.label}` : step.title;
}

function isRecord(value: unknown): value is Record<string, unknown> {
  return value !== null && typeof value === 'object' && !Array.isArray(value);
}

function stringValue(value: unknown): string {
  return typeof value === 'string' ? value : '';
}

function nullableString(value: unknown): string | null {
  return typeof value === 'string' && value.length > 0 ? value : null;
}
