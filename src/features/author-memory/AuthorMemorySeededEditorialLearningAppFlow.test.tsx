import { fireEvent, render, screen, waitFor, within } from '@testing-library/react';
import { beforeEach, describe, expect, it } from 'vitest';
import { App } from '../../App';
import { renderAppCabinet } from '../../test-support/appFlowDriver';

const FLOW_WAIT = { timeout: 30000 };

describe('Seeded editorial learning demo flow', () => {
  beforeEach(() => {
    localStorage.clear();
  });

  it('shows seeded HITL draft versions and the reviewable author-memory note', async () => {
    renderAppCabinet();

    fireEvent.click(screen.getByRole('button', { name: /Редактура/i }));
    const seededRowTitles = await screen.findAllByText(/AI-B2B demo не доказывает продукт/i, undefined, FLOW_WAIT);
    const seededRow = seededRowTitles[0].closest('article') as HTMLElement;
    fireEvent.click(within(seededRow).getByRole('button', { name: /AI-B2B demo не доказывает продукт/i }));
    fireEvent.click(within(seededRow).getByRole('button', { name: /К рабочему столу/i }));
    fireEvent.click(screen.getByRole('tab', { name: /Рабочий стол/i }));
    fireEvent.click(screen.getByRole('tab', { name: /Драфт/i }));

    await waitFor(() => {
      expect(screen.getByLabelText('Версии драфта')).toBeInTheDocument();
    }, FLOW_WAIT);
    const versionList = within(screen.getByLabelText('Версии драфта'));
    expect(versionList.getByRole('button', { name: /v1/i })).toBeInTheDocument();
    expect(versionList.getByRole('button', { name: /v2.*прошла проверку.*финал/i })).toBeInTheDocument();
    expect(versionList.getByRole('button', { name: /v3.*есть риски/i })).toBeInTheDocument();
    expect(versionList.getByRole('button', { name: /v4.*есть риски/i })).toBeInTheDocument();

    fireEvent.click(screen.getByRole('button', { name: /Память автора/i }));
    fireEvent.change(screen.getByLabelText(/Фильтр типа заметки/i), {
      target: { value: 'editorialLearning' }
    });

    const noteBody = await screen.findByText(/добавь 3 критерия/i, undefined, FLOW_WAIT);
    const card = noteBody.closest('article') as HTMLElement;

    expect(within(card).getByText('Авто')).toBeInTheDocument();
    expect(within(card).getByText('На проверке')).toBeInTheDocument();
    expect(within(card).getByText(/усиль авторскую позицию/i)).toBeInTheDocument();
    expect(within(card).getByText(/убери сухой отчетный тон/i)).toBeInTheDocument();
    fireEvent.click(within(card).getByRole('button', { name: /Показать полностью/i }));
    expect(within(card).getByText(/Что запомнить/i)).toBeInTheDocument();

    fireEvent.click(within(card).getByRole('button', { name: /Принять в память/i }));

    await waitFor(() => {
      expect(within(card).getByText('Принято')).toBeInTheDocument();
    }, FLOW_WAIT);
  });
});
