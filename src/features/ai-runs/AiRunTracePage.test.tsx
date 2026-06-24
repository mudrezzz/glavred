import { fireEvent, render, screen, within, waitFor } from '@testing-library/react';
import { afterEach, describe, expect, it, vi } from 'vitest';
import { App } from '../../App';
import { setRunTraceFetchForTests } from '../../infrastructure/runTraceClient';
import { AiRunTracePage } from './AiRunTracePage';

describe('AiRunTracePage', () => {
  afterEach(() => {
    setRunTraceFetchForTests(null);
    window.history.pushState({}, '', '/');
  });

  it('loads a DraftRun timeline with child LLM calls by run id', async () => {
    const fetchMock = vi.fn()
      .mockResolvedValueOnce({ ok: true, json: async () => draftRunResponse })
      .mockResolvedValueOnce({ ok: true, json: async () => materialPlanAiRun })
      .mockResolvedValueOnce({ ok: true, json: async () => strategyAiRun })
      .mockResolvedValueOnce({ ok: true, json: async () => candidateAiRun });
    setRunTraceFetchForTests(fetchMock as unknown as typeof fetch);

    render(<AiRunTracePage />);

    fireEvent.change(screen.getByLabelText('Run ID'), { target: { value: 'draft-run-1' } });
    fireEvent.click(screen.getByRole('button', { name: /Показать трассировку/i }));

    await waitFor(() => expect(fetchMock).toHaveBeenCalledTimes(4));
    expect(screen.getByText('DraftRun')).toBeInTheDocument();
    expect(screen.getByTestId('ai-run-timeline')).toHaveTextContent('context');
    expect(screen.getByTestId('ai-run-timeline')).toHaveTextContent('materialPlan');
    expect(screen.getByTestId('ai-run-timeline')).toHaveTextContent('strategy');
    expect(screen.getByTestId('ai-run-timeline')).toHaveTextContent('draft');
    expect(screen.getByTestId('ai-run-timeline')).toHaveTextContent('ai-material');
    expect(screen.getByTestId('ai-run-timeline')).toHaveTextContent('ai-strategy');
    expect(screen.getByTestId('ai-run-timeline')).toHaveTextContent('ai-candidate');
    expect(screen.getByTestId('ai-run-timeline')).toHaveTextContent('Кандидат 1');
    expect(screen.getByTestId('ai-run-timeline')).toHaveTextContent('Скоринг кандидатов');
    expect(screen.getByTestId('ai-run-timeline')).toHaveTextContent('Выбор итогового драфта');
  });

  it('uses canonical tabs for top-level and detail switching', async () => {
    setRunTraceFetchForTests(vi.fn()
      .mockResolvedValueOnce({ ok: true, json: async () => draftRunResponse })
      .mockResolvedValueOnce({ ok: true, json: async () => materialPlanAiRun })
      .mockResolvedValueOnce({ ok: true, json: async () => strategyAiRun })
      .mockResolvedValueOnce({ ok: true, json: async () => candidateAiRun }) as unknown as typeof fetch);

    render(<AiRunTracePage />);

    fireEvent.change(screen.getByLabelText('Run ID'), { target: { value: 'draft-run-1' } });
    fireEvent.click(screen.getByRole('button', { name: /Показать трассировку/i }));

    const traceTab = await screen.findByRole('tab', { name: 'Трейс' });
    expect(traceTab).toHaveClass('tab');
    expect(screen.getByRole('tab', { name: 'Смысловой результат' })).toHaveClass('tab');
    expect(screen.getByRole('tab', { name: 'Readable' })).toHaveClass('tab');
    expect(screen.getByRole('tab', { name: 'JSON' })).toHaveClass('tab');
    expect(document.querySelector('.ai-run-json-tabs')).not.toBeInTheDocument();
  });

  it('moves semantic artifacts into the semantic result tab', async () => {
    setRunTraceFetchForTests(vi.fn()
      .mockResolvedValueOnce({ ok: true, json: async () => draftRunResponse })
      .mockResolvedValueOnce({ ok: true, json: async () => materialPlanAiRun })
      .mockResolvedValueOnce({ ok: true, json: async () => strategyAiRun })
      .mockResolvedValueOnce({ ok: true, json: async () => candidateAiRun }) as unknown as typeof fetch);

    render(<AiRunTracePage />);

    fireEvent.change(screen.getByLabelText('Run ID'), { target: { value: 'draft-run-1' } });
    fireEvent.click(screen.getByRole('button', { name: /Показать трассировку/i }));

    fireEvent.click(await screen.findByRole('tab', { name: 'Смысловой результат' }));
    expect(screen.getByTestId('ai-run-semantic-grid')).toHaveTextContent('Material plan');
    expect(screen.getByTestId('ai-run-semantic-grid')).toHaveTextContent('Rule registry');
    expect(screen.getByTestId('ai-run-semantic-grid')).toHaveTextContent('Draft strategy');
    expect(screen.getByTestId('ai-run-semantic-grid')).toHaveTextContent('Кандидат 1');
    expect(screen.getByTestId('ai-run-semantic-grid')).toHaveTextContent('Draft scorecard');
    expect(screen.getByTestId('ai-run-semantic-grid')).toHaveTextContent('Selected draft candidate');
    expect(screen.getByTestId('ai-run-semantic-grid')).toHaveTextContent('Selected draft');
  });

  it('opens draft scorecard and selected candidate details from the timeline', async () => {
    setRunTraceFetchForTests(vi.fn()
      .mockResolvedValueOnce({ ok: true, json: async () => draftRunResponse })
      .mockResolvedValueOnce({ ok: true, json: async () => materialPlanAiRun })
      .mockResolvedValueOnce({ ok: true, json: async () => strategyAiRun })
      .mockResolvedValueOnce({ ok: true, json: async () => candidateAiRun }) as unknown as typeof fetch);

    render(<AiRunTracePage />);

    fireEvent.change(screen.getByLabelText('Run ID'), { target: { value: 'draft-run-1' } });
    fireEvent.click(screen.getByRole('button', { name: /Показать трассировку/i }));

    fireEvent.click(await screen.findByText('Скоринг кандидатов'));
    const scorecard = within(screen.getByTestId('ai-run-detail-panel')).getByTestId('ai-run-scorecard');
    expect(scorecard).toHaveTextContent('Candidate title');
    expect(scorecard).toHaveTextContent('Alternative candidate');
    expect(scorecard).toHaveTextContent('80');
    expect(scorecard).toHaveTextContent('68');
    expect(scorecard).toHaveTextContent('eligible');
    expect(scorecard).toHaveTextContent('excluded');
    expect(scorecard).toHaveTextContent('fallback-candidate-provider-alternative');
    expect(screen.getByTestId('ai-run-detail-panel')).not.toHaveTextContent('Score rows');

    fireEvent.click(screen.getByText('Выбор итогового драфта'));
    expect(screen.getByTestId('ai-run-detail-panel')).toHaveTextContent('Candidate title');
    expect(screen.getByTestId('ai-run-detail-panel')).toHaveTextContent('Best fit');
  });

  it('selects a child LLM call and shows prompt messages plus provider metadata', async () => {
    setRunTraceFetchForTests(vi.fn()
      .mockResolvedValueOnce({ ok: true, json: async () => draftRunResponse })
      .mockResolvedValueOnce({ ok: true, json: async () => materialPlanAiRun })
      .mockResolvedValueOnce({ ok: true, json: async () => strategyAiRun })
      .mockResolvedValueOnce({ ok: true, json: async () => candidateAiRun }) as unknown as typeof fetch);

    render(<AiRunTracePage />);

    fireEvent.change(screen.getByLabelText('Run ID'), { target: { value: 'draft-run-1' } });
    fireEvent.click(screen.getByRole('button', { name: /Показать трассировку/i }));

    const timeline = await screen.findByTestId('ai-run-timeline');
    fireEvent.click(within(timeline).getAllByText('ai-candidate')[0]);
    const detail = screen.getByTestId('ai-run-detail-panel');
    expect(detail).toHaveTextContent('LLM call');
    expect(detail).toHaveTextContent('Return JSON');
    expect(detail).toHaveTextContent('Candidate input');
    expect(detail).toHaveTextContent('openrouter');
  });

  it('pretty-prints JSON string messages in selected message detail', async () => {
    setRunTraceFetchForTests(vi.fn()
      .mockResolvedValueOnce({ ok: false, status: 404 })
      .mockResolvedValueOnce({ ok: true, json: async () => jsonStringAiRun }) as unknown as typeof fetch);

    render(<AiRunTracePage />);

    fireEvent.change(screen.getByLabelText('Run ID'), { target: { value: 'ai-json' } });
    fireEvent.click(screen.getByRole('button', { name: /Показать трассировку/i }));

    fireEvent.click(await screen.findByText(/json payload/i));
    const detail = screen.getByTestId('ai-run-detail-panel');
    expect(detail).toHaveTextContent('"brief"');
    expect(detail).toHaveTextContent('"title"');
  });

  it('keeps single AiRun lookup after DraftRun 404', async () => {
    const fetchMock = vi.fn()
      .mockResolvedValueOnce({ ok: false, status: 404 })
      .mockResolvedValueOnce({ ok: true, json: async () => candidateAiRun });
    setRunTraceFetchForTests(fetchMock as unknown as typeof fetch);

    render(<AiRunTracePage />);

    fireEvent.change(screen.getByLabelText('Run ID'), { target: { value: 'ai-candidate' } });
    fireEvent.click(screen.getByRole('button', { name: /Показать трассировку/i }));

    await waitFor(() => expect(fetchMock).toHaveBeenCalledTimes(2));
    expect(screen.getByText('AiRun')).toBeInTheDocument();
    expect(screen.getByTestId('ai-run-timeline')).toHaveTextContent('ai-candidate');
  });

  it('shows missing child runs as warnings inside the timeline', async () => {
    setRunTraceFetchForTests(vi.fn()
      .mockResolvedValueOnce({ ok: true, json: async () => ({ ...draftRunResponse, aiRunIds: ['missing-ai'] }) })
      .mockResolvedValueOnce({ ok: false, status: 404 }) as unknown as typeof fetch);

    render(<AiRunTracePage />);

    fireEvent.change(screen.getByLabelText('Run ID'), { target: { value: 'draft-run-1' } });
    fireEvent.click(screen.getByRole('button', { name: /Показать трассировку/i }));

    expect(await screen.findByText('missing-ai')).toBeInTheDocument();
    expect(screen.getByTestId('ai-run-timeline')).toHaveTextContent('Missing child run');
  });

  it('shows a readable error when neither DraftRun nor AiRun exists', async () => {
    setRunTraceFetchForTests(vi.fn()
      .mockResolvedValueOnce({ ok: false, status: 404 })
      .mockResolvedValueOnce({ ok: false, status: 404 }) as unknown as typeof fetch);

    render(<AiRunTracePage />);

    fireEvent.change(screen.getByLabelText('Run ID'), { target: { value: 'missing' } });
    fireEvent.click(screen.getByRole('button', { name: /Показать трассировку/i }));

    expect(await screen.findByText(/Run not found/i)).toBeInTheDocument();
  });

  it('opens outside the main cabinet route', () => {
    window.history.pushState({}, '', '/ai-runs');

    render(<App />);

    expect(screen.getByRole('heading', { name: /Трассировка запуска/i })).toBeInTheDocument();
    expect(screen.queryByText('Главред')).not.toBeInTheDocument();
  });

  it('loads from a direct run-id URL', async () => {
    window.history.pushState({}, '', '/ai-runs?runId=draft-run-1');
    const fetchMock = vi.fn()
      .mockResolvedValueOnce({ ok: true, json: async () => draftRunResponse })
      .mockResolvedValueOnce({ ok: true, json: async () => materialPlanAiRun })
      .mockResolvedValueOnce({ ok: true, json: async () => strategyAiRun })
      .mockResolvedValueOnce({ ok: true, json: async () => candidateAiRun });
    setRunTraceFetchForTests(fetchMock as unknown as typeof fetch);

    render(<App />);

    await waitFor(() => expect(fetchMock).toHaveBeenCalled());
    expect(screen.getByText('DraftRun')).toBeInTheDocument();
  });
});

const draftRunResponse = {
  id: 'draft-run-1',
  status: 'succeeded',
  inputSummary: { title: 'AI product discovery' },
  steps: [
    makeStep('context', { workItem: { title: 'Post title' } }),
    makeStep('rulePack', {
      hardConstraints: [{ text: 'No hype' }],
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
    }),
    makeStep('materialPlan', {
      source: 'openrouter',
      aiRunId: 'ai-material',
      fallbackUsed: false,
      materialPlan: { availableEvidence: ['pilot usage'], missingEvidence: ['benchmark'] }
    }),
    makeStep('strategy', {
      source: 'openrouter',
      aiRunId: 'ai-strategy',
      fallbackUsed: false,
      draftStrategy: { thesisAngle: 'workflow before model', openingMove: 'pilot gap' }
    }),
    makeStep('draft', {
      source: 'openrouter',
      fallbackUsed: false,
      aiRunIds: ['ai-candidate'],
      candidates: [{
        id: 'candidate-1',
        direction: { id: 'research', label: 'Research' },
        title: 'Candidate title',
        body: 'Candidate body',
        rationale: 'Fits rules',
        usedEvidence: ['pilot usage'],
        ruleCoverage: ['topic fit'],
        risks: ['claim risk'],
        weaknesses: ['needs source'],
        source: 'openrouter',
        aiRunId: 'ai-candidate'
      }, {
        id: 'candidate-2',
        direction: { id: 'contrast', label: 'Contrast' },
        rhetoricalPlanId: 'contrast',
        title: 'Alternative candidate',
        body: 'Alternative body',
        rationale: 'Stronger contrast, weaker evidence.',
        usedEvidence: ['pilot usage'],
        ruleCoverage: ['topic fit'],
        risks: ['claim risk', 'tone risk'],
        weaknesses: ['needs more source'],
        source: 'openrouter',
        aiRunId: null
      }],
      selection: {
        selectedCandidateId: 'candidate-1',
        reason: 'Best fit',
        scorecard: [
          {
            candidateId: 'candidate-1',
            hardConstraintFit: 20,
            evidenceGrounding: 20,
            topicFit: 16,
            fabulaFit: 16,
            audienceValue: 12,
            riskPenalty: 4,
            publishable: true,
            selectionStatus: 'eligible',
            selectionPenalty: 0,
            selectionReasons: [],
            total: 80
          },
          {
            candidateId: 'candidate-2',
            hardConstraintFit: 18,
            evidenceGrounding: 16,
            topicFit: 16,
            fabulaFit: 14,
            audienceValue: 12,
            riskPenalty: 8,
            publishable: false,
            selectionStatus: 'excluded',
            selectionPenalty: 500,
            selectionReasons: ['fallback-candidate-provider-alternative'],
            total: 68
          }
        ],
        unresolvedRisks: []
      }
    }),
    makeStep('validation', { status: 'placeholder-passed' }),
    makeStep('complete', { status: 'succeeded' })
  ],
  finalDraft: { title: 'Selected title', body: 'Selected body', version: 1, status: 'draft' },
  error: null,
  aiRunIds: ['ai-material', 'ai-strategy', 'ai-candidate'],
  createdAt: '2026-06-19T00:00:00+00:00',
  updatedAt: '2026-06-19T00:00:02+00:00'
};

const materialPlanAiRun = makeAiRun('ai-material', 'materialPlan', {
  result: { availableEvidence: ['pilot usage'], missingEvidence: ['benchmark'] }
});

const strategyAiRun = makeAiRun('ai-strategy', 'strategy', {
  result: { thesisAngle: 'workflow before model', openingMove: 'pilot gap' }
});

const candidateAiRun = makeAiRun('ai-candidate', 'draftCandidate', {
  candidate: {
    title: 'Candidate title',
    body: 'Candidate body',
    rationale: 'Fits rules',
    usedEvidence: ['pilot usage'],
    ruleCoverage: ['topic fit'],
    risks: ['claim risk'],
    weaknesses: ['needs source'],
    source: 'openrouter',
    aiRunId: 'ai-candidate'
  },
  providerResponse: { id: 'or-run', model: 'deepseek/deepseek-v3.2' }
});

const jsonStringAiRun = {
  ...makeAiRun('ai-json', 'draftCandidate', { candidate: { title: 'JSON candidate', body: 'Body' } }),
  requestPayload: {
    draftRunStep: 'draftCandidate',
    providerRequest: {
      messages: [
        { role: 'system', content: 'Return JSON' },
        { role: 'user', content: '{"brief":{"title":"json payload"}}' }
      ]
    }
  }
};

function makeStep(key: string, artifactPayload: Record<string, unknown>) {
  return {
    key,
    status: 'succeeded',
    title: key,
    artifactPayload,
    error: null,
    startedAt: '2026-06-19T00:00:00+00:00',
    completedAt: '2026-06-19T00:00:01+00:00'
  };
}

function makeAiRun(id: string, step: string, resultPayload: Record<string, unknown>) {
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
          { role: 'user', content: `${step === 'draftCandidate' ? 'Candidate' : step} input` }
        ],
        temperature: 0.4
      }
    },
    resultPayload: { draftRunStep: step, ...resultPayload },
    error: null,
    fallbackUsed: false,
    createdAt: '2026-06-19T00:00:00+00:00',
    updatedAt: '2026-06-19T00:00:01+00:00'
  };
}
