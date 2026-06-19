import { fireEvent, render, screen, waitFor, within } from '@testing-library/react';
import { beforeEach, describe, expect, it, vi } from 'vitest';
import { App } from '../../App';
import { createApprovedBrief } from '../../test-support/productionFlowDriver';
import { goToSignals, openFoundSignals } from '../../test-support/signalsFlowDriver';
import { setDraftRunFetchForTests, setDraftRunPollingForTests } from '../../infrastructure/draftRunClient';

describe('Editorial workbench app flow', () => {
  beforeEach(() => {
    localStorage.clear();
  });

  it('moves from source signal to an approved post brief and automatic draft', async () => {
    render(<App />);

    await createApprovedBrief();

    expect(screen.getByTestId('editorial-workbench')).toBeInTheDocument();
    expect(screen.queryByRole('button', { name: /Написать драфт/i })).not.toBeInTheDocument();
    expect(screen.getByLabelText('Текст драфта')).toBeInTheDocument();
  });

  it('shows an empty editorial work queue before approved plan slots', () => {
    render(<App />);

    fireEvent.click(screen.getByRole('button', { name: /Редактура/i }));

    expect(screen.getByTestId('editorial-work-empty')).toHaveTextContent(/План/i);
    expect(screen.getByTestId('editorial-work-toolbar')).toBeInTheDocument();
  });

  it('shows draft generation progress while backend draft run is pending', async () => {
    render(<App />);

    goToSignals();
    openFoundSignals();
    fireEvent.click(screen.getByRole('button', { name: /Собрать инсайт/i }));
    fireEvent.click(screen.getByRole('button', { name: /В план/i }));
    fireEvent.click(screen.getByRole('button', { name: /^Утвердить$/i }));
    fireEvent.click(screen.getByRole('button', { name: /Редактура/i }));
    fireEvent.click(screen.getByRole('tab', { name: /Рабочий стол/i }));

    const pendingFetch = vi.fn().mockImplementation(async (_url, init) => {
      if (init?.method === 'POST') {
        return {
          ok: true,
          json: async () => ({ runId: 'draft-run-pending', status: 'queued' })
        };
      }
      return new Promise<Response>(() => undefined);
    }) as unknown as typeof fetch;
    setDraftRunFetchForTests(pendingFetch);
    setDraftRunPollingForTests({ intervalMs: 1, timeoutMs: 1000 });
    try {
      fireEvent.click(screen.getByRole('button', { name: /Утвердить фабулу/i }));

      expect(await screen.findByText(/Генерируем драфт/i)).toBeInTheDocument();
      fireEvent.click(screen.getByRole('tab', { name: /Фабула/i }));
      expect(screen.getByRole('button', { name: /Генерируем драфт/i })).toBeDisabled();
    } finally {
      setDraftRunFetchForTests(null);
      setDraftRunPollingForTests({ intervalMs: 1600, timeoutMs: 120000 });
    }
  });

  it('creates, edits, approves, and persists approved draft text', async () => {
    const { unmount } = render(<App />);

    await createApprovedBrief();

    expect(screen.getByText('Стиль')).toBeInTheDocument();
    expect(screen.getByText('Анти-AI')).toBeInTheDocument();
    expect(screen.getAllByText('Фактчек').length).toBeGreaterThan(0);
    expect(screen.getByText('Политика')).toBeInTheDocument();

    const draftEditor = screen.getByLabelText('Текст драфта');
    fireEvent.change(draftEditor, {
      target: {
            value: `${(draftEditor as HTMLTextAreaElement).value}\n\nРучная редакторская правка перед утверждением текста.`
      }
    });
    fireEvent.click(screen.getByRole('button', { name: /Утвердить текст/i }));

    expect(screen.getAllByText(/Текст утвержден/i).length).toBeGreaterThan(0);
    expect(screen.getAllByText(/следующий шаг: Визуал/i).length).toBeGreaterThan(0);

    unmount();
    render(<App />);

    fireEvent.click(screen.getByRole('button', { name: /Редактура/i }));
    fireEvent.click(screen.getByRole('tab', { name: /Рабочий стол/i }));
    expect(screen.queryByRole('tab', { name: /Финал/i })).not.toBeInTheDocument();
    expect(screen.getAllByText(/Текст утвержден/i).length).toBeGreaterThan(0);
    fireEvent.click(screen.getByRole('tab', { name: /Драфт/i }));
    expect(screen.getByDisplayValue(/Ручная редакторская правка/i)).toBeInTheDocument();
  });
});
