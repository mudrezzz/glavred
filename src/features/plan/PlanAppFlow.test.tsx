import { fireEvent, render, screen, waitFor, within } from '@testing-library/react';
import { beforeEach, describe, expect, it } from 'vitest';
import { App } from '../../App';
import { renderAppCabinet } from '../../test-support/appFlowDriver';

describe('Plan app flow', () => {
  beforeEach(() => {
    localStorage.clear();
  });

  it('shows broadcast grid slots and keeps post brief as an internal production step', () => {
    renderAppCabinet();

    fireEvent.click(screen.getByRole('button', { name: /План/i }));

    expect(screen.getByTestId('broadcast-grid')).toBeInTheDocument();
    expect(screen.getByText(/Сетка на месяц/i)).toBeInTheDocument();
    expect(screen.getAllByText(/Сетка вещания/i).length).toBeGreaterThan(0);

    fireEvent.click(screen.getAllByRole('button', { name: /^Редактировать$/i })[0]);
    fireEvent.change(screen.getByLabelText('Заголовок'), { target: { value: 'AI-B2B rollout grid slot' } });
    fireEvent.click(screen.getByRole('button', { name: /^Отменить$/i }));
    expect(screen.queryByText('AI-B2B rollout grid slot')).not.toBeInTheDocument();

    fireEvent.click(screen.getAllByRole('button', { name: /^Редактировать$/i })[0]);
    fireEvent.change(screen.getByLabelText('Заголовок'), { target: { value: 'AI-B2B rollout grid slot' } });
    fireEvent.click(screen.getByRole('button', { name: /^Сохранить$/i }));
    expect(screen.getByText('AI-B2B rollout grid slot')).toBeInTheDocument();

    fireEvent.click(screen.getByRole('button', { name: /^Утвердить$/i }));
    expect(screen.queryByRole('button', { name: /Подготовить фабулу поста/i })).not.toBeInTheDocument();
    expect(screen.getByRole('button', { name: /В редактуре/i })).toBeInTheDocument();
    expect(screen.getByTestId('broadcast-grid')).toBeInTheDocument();
  });
});
