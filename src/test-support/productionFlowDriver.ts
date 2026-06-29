import { fireEvent, screen, waitFor } from '@testing-library/react';
import { expect, vi } from 'vitest';
import { setDraftRunFetchForTests, setDraftRunPollingForTests } from '../infrastructure/draftRunClient';
import { goToSignals, openFoundSignals } from './signalsFlowDriver';

export async function createApprovedBrief() {
  goToSignals();
  openFoundSignals();
  fireEvent.click(screen.getByRole('button', { name: /Собрать инсайт/i }));
  fireEvent.click(screen.getByRole('button', { name: /В план/i }));
  fireEvent.click(screen.getByRole('button', { name: /^Утвердить$/i }));
  fireEvent.click(screen.getByRole('button', { name: /Редактура/i }));
  fireEvent.click(screen.getByRole('tab', { name: /Рабочий стол/i }));
  const draftRunFetch = vi.fn().mockImplementation(async (_url, init) => ({
    ok: true,
    json: async () => init?.method === 'POST' ? makeCreatedRun() : makeCompletedRun()
  })) as unknown as typeof fetch;
  setDraftRunFetchForTests(draftRunFetch);
  setDraftRunPollingForTests({ intervalMs: 1, timeoutMs: 1000 });
  try {
    fireEvent.click(screen.getByRole('button', { name: /Утвердить фабулу/i }));
    await waitFor(() => {
      expect(draftRunFetch).toHaveBeenCalled();
    });
    fireEvent.click(screen.getByRole('tab', { name: /Драфт/i }));
    await waitFor(() => {
      expect(screen.getByLabelText('Текст драфта')).toBeInTheDocument();
    });
  } finally {
    setDraftRunFetchForTests(null);
    setDraftRunPollingForTests({ intervalMs: 1600, timeoutMs: 120000 });
  }
}

export async function createApprovedFinalText() {
  await createApprovedBrief();
  fireEvent.click(screen.getByRole('button', { name: /Сделать финальной/i }));
  await waitFor(() => {
    expect(screen.getAllByText(/Текст утвержден/i).length).toBeGreaterThan(0);
  });
}

export async function createExportedRelease() {
  await createApprovedFinalText();
  fireEvent.click(screen.getByRole('button', { name: /Выпуск/i }));
  fireEvent.click(screen.getByRole('button', { name: /Подготовить выпуск/i }));
  fireEvent.click(screen.getByLabelText(/Фактические warnings просмотрены/i));
  fireEvent.click(screen.getByLabelText(/CTA проверен/i));
  fireEvent.click(screen.getByLabelText(/Текст скопирован или Markdown скачан/i));
  fireEvent.click(screen.getByRole('button', { name: /Готово к выпуску/i }));
  fireEvent.click(screen.getByRole('button', { name: /Скопировать текст/i }));

  await waitFor(() => {
    expect(screen.getAllByText(/Экспортировано вручную/i).length).toBeGreaterThan(0);
  });
}

function makeCreatedRun() {
  return { runId: 'draft-run-app-flow', status: 'queued' };
}

function makeCompletedRun() {
  return {
    id: 'draft-run-app-flow',
    status: 'succeeded',
    steps: [
      step('context', 'Сбор контекста'),
      step('complete', 'Завершение')
    ],
    finalDraft: {
      id: 'draft-app-flow',
      briefId: 'brief-app-flow',
      title: 'AI-B2B demo еще не продукт',
      body: 'AI-B2B продукт начинается не с впечатляющего demo, а с доказуемого workflow improvement, evals и доверия пользователя к границам системы.',
      status: 'draft',
      version: 1,
      updatedAt: '2026-06-18T00:00:00.000Z'
    },
    error: null,
    createdAt: '2026-06-18T00:00:00.000Z',
    updatedAt: '2026-06-18T00:00:00.000Z'
  };
}

function step(key: string, title: string) {
  return {
    key,
    title,
    status: 'succeeded',
    artifactPayload: {},
    error: null,
    startedAt: null,
    completedAt: null
  };
}
