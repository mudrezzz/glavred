import { fireEvent, render, screen, within } from '@testing-library/react';
import { describe, expect, it, vi } from 'vitest';
import { createDemoWorkspace } from '../../fixtures/demoWorkspace';
import type { ContentPlanItem, ContentPlanSettings } from '../../domain/editorialWorkspace';
import { PlanView } from './PlanView';

describe('PlanView', () => {
  it('uses canonical plan tabs below the header and keeps the grid filter card in main content', () => {
    const workspace = createDemoWorkspace();

    renderPlan(workspace);

    const tabs = screen.getByRole('tablist', { name: /План/i });
    expect(tabs).toHaveClass('tabs');
    expect(within(tabs).getAllByRole('tab')[0]).toHaveClass('tab');

    const filterCard = screen.getByTestId('broadcast-filter-toolbar');
    const grid = screen.getByTestId('broadcast-grid');
    expect(filterCard.closest('.broadcast-main')).toBeInTheDocument();
    expect(grid.closest('.broadcast-main')).toBeInTheDocument();
    expect(grid.closest('.broadcast-aside')).toBeNull();
  });

  it('filters and groups broadcast slots without moving rows to the side panel', () => {
    const workspace = createDemoWorkspace();

    renderPlan(workspace);

    fireEvent.change(screen.getByLabelText(/Поиск/i), { target: { value: 'Разбор мифа' } });
    expect(within(screen.getByTestId('broadcast-grid')).getAllByText(/Разбор мифа/i).length).toBeGreaterThan(0);
    expect(within(screen.getByTestId('broadcast-grid')).queryByText(/Исследовательская заметка/i)).not.toBeInTheDocument();

    fireEvent.change(screen.getByLabelText(/Поиск/i), { target: { value: '' } });
    fireEvent.click(screen.getByRole('tab', { name: /Группы/i }));
    expect(screen.getByRole('tablist', { name: /Вид сетки/i }).closest('.broadcast-main')).toBeInTheDocument();
    expect(screen.getByText(/По дате/i)).toBeInTheDocument();
  });

  it('shows full candidate context in the opened slot and readonly context in edit mode', () => {
    const workspace = createDemoWorkspace();

    renderPlan(workspace);

    const grid = screen.getByTestId('broadcast-grid');
    expect(within(grid).getByText(/Сигнал/i)).toBeInTheDocument();
    expect(within(grid).getAllByText(/^Тема$/i).length).toBeGreaterThan(0);
    expect(within(grid).getAllByText(/^Фабула$/i).length).toBeGreaterThan(0);
    expect(within(grid).getAllByText(/^Доказательство$/i).length).toBeGreaterThan(0);

    fireEvent.click(within(grid).getByRole('button', { name: /^Редактировать$/i }));
    expect(within(grid).getByLabelText(/Контекст кандидата/i)).toBeInTheDocument();
    expect(within(grid).getByLabelText(/Заголовок/i)).toBeInTheDocument();
  });

  it('shows calendar settings, saves explicit slots, and keeps candidate summary visible', () => {
    const workspace = createDemoWorkspace();
    const onSettingsSave = vi.fn();

    renderPlan(workspace, { onSettingsSave });

    fireEvent.click(screen.getByRole('tab', { name: /Настройка сетки/i }));
    expect(screen.getByTestId('plan-settings-panel')).toBeInTheDocument();
    expect(screen.getByText(/доступных кандидатов/i)).toBeInTheDocument();
    expect(screen.getByText(/утвержденных концептов/i)).toBeInTheDocument();

    fireEvent.change(screen.getByLabelText(/Период/i), { target: { value: 'week' } });
    fireEvent.change(screen.getByLabelText(/Темп/i), { target: { value: '2' } });
    fireEvent.change(screen.getByLabelText(/Площадка/i), { target: { value: 'LinkedIn' } });
    fireEvent.change(screen.getByLabelText(/Время публикаций/i), { target: { value: '09:00, 18:30' } });
    const calendarDay = screen.getAllByRole('button', { pressed: false }).find((button) =>
      button.classList.contains('publish-calendar-day') && !button.hasAttribute('disabled')
    );
    expect(calendarDay).toBeDefined();
    fireEvent.click(calendarDay as HTMLElement);
    fireEvent.click(screen.getByRole('button', { name: /Сохранить настройку/i }));

    expect(onSettingsSave).toHaveBeenCalledWith(
      expect.objectContaining({
        period: 'week',
        postsPerWeek: 2,
        defaultPlatform: 'LinkedIn',
        publishingTimes: ['09:00', '18:30'],
        signalSelectionPolicy: 'hitl-only',
        publishSlots: expect.arrayContaining([expect.objectContaining({ time: '09:00' })])
      })
    );
  });
});

function renderPlan(
  workspace = createDemoWorkspace(),
  overrides: Partial<{
    onGenerate: () => void;
    onItemChange: (item: ContentPlanItem) => void;
    onApprove: (itemId: string) => void;
    onBrief: (item: ContentPlanItem) => void;
    onSettingsSave: (settings: ContentPlanSettings) => void;
  }> = {}
) {
  return render(
    <PlanView
      workspace={workspace}
      onGenerate={overrides.onGenerate ?? vi.fn()}
      onItemChange={overrides.onItemChange ?? vi.fn()}
      onApprove={overrides.onApprove ?? vi.fn()}
      onBrief={overrides.onBrief ?? vi.fn()}
      onSettingsSave={overrides.onSettingsSave ?? vi.fn()}
    />
  );
}
