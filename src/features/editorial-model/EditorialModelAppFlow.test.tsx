import { fireEvent, render, screen, waitFor, within } from '@testing-library/react';
import { beforeEach, describe, expect, it, vi } from 'vitest';
import { App } from '../../App';
import { renderAppCabinet } from '../../test-support/appFlowDriver';

describe('Editorial model app flow', () => {
  beforeEach(() => {
    localStorage.clear();
  });

  it('edits editorial rules, topics, fabulas, and compatibility matrix', () => {
    renderAppCabinet();

    fireEvent.click(screen.getByRole('button', { name: /Редакционная модель/i }));
    expect(screen.getAllByText('AI Design Patterns').length).toBeGreaterThan(0);
    expect(screen.getByRole('tab', { name: /Издательство/i })).toBeInTheDocument();
    expect(screen.getByRole('tab', { name: /Темы/i })).toBeInTheDocument();
    expect(screen.getByRole('tab', { name: /Фабулы/i })).toBeInTheDocument();
    expect(screen.getByRole('tab', { name: /Матрица/i })).toBeInTheDocument();
    expect(screen.getByText(/Еще не проверено/i)).toBeInTheDocument();
    expect(screen.queryByText(/Редакционная модель требует внимания/i)).not.toBeInTheDocument();
    fireEvent.click(screen.getByRole('button', { name: /^Проверить$/i }));
    expect(screen.getByText(/Редакционная модель требует внимания/i)).toBeInTheDocument();
    expect(screen.queryByText(/Legacy-рубрики/i)).not.toBeInTheDocument();

    const authorSection = screen.getByText('Автор').closest('section');
    expect(authorSection).toBeInTheDocument();
    fireEvent.click(within(authorSection as HTMLElement).getByRole('button', { name: /\+ Правило/i }));
    fireEvent.change(screen.getByLabelText('Название'), { target: { value: 'Тестовое правило автора' } });
    fireEvent.change(screen.getByLabelText('Правило'), {
      target: { value: 'Писать от лица практикующего AI PM, а не внешнего комментатора.' }
    });
    fireEvent.click(screen.getByRole('button', { name: /^Сохранить$/i }));
    expect(screen.getByText('Тестовое правило автора')).toBeInTheDocument();
    expect(screen.getByText(/Требует повторной проверки/i)).toBeInTheDocument();

    fireEvent.click(screen.getByRole('tab', { name: /Темы/i }));
    const topicButton = screen.getByRole('button', { name: 'Decision Intelligence для ТОиР' });
    expect(topicButton).toBeInTheDocument();
    expect(topicButton.closest('.entity-row-main')?.querySelector('.entity-row-meta')).toBeTruthy();
    expect(document.querySelector('.entity-details-scroll')).toBeInTheDocument();
    const topicRow = topicButton.closest('article') as HTMLElement;
    fireEvent.click(within(topicRow).getByRole('button', { name: /^Редактировать$/i }));
    fireEvent.change(screen.getByLabelText('Название'), {
      target: { value: 'Industrial workflow discovery' }
    });
    fireEvent.click(screen.getByRole('button', { name: /^Сохранить$/i }));
    expect(screen.getByText('Industrial workflow discovery')).toBeInTheDocument();

    fireEvent.click(screen.getByRole('tab', { name: /Фабулы/i }));
    const fabulaRow = screen.getByText('Карточка паттерна').closest('article') as HTMLElement;
    fireEvent.click(within(fabulaRow).getByRole('button', { name: /^Редактировать$/i }));
    fireEvent.change(screen.getByLabelText('Название'), { target: { value: 'Карточка industrial AI паттерна' } });
    fireEvent.click(screen.getByRole('button', { name: /^Сохранить$/i }));
    expect(screen.getByText('Карточка industrial AI паттерна')).toBeInTheDocument();

    fireEvent.click(screen.getByRole('tab', { name: /Матрица/i }));
    expect(screen.getByTestId('topic-fabula-matrix-scroll')).toBeInTheDocument();
    expect(document.querySelector('.matrix-sticky')).toBeTruthy();
    fireEvent.click(screen.getAllByRole('checkbox')[0]);

    expect(screen.getByText(/Есть несохраненные изменения/i)).toBeInTheDocument();
    fireEvent.click(screen.getByRole('button', { name: /Сохранить матрицу/i }));
    expect(screen.queryByText(/Есть несохраненные изменения/i)).not.toBeInTheDocument();
  });

  it('shows validator cards with score, evidence, and suggestions after manual validation', () => {
    renderAppCabinet();

    fireEvent.click(screen.getByRole('button', { name: /Редакционная модель/i }));
    expect(screen.queryByText('author-position-clarity')).not.toBeInTheDocument();

    fireEvent.click(screen.getByRole('button', { name: /^Проверить$/i }));

    expect(screen.getByText('author-position-clarity')).toBeInTheDocument();
    expect(screen.getByText('topic-fabula-coverage')).toBeInTheDocument();
    expect(screen.getByText('Score')).toBeInTheDocument();
    expect(screen.getAllByText(/Evidence и рекомендации/i).length).toBeGreaterThan(0);
  });

  it('adds and deletes topics and fabulas with matrix updates', () => {
    const confirm = vi.spyOn(window, 'confirm').mockReturnValue(true);
    renderAppCabinet();

    fireEvent.click(screen.getByRole('button', { name: /Редакционная модель/i }));
    fireEvent.click(screen.getByRole('button', { name: /^Проверить$/i }));

    fireEvent.click(screen.getByRole('tab', { name: /Темы/i }));
    fireEvent.click(screen.getByRole('button', { name: /\+ Тема/i }));
    expect(screen.getByRole('button', { name: /^Сохранить$/i })).toBeDisabled();
    fireEvent.change(screen.getByLabelText('Название'), { target: { value: 'AI trust onboarding' } });
    expect(screen.getByDisplayValue('AI trust onboarding')).toBeInTheDocument();
    fireEvent.click(screen.getByRole('button', { name: /^Сохранить$/i }));
    expect(screen.getByText(/Требует повторной проверки/i)).toBeInTheDocument();
    expect(screen.getByText('AI trust onboarding')).toBeInTheDocument();

    fireEvent.click(screen.getByRole('tab', { name: /Матрица/i }));
    expect(screen.getByText('AI trust onboarding')).toBeInTheDocument();

    fireEvent.click(screen.getByRole('tab', { name: /Темы/i }));
    fireEvent.click(screen.getByRole('button', { name: /AI trust onboarding/i }));
    const topicRow = screen.getByText('AI trust onboarding').closest('article') as HTMLElement;
    fireEvent.click(within(topicRow).getByRole('button', { name: /^Удалить$/i }));
    expect(confirm).toHaveBeenCalledWith(expect.stringContaining('AI trust onboarding'));
    expect(screen.queryByText('AI trust onboarding')).not.toBeInTheDocument();

    fireEvent.click(screen.getByRole('tab', { name: /Фабулы/i }));
    fireEvent.click(screen.getByRole('button', { name: /\+ Фабула/i }));
    expect(screen.getByRole('button', { name: /^Сохранить$/i })).toBeDisabled();
    fireEvent.change(screen.getByLabelText('Название'), { target: { value: 'Контрольный разбор внедрения' } });
    fireEvent.click(screen.getByRole('button', { name: /^Сохранить$/i }));
    expect(screen.getByText('Контрольный разбор внедрения')).toBeInTheDocument();

    fireEvent.click(screen.getByRole('tab', { name: /Матрица/i }));
    expect(screen.getByText('Контрольный разбор внедрения')).toBeInTheDocument();

    fireEvent.click(screen.getByRole('tab', { name: /Фабулы/i }));
    fireEvent.click(screen.getByRole('button', { name: /Контрольный разбор внедрения/i }));
    const fabulaRow = screen.getByText('Контрольный разбор внедрения').closest('article') as HTMLElement;
    fireEvent.click(within(fabulaRow).getByRole('button', { name: /^Удалить$/i }));
    expect(confirm).toHaveBeenCalledWith(expect.stringContaining('Контрольный разбор внедрения'));
    expect(screen.queryByText('Контрольный разбор внедрения')).not.toBeInTheDocument();

    confirm.mockRestore();
  });
});
