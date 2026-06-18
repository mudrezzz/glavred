import { fireEvent, screen, waitFor } from '@testing-library/react';
import { expect, vi } from 'vitest';
import { setBackendDraftFetchForTests } from '../infrastructure/backendDraftClient';
import { goToSignals, openFoundSignals } from './signalsFlowDriver';

export async function createApprovedBrief() {
  goToSignals();
  openFoundSignals();
  fireEvent.click(screen.getByRole('button', { name: /Собрать инсайт/i }));
  fireEvent.click(screen.getByRole('button', { name: /В план/i }));
  fireEvent.click(screen.getByRole('button', { name: /^Утвердить$/i }));
  fireEvent.click(screen.getByRole('button', { name: /Редактура/i }));
  fireEvent.click(screen.getByRole('tab', { name: /Рабочий стол/i }));
  const backendDraftFetch = vi.fn().mockResolvedValue({
    ok: true,
    json: async () => ({
      draft: {
        id: 'draft-app-flow',
        briefId: 'brief-app-flow',
        title: 'AI-B2B demo еще не продукт',
        body: 'AI-B2B продукт начинается не с впечатляющего demo, а с доказуемого workflow improvement, evals и доверия пользователя к границам системы.',
        status: 'draft',
        version: 1,
        updatedAt: '2026-06-18T00:00:00.000Z'
      },
      aiRun: {
        id: 'airun-app-flow',
        capability: 'draftGeneration',
        status: 'succeeded',
        provider: 'openrouter',
        model: 'openai/gpt-4.1-mini',
        requestPayload: {},
        resultPayload: {},
        error: null,
        fallbackUsed: false,
        createdAt: '2026-06-18T00:00:00.000Z',
        updatedAt: '2026-06-18T00:00:00.000Z'
      }
    })
  }) as unknown as typeof fetch;
  setBackendDraftFetchForTests(backendDraftFetch);
  try {
    fireEvent.click(screen.getByRole('button', { name: /Утвердить фабулу/i }));
    await waitFor(() => {
      expect(backendDraftFetch).toHaveBeenCalled();
    });
    fireEvent.click(screen.getByRole('tab', { name: /Драфт/i }));
    await waitFor(() => {
      expect(screen.getByLabelText('Текст драфта')).toBeInTheDocument();
    });
  } finally {
    setBackendDraftFetchForTests(null);
  }
}

export async function createApprovedFinalText() {
  await createApprovedBrief();
  fireEvent.click(screen.getByRole('button', { name: /Утвердить текст/i }));
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
