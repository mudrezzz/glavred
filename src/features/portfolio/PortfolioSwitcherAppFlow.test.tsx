import { fireEvent, render, screen } from '@testing-library/react';
import { beforeEach, describe, expect, it } from 'vitest';
import { App } from '../../App';

function openPortfolioSwitcher() {
  fireEvent.click(screen.getByRole('button', { name: /AI Design Patterns/i }));
}

describe('Portfolio switcher app flow', () => {
  beforeEach(() => {
    localStorage.clear();
  });

  it('renders the portfolio control in the sidebar footer instead of the main top area', () => {
    render(<App />);

    const switcher = screen.getByTestId('portfolio-switcher');
    expect(switcher.closest('aside.side')).toBeInTheDocument();
    expect(switcher.closest('main.main')).toBeNull();
    expect(screen.queryByTestId('portfolio-switcher-panel')).not.toBeInTheDocument();

    openPortfolioSwitcher();

    expect(screen.getByTestId('portfolio-switcher-panel')).toBeInTheDocument();
    expect(screen.getByRole('combobox', { name: 'Пользователь' })).toHaveDisplayValue('Владелец портфеля');
    expect(screen.getByRole('combobox', { name: 'Блог' })).toHaveDisplayValue('AI Design Patterns');
  });

  it('shows local users and their accessible blog projects', () => {
    render(<App />);
    openPortfolioSwitcher();

    fireEvent.change(screen.getByRole('combobox', { name: 'Блог' }), {
      target: { value: 'project-kasha-iz-topora' }
    });
    expect(screen.getByRole('combobox', { name: 'Блог' })).toHaveDisplayValue('Каша из топора');

    fireEvent.change(screen.getByRole('combobox', { name: 'Пользователь' }), {
      target: { value: 'user-product-editor' }
    });
    expect(screen.getByRole('combobox', { name: 'Пользователь' })).toHaveDisplayValue('Редактор Главреда');
    expect(screen.getByRole('combobox', { name: 'Блог' })).toHaveDisplayValue('Блог Главреда');
  });

  it('keeps author memory isolated between projects', () => {
    render(<App />);

    expect(screen.getByText(/AI as an execution layer/i)).toBeInTheDocument();

    fireEvent.change(screen.getByLabelText('Заметка автора'), {
      target: { value: 'Project-specific note for AI Design Patterns only.' }
    });
    fireEvent.click(screen.getByRole('button', { name: /Добавить в память/i }));
    expect(screen.getAllByText(/Project-specific note for AI Design Patterns only/i).length).toBeGreaterThan(0);

    openPortfolioSwitcher();
    fireEvent.change(screen.getByRole('combobox', { name: 'Блог' }), {
      target: { value: 'project-kasha-iz-topora' }
    });
    expect(screen.queryByText(/Project-specific note for AI Design Patterns only/i)).not.toBeInTheDocument();
    expect(screen.getByText(/Сложный B2B не продается как коробка/i)).toBeInTheDocument();

    fireEvent.change(screen.getByRole('combobox', { name: 'Блог' }), {
      target: { value: 'project-ai-design-patterns' }
    });
    expect(screen.getAllByText(/Project-specific note for AI Design Patterns only/i).length).toBeGreaterThan(0);
  });

  it('shows Glavred blog context for the second demo user', () => {
    render(<App />);
    openPortfolioSwitcher();

    fireEvent.change(screen.getByRole('combobox', { name: 'Пользователь' }), {
      target: { value: 'user-product-editor' }
    });

    expect(screen.getByRole('combobox', { name: 'Блог' })).toHaveDisplayValue('Блог Главреда');
    expect(screen.getByText(/Главред - не генератор постов/i)).toBeInTheDocument();
    expect(screen.queryByText(/Сложный B2B не продается как коробка/i)).not.toBeInTheDocument();
  });
});
