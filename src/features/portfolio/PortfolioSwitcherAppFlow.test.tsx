import { fireEvent, render, screen } from '@testing-library/react';
import { beforeEach, describe, expect, it } from 'vitest';
import { App } from '../../App';

describe('Portfolio switcher app flow', () => {
  beforeEach(() => {
    localStorage.clear();
  });

  it('shows local users and their accessible blog projects', () => {
    render(<App />);

    expect(screen.getByTestId('portfolio-switcher')).toBeInTheDocument();
    expect(screen.getByRole('combobox', { name: 'Пользователь' })).toHaveDisplayValue('Владелец портфеля');
    expect(screen.getByRole('combobox', { name: 'Блог' })).toHaveDisplayValue('AI Design Patterns');

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

    fireEvent.change(screen.getByLabelText('Заметка автора'), {
      target: { value: 'Project-specific note for AI Design Patterns only.' }
    });
    fireEvent.click(screen.getByRole('button', { name: /Добавить в память/i }));
    expect(screen.getAllByText(/Project-specific note for AI Design Patterns only/i).length).toBeGreaterThan(0);

    fireEvent.change(screen.getByRole('combobox', { name: 'Блог' }), {
      target: { value: 'project-kasha-iz-topora' }
    });
    expect(screen.queryByText(/Project-specific note for AI Design Patterns only/i)).not.toBeInTheDocument();

    fireEvent.change(screen.getByRole('combobox', { name: 'Блог' }), {
      target: { value: 'project-ai-design-patterns' }
    });
    expect(screen.getAllByText(/Project-specific note for AI Design Patterns only/i).length).toBeGreaterThan(0);
  });
});
