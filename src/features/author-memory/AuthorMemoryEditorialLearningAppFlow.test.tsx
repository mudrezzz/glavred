import { fireEvent, render, screen, waitFor, within } from '@testing-library/react';
import { beforeEach, describe, expect, it } from 'vitest';
import { App } from '../../App';
import { createApprovedBrief } from '../../test-support/productionFlowDriver';

const FLOW_WAIT = { timeout: 30000 };

describe('Author memory editorial learning flow', () => {
  beforeEach(() => {
    localStorage.clear();
  });

  it('creates a reviewable editorial learning note after final draft selection', async () => {
    render(<App />);
    await createApprovedBrief();

    fireEvent.click(screen.getByRole('button', { name: /Сделать финальной/i }));
    await waitFor(() => {
      expect(screen.getAllByText(/Текст утвержден/i).length).toBeGreaterThan(0);
    }, FLOW_WAIT);

    fireEvent.click(screen.getByRole('button', { name: /Память автора/i }));
    fireEvent.change(screen.getByLabelText(/Фильтр типа заметки/i), {
      target: { value: 'editorialLearning' }
    });

    const noteBody = await screen.findByText(/Что запомнить/i, undefined, FLOW_WAIT);
    const card = noteBody.closest('article') as HTMLElement;

    expect(card).toBeInTheDocument();
    expect(within(card).getAllByText(/Редакторское наблюдение/i).length).toBeGreaterThan(0);
    expect(within(card).getByText('Авто')).toBeInTheDocument();
    expect(within(card).getByText('На проверке')).toBeInTheDocument();
    expect(within(card).getByText(/Что запомнить/i)).toBeInTheDocument();

    fireEvent.click(within(card).getByRole('button', { name: /Принять в память/i }));

    await waitFor(() => {
      expect(within(card).getByText('Принято')).toBeInTheDocument();
    }, FLOW_WAIT);
    expect(within(card).queryByRole('button', { name: /Принять в память/i })).not.toBeInTheDocument();
  });
});
