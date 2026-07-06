import { describe, expect, it } from 'vitest';
import type { RunTraceBundle } from '../../infrastructure/runTraceClient';
import { buildQualityFidelityViewModel } from './qualityFidelityViewModel';

describe('buildQualityFidelityViewModel', () => {
  it('uses complete qualityFidelity when it is stored on the complete artifact', () => {
    const model = buildQualityFidelityViewModel(draftRunBundle({
      complete: {
        qualityFidelity: qualityReport({ overallVerdict: 'recoveredSuccess', providerRecoveryStatus: 'retryRecovered' })
      }
    }));

    expect(model?.overallVerdict).toBe('recoveredSuccess');
    expect(model?.providerRecoveryStatus).toBe('retryRecovered');
    expect(model?.tone).toBe('ok');
    expect(model?.evidenceFields).toContainEqual({ label: 'Coverage', value: 'sufficient' });
  });

  it('falls back to validation rankingRevision qualityFidelity', () => {
    const model = buildQualityFidelityViewModel(draftRunBundle({
      validation: {
        rankingRevision: {
          qualityFidelity: qualityReport({ overallVerdict: 'needsAttention', editorialStatus: 'needsHumanReview' })
        }
      }
    }));

    expect(model?.overallVerdict).toBe('needsAttention');
    expect(model?.tone).toBe('danger');
    expect(model?.editorialFields).toContainEqual({ label: 'Open critical', value: '1' });
  });

  it('does not render for old runs or single AiRun traces without stored qualityFidelity', () => {
    expect(buildQualityFidelityViewModel(draftRunBundle({}))).toBeNull();
    expect(buildQualityFidelityViewModel({
      kind: 'aiRun',
      aiRun: {
        id: 'ai-1',
        capability: 'draftGeneration',
        status: 'succeeded',
        provider: 'openrouter',
        model: 'review-model',
        requestPayload: {},
        resultPayload: {},
        error: null,
        fallbackUsed: false,
        createdAt: '2026-07-06T00:00:00+00:00',
        updatedAt: '2026-07-06T00:00:01+00:00'
      }
    })).toBeNull();
  });
});

function draftRunBundle(payloads: { complete?: Record<string, unknown>; validation?: Record<string, unknown> }): RunTraceBundle {
  return {
    kind: 'draftRun',
    draftRun: {
      id: 'draft-run',
      status: 'succeeded',
      inputSummary: {},
      steps: [
        {
          key: 'validation',
          status: 'succeeded',
          title: 'Validation',
          artifactPayload: payloads.validation ?? {},
          error: null,
          startedAt: null,
          completedAt: null
        },
        {
          key: 'complete',
          status: 'succeeded',
          title: 'Complete',
          artifactPayload: payloads.complete ?? {},
          error: null,
          startedAt: null,
          completedAt: null
        }
      ],
      finalDraft: { title: 'Draft' },
      error: null,
      aiRunIds: [],
      createdAt: '2026-07-06T00:00:00+00:00',
      updatedAt: '2026-07-06T00:00:01+00:00'
    },
    childAiRuns: [],
    missingAiRunIds: []
  };
}

function qualityReport(overrides: Record<string, unknown>) {
  return {
    technicalStatus: 'succeeded',
    providerRecoveryStatus: 'clean',
    editorialStatus: 'publishable',
    overallVerdict: 'cleanSuccess',
    stageSummaries: [{ retryPath: 'clean', resultImpact: 'accepted' }],
    evidenceFidelity: {
      coverageVerdict: 'sufficient',
      foundEvidenceCount: 5,
      acceptedEvidenceCount: 4,
      interpretedEvidenceCount: 4,
      fallbackInterpretedEvidenceCount: 0,
      rejectedEvidenceCount: 1
    },
    issueLifecycle: {
      openCriticalCount: 1,
      openWarningCount: 2,
      suppressedCount: 0,
      acceptedRiskCount: 1
    },
    ...overrides
  };
}
