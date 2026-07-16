import { fireEvent, render, screen } from '@testing-library/react';
import { describe, expect, it, vi } from 'vitest';
import type { WorkspaceState } from '../../domain/editorialWorkspace';
import { SourceSignalCard } from './SourceSignalCard';
import type { SignalsController } from './useSignalsController';

describe('SourceSignalCard extraction candidate', () => {
  it('shows grounding, uncertainty, mechanism, outcome, limitations, and evidence', () => {
    const signal = {
      id: 'signal-1',
      type: 'case',
      title: 'Предиктивное обслуживание предупреждает мастера',
      source: 'Industrial report',
      capturedAt: '2026-07-14T10:00:00+00:00',
      summary: 'Система сопоставляет вибрацию с журналом ремонтов.',
      rawNote: 'Доказательный кандидат',
      radarId: 'radar-1',
      reviewStatus: 'candidate' as const,
      confidence: 'high' as const,
      uncertainty: 'Зависит от качества истории отказов.',
      mechanism: 'Сопоставление двух производственных источников данных.',
      outcome: 'Мастер получает предупреждение.',
      limitations: ['Требуется качественная история отказов.'],
      evidence: [{
        id: 'evidence-1', sourceTitle: 'Industrial report', sourceUrl: 'https://example.org/case',
        quote: 'Система сопоставляет вибрацию оборудования с журналом ремонтов.', summary: 'Проверяемый фрагмент.'
      }]
    };
    const controller = {
      expandedSignalId: signal.id,
      editingSignal: null,
      setExpandedSignalId: vi.fn(),
      startSignalEdit: vi.fn()
    } as unknown as SignalsController;
    const workspace = { radars: [{ id: 'radar-1', title: 'Промышленные AI-кейсы' }] } as WorkspaceState;

    render(
      <SourceSignalCard
        signal={signal}
        workspace={workspace}
        controller={controller}
        onApproveSignal={vi.fn()}
        onRejectSignal={vi.fn()}
        onArchiveSignal={vi.fn()}
      />
    );

    expect(screen.getByText('Уверенность')).toBeInTheDocument();
    expect(screen.getByText('Зависит от качества истории отказов.')).toBeInTheDocument();
    expect(screen.getByText('Сопоставление двух производственных источников данных.')).toBeInTheDocument();
    expect(screen.getByText('Мастер получает предупреждение.')).toBeInTheDocument();
    expect(screen.getByText('Требуется качественная история отказов.')).toBeInTheDocument();
    expect(screen.getByRole('heading', { name: 'Доказательства' })).toBeInTheDocument();
    fireEvent.click(screen.getByText(signal.title));
    expect(controller.setExpandedSignalId).toHaveBeenCalledWith('');
  });
});
