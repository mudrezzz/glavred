import { fireEvent, render, screen, within } from '@testing-library/react';
import { describe, expect, it, vi } from 'vitest';
import { createDemoWorkspace } from '../../fixtures/demoWorkspace';
import type { ContentPlanItem, ContentPlanSettings } from '../../domain/editorialWorkspace';
import { PlanView } from './PlanView';

describe('PlanView', () => {
  it('shows grid settings, saves explicit settings, and keeps candidate summary visible', () => {
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
    fireEvent.click(screen.getByRole('button', { name: /Сохранить настройку/i }));

    expect(onSettingsSave).toHaveBeenCalledWith(
      expect.objectContaining({
        period: 'week',
        postsPerWeek: 2,
        defaultPlatform: 'LinkedIn',
        publishingTimes: ['09:00', '18:30'],
        signalSelectionPolicy: 'hitl-only'
      })
    );
  });

  it('keeps broadcast cards in the main plan area and shows date with time', () => {
    const workspace = createDemoWorkspace();

    renderPlan(workspace);

    const grid = screen.getByTestId('broadcast-grid');
    expect(grid.closest('.broadcast-main')).toBeInTheDocument();
    expect(grid.closest('.broadcast-aside')).toBeNull();
    expect(within(grid).getAllByText(/10:00/i).length).toBeGreaterThan(0);
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
