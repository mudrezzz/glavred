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
    expect(screen.getByTestId('ai-run-semantic-grid')).toHaveTextContent('Draft strategy');
    expect(screen.getByTestId('ai-run-semantic-grid')).toHaveTextContent('Draft candidate 1');
    expect(screen.getByTestId('ai-run-semantic-grid')).toHaveTextContent('Selected draft');
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

    fireEvent.click(await screen.findByText('ai-candidate'));
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
    makeStep('rulePack', { hardConstraints: [{ text: 'No hype' }] }),
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
      }],
      selection: { selectedCandidateId: 'candidate-1', rationale: 'Best fit', scorecard: { topicFit: 90 } }
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
