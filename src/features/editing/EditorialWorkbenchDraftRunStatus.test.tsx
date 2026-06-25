import { fireEvent, render, screen, waitFor } from '@testing-library/react';
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';
import { App } from '../../App';
import { setDraftRunFetchForTests, setDraftRunPollingForTests } from '../../infrastructure/draftRunClient';
import { goToSignals, openFoundSignals } from '../../test-support/signalsFlowDriver';

describe('Editorial workbench DraftRun status', () => {
  beforeEach(() => {
    localStorage.clear();
  });

  afterEach(() => {
    setDraftRunFetchForTests(null);
    setDraftRunPollingForTests({ intervalMs: 1600, timeoutMs: 120000 });
    vi.unstubAllGlobals();
  });

  it('keeps a live stale DraftRun visible instead of using compatibility fallback', async () => {
    render(<App />);
    goToSignals();
    openFoundSignals();
    fireEvent.click(screen.getByRole('button', { name: /Собрать инсайт/i }));
    fireEvent.click(screen.getByRole('button', { name: /В план/i }));
    fireEvent.click(screen.getByRole('button', { name: /^Утвердить$/i }));
    fireEvent.click(screen.getByRole('button', { name: /Редактура/i }));
    fireEvent.click(screen.getByRole('tab', { name: /Рабочий стол/i }));

    const compatibilityFetch = vi.fn();
    vi.stubGlobal('fetch', compatibilityFetch);
    let allowComplete = false;
    const draftRunFetch = vi.fn().mockImplementation(async (_url: RequestInfo | URL, init?: RequestInit) => ({
      ok: true,
      json: async () => init?.method === 'POST'
        ? { runId: 'draft-run-pending', status: 'queued' }
        : allowComplete ? completedRun() : staleRunningRun()
    })) as unknown as typeof fetch;
    setDraftRunFetchForTests(draftRunFetch);
    setDraftRunPollingForTests({ intervalMs: 1, timeoutMs: 1000 });

    fireEvent.click(screen.getByRole('button', { name: /Утвердить фабулу/i }));

    expect(await screen.findByText(/Генерируем драфт/i)).toBeInTheDocument();
    expect(screen.getAllByRole('link').some((link) => link.getAttribute('href') === '/ai-runs?runId=draft-run-pending')).toBe(true);
    expect(screen.getAllByText(/Search public sources/i).length).toBeGreaterThan(0);
    expect((await screen.findAllByText((content) => content.includes('5') && content.includes('минут'))).length).toBeGreaterThan(0);
    await new Promise((resolve) => setTimeout(resolve, 20));
    expect(compatibilityFetch).not.toHaveBeenCalled();

    allowComplete = true;
    await waitFor(() => expect(screen.queryByText(/Генерируем драфт/i)).not.toBeInTheDocument());
  });
});

function staleRunningRun() {
  return {
    id: 'draft-run-pending',
    status: 'running',
    steps: [{
      key: 'publicEvidence',
      status: 'running',
      title: 'Public evidence',
      artifactPayload: {
        progress: {
          status: 'running',
          currentOperationId: 'search-task-1',
          operations: [{
            id: 'search-task-1',
            kind: 'findPublicSources',
            label: 'Search public sources: opinion leaders',
            status: 'running',
            startedAt: '2026-06-23T00:00:00.000Z',
            completedAt: null,
            target: 'opinion leaders'
          }]
        }
      },
      error: null,
      startedAt: '2026-06-23T00:00:00.000Z',
      completedAt: null
    }],
    finalDraft: null,
    error: null,
    isStale: true,
    staleReason: 'No DraftRun progress for more than 5 minutes.',
    lastProgressAt: '2026-06-23T00:00:00.000Z',
    createdAt: '2026-06-23T00:00:00.000Z',
    updatedAt: '2026-06-23T00:00:00.000Z'
  };
}
function completedRun() {
  return {
    ...staleRunningRun(),
    status: 'succeeded',
    steps: staleRunningRun().steps.map((step) => ({ ...step, status: 'succeeded', completedAt: '2026-06-23T00:00:01.000Z' })),
    finalDraft: {
      id: 'draft-run-draft',
      briefId: 'brief-demo',
      title: 'DraftRun draft',
      body: 'DraftRun body',
      version: 1,
      status: 'draft',
      updatedAt: '2026-06-23T00:00:01.000Z'
    },
    isStale: false,
    staleReason: null,
    updatedAt: '2026-06-23T00:00:01.000Z'
  };
}
