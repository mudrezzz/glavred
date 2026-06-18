import { fireEvent, render, screen, waitFor } from '@testing-library/react';
import { afterEach, describe, expect, it, vi } from 'vitest';
import { App } from '../../App';
import { setAiRunTraceFetchForTests } from '../../infrastructure/aiRunTraceClient';
import { AiRunTracePage } from './AiRunTracePage';

const traceResponse = {
  id: 'run-demo',
  capability: 'draftGeneration',
  status: 'succeeded',
  provider: 'openrouter',
  model: 'openai/gpt-4.1-mini',
  requestPayload: {
    promptMessages: [{ role: 'user', content: 'Approved fabula context' }],
    providerRequest: { temperature: 0.4 }
  },
  resultPayload: {
    draft: {
      title: 'AI run debug draft',
      body: 'Full generated draft body'
    }
  },
  error: null,
  fallbackUsed: false,
  createdAt: '2026-06-18T00:00:00+00:00',
  updatedAt: '2026-06-18T00:00:01+00:00'
};

describe('AiRunTracePage', () => {
  afterEach(() => {
    setAiRunTraceFetchForTests(null);
    window.history.pushState({}, '', '/');
  });

  it('loads and renders detailed trace by run id', async () => {
    const fetchMock = vi.fn().mockResolvedValue({
      ok: true,
      json: async () => traceResponse
    }) as unknown as typeof fetch;
    setAiRunTraceFetchForTests(fetchMock);

    render(<AiRunTracePage />);

    fireEvent.change(screen.getByLabelText('Run ID'), { target: { value: 'run-demo' } });
    fireEvent.click(screen.getByRole('button', { name: /Показать трассировку/i }));

    await waitFor(() => expect(fetchMock).toHaveBeenCalled());
    expect(screen.getByText('draftGeneration')).toBeInTheDocument();
    expect(screen.getByText('openrouter')).toBeInTheDocument();
    expect(screen.getByText(/Approved fabula context/i)).toBeInTheDocument();
    expect(screen.getByText(/Full generated draft body/i)).toBeInTheDocument();
  });

  it('shows a readable error when the backend cannot find a run', async () => {
    setAiRunTraceFetchForTests(vi.fn().mockResolvedValue({ ok: false, status: 404 }) as unknown as typeof fetch);

    render(<AiRunTracePage />);

    fireEvent.change(screen.getByLabelText('Run ID'), { target: { value: 'missing' } });
    fireEvent.click(screen.getByRole('button', { name: /Показать трассировку/i }));

    expect(await screen.findByText(/not found/i)).toBeInTheDocument();
  });

  it('opens outside the main cabinet route', () => {
    window.history.pushState({}, '', '/ai-runs');

    render(<App />);

    expect(screen.getByRole('heading', { name: /Трассировка запуска/i })).toBeInTheDocument();
    expect(screen.queryByText('Главред')).not.toBeInTheDocument();
  });

  it('loads from a direct run-id URL', async () => {
    window.history.pushState({}, '', '/ai-runs?runId=run-demo');
    const fetchMock = vi.fn().mockResolvedValue({
      ok: true,
      json: async () => traceResponse
    }) as unknown as typeof fetch;
    setAiRunTraceFetchForTests(fetchMock);

    render(<App />);

    await waitFor(() => expect(fetchMock).toHaveBeenCalled());
    expect(screen.getByText(/AI run debug draft/i)).toBeInTheDocument();
  });
});
