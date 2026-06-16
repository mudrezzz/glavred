import { fireEvent, render, screen, within } from '@testing-library/react';
import { describe, expect, it, vi } from 'vitest';
import { createDemoWorkspace } from '../../fixtures/demoWorkspace';
import { PostCandidatesPreviewTab } from './PostCandidatesPreviewTab';
import type { SignalsController } from './useSignalsController';

function createController(workspace = createDemoWorkspace()): SignalsController {
  return {
    signalSummary: {
      total: workspace.sourceSignals.length,
      new: workspace.sourceSignals.filter((signal) => signal.reviewStatus === 'new').length,
      approved: workspace.sourceSignals.filter((signal) => signal.reviewStatus === 'approved').length,
      archived: workspace.sourceSignals.filter((signal) => signal.reviewStatus === 'archived').length,
      highRisk: workspace.sourceSignals.filter((signal) => signal.duplicateRisk === 'high').length
    }
  } as SignalsController;
}

describe('PostCandidatesPreviewTab', () => {
  it('shows two or three deterministic candidates for the demo workspace', () => {
    const onApprove = vi.fn();

    render(
      <PostCandidatesPreviewTab
        workspace={createDemoWorkspace()}
        controller={createController()}
        onApprovePostCandidate={onApprove}
        onEditPostCandidate={vi.fn()}
        onRejectPostCandidate={vi.fn()}
        onCreateInsight={vi.fn()}
        onPlan={vi.fn()}
      />
    );

    expect(screen.queryByText(/Сравните сборки/i)).not.toBeInTheDocument();
    expect(screen.getByLabelText(/Сигнал/i).closest('.post-candidate-toolbar')).toBeInTheDocument();
    expect(screen.getByLabelText(/Поиск/i)).toBeInTheDocument();

    const cards = screen.getAllByTestId('post-candidate-card');
    expect(cards.length).toBeGreaterThanOrEqual(2);
    expect(cards.length).toBeLessThanOrEqual(3);
    expect(cards[0].closest('.memory-main')).toBeInTheDocument();
    expect(cards[0].closest('.memory-side')).toBeNull();
    expect(within(cards[0]).getByText(/confidence/i)).toBeInTheDocument();
    expect(within(cards[0]).getByText('Risks')).toBeInTheDocument();
    expect(within(cards[0]).getByText('Доказательство').closest('.wide')).toBeInTheDocument();

    const approveButton = within(cards[0]).getByRole('button', { name: /Утвердить/i });
    expect(approveButton.closest('.inline-actions')).toBeInTheDocument();
    expect(approveButton).toHaveClass('btn-pri');
    expect(within(cards[0]).getByRole('button', { name: /Редактировать/i })).toHaveClass('btn-sec');
    expect(within(cards[0]).getByRole('button', { name: /Отклонить/i })).toHaveClass('btn-sec');

    fireEvent.click(approveButton);
    expect(onApprove).toHaveBeenCalledTimes(1);
  });

  it('filters, searches, groups, edits, and rejects candidates locally', () => {
    const workspace = createDemoWorkspace();
    const onEdit = vi.fn();
    const onReject = vi.fn();

    render(
      <PostCandidatesPreviewTab
        workspace={workspace}
        controller={createController(workspace)}
        onApprovePostCandidate={vi.fn()}
        onEditPostCandidate={onEdit}
        onRejectPostCandidate={onReject}
        onCreateInsight={vi.fn()}
        onPlan={vi.fn()}
      />
    );

    const initialCards = screen.getAllByTestId('post-candidate-card');
    const firstCard = initialCards[0];
    const firstTitle = within(firstCard).getByRole('heading', { level: 3 }).textContent ?? '';
    const firstSignal = workspace.sourceSignals.find((signal) => signal.reviewStatus === 'approved')!;

    fireEvent.change(screen.getByLabelText(/Сигнал/i), { target: { value: firstSignal.id } });
    expect(screen.getAllByTestId('post-candidate-card').length).toBeGreaterThan(0);

    fireEvent.change(screen.getByLabelText(/Поиск/i), { target: { value: 'нет такого evidence' } });
    expect(screen.queryByTestId('post-candidate-card')).not.toBeInTheDocument();
    expect(screen.getByText(/По текущим фильтрам/i)).toBeInTheDocument();

    fireEvent.change(screen.getByLabelText(/Поиск/i), { target: { value: firstTitle.slice(0, 12) } });
    expect(screen.getAllByTestId('post-candidate-card').length).toBeGreaterThan(0);

    fireEvent.click(screen.getByRole('button', { name: /Группы/i }));
    expect(screen.getByDisplayValue('По сигналу')).toBeInTheDocument();
    fireEvent.change(screen.getByDisplayValue('По сигналу'), { target: { value: 'risk' } });
    expect(screen.getByDisplayValue('По risk')).toBeInTheDocument();

    const editableCard = screen.getAllByTestId('post-candidate-card')[0];
    fireEvent.click(within(editableCard).getByRole('button', { name: /Редактировать/i }));
    fireEvent.change(screen.getByLabelText('Название'), { target: { value: 'Edited candidate title' } });
    fireEvent.click(screen.getByRole('button', { name: /Сохранить/i }));
    expect(onEdit).toHaveBeenCalledWith(expect.any(Object), expect.objectContaining({ title: 'Edited candidate title' }));

    const rejectableCard = screen.getAllByTestId('post-candidate-card')[0];
    fireEvent.click(within(rejectableCard).getByRole('button', { name: /Отклонить/i }));
    expect(onReject).toHaveBeenCalledTimes(1);
  });

  it('shows the approved-signal empty state', () => {
    const workspace = createDemoWorkspace();
    const withoutApprovedSignals = {
      ...workspace,
      sourceSignals: workspace.sourceSignals.map((signal) => ({ ...signal, reviewStatus: 'new' as const })),
      sourceSignal: { ...workspace.sourceSignal, reviewStatus: 'new' as const }
    };

    render(
      <PostCandidatesPreviewTab
        workspace={withoutApprovedSignals}
        controller={createController(withoutApprovedSignals)}
        onApprovePostCandidate={vi.fn()}
        onEditPostCandidate={vi.fn()}
        onRejectPostCandidate={vi.fn()}
        onCreateInsight={vi.fn()}
        onPlan={vi.fn()}
      />
    );

    expect(screen.queryByTestId('post-candidate-card')).not.toBeInTheDocument();
    expect(screen.getByText(/Сначала утвердите подходящий сигнал/i)).toBeInTheDocument();
  });
});
