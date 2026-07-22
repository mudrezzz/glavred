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
      radarRunId: 'run-1',
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
        projectId="project-ai"
        signal={signal}
        workspace={workspace}
        controller={controller}
        onApproveSignal={vi.fn()}
        onRejectSignal={vi.fn()}
        onArchiveSignal={vi.fn()}
      />
    );

    expect(screen.getByText('Уверенность извлечения')).toBeInTheDocument();
    expect(screen.getByText('Высокая')).toBeInTheDocument();
    expect(screen.getByText('Зависит от качества истории отказов.')).toBeInTheDocument();
    expect(screen.getByText('Сопоставление двух производственных источников данных.')).toBeInTheDocument();
    expect(screen.getByText('Мастер получает предупреждение.')).toBeInTheDocument();
    expect(screen.getByText('Требуется качественная история отказов.')).toBeInTheDocument();
    expect(screen.getByRole('heading', { name: 'Доказательства' })).toBeInTheDocument();
    expect(screen.getByRole('link', { name: /Открыть источник/ })).toHaveAttribute('href', 'https://example.org/case');
    expect(screen.getByRole('link', { name: 'Показать в трассе' })).toHaveAttribute(
      'href',
      '/radar-runs?runId=run-1&projectId=project-ai&detailId=signal-extraction&signalId=signal-1'
    );
    expect(screen.queryByText('Что нашли')).not.toBeInTheDocument();
    expect(screen.getByText('Редакционная полезность не оценена')).toBeInTheDocument();
    fireEvent.click(screen.getByText(signal.title));
    expect(controller.setExpandedSignalId).toHaveBeenCalledWith('');
  });

  it('separates a legacy heuristic from the current utility verdict', () => {
    const workspace = { radars: [{ id: 'radar-1', title: 'Промышленные AI-кейсы' }] } as WorkspaceState;
    const signal = {
      ...({
        id: 'signal-legacy', type: 'observation', title: 'Старый сигнал', capturedAt: '2026-07-14',
        source: 'Архив', summary: 'Старое наблюдение.', rawNote: 'Заметка'
      }),
      radarId: 'radar-1',
      reviewStatus: 'candidate' as const,
      legacyIntegrityStatus: 'needsReExtraction' as const,
      legacyUtilityEvaluation: {
        status: 'rejected' as const,
        source: 'legacy-client-keyword-evaluator' as const,
        canonical: false as const,
        evaluations: [{
          filterId: 'filter-topic', dimension: 'topics' as const, status: 'failed' as const, score: 0.34,
          summary: 'Связь требует проверки.', evidence: 'Предварительная локальная эвристика.'
        }]
      }
    };
    const controller = {
      expandedSignalId: signal.id,
      editingSignal: null,
      setExpandedSignalId: vi.fn(),
      startSignalEdit: vi.fn()
    } as unknown as SignalsController;

    render(
      <SourceSignalCard
        projectId="project-ai"
        signal={signal}
        workspace={workspace}
        controller={controller}
        onApproveSignal={vi.fn()}
        onRejectSignal={vi.fn()}
        onArchiveSignal={vi.fn()}
      />
    );

    expect(screen.getAllByText('Требуется повторное извлечение')).toHaveLength(2);
    expect(screen.queryByText('0.34%')).not.toBeInTheDocument();
    expect(screen.queryByText('Связь требует проверки.')).not.toBeInTheDocument();
  });

  it('keeps immutable context visible while editorial fields are edited', () => {
    const signal = {
      id: 'signal-edit', type: 'case', title: 'Промышленный пилот', source: 'Отчет',
      capturedAt: '2026-07-17', summary: 'Краткая сводка.', rawNote: '', radarId: 'radar-1',
      reviewStatus: 'candidate' as const, confidence: 'high' as const,
      uncertainty: 'Один источник.', mechanism: 'Мониторинг отклонений.',
      outcome: 'Раннее вмешательство.', limitations: ['Один пилот.'],
      evidence: [{
        id: 'e-1', materialId: 'm-1', fragmentId: 'f-1', sourceTitle: 'Полное название источника',
        sourceUrl: 'https://example.org/report', quote: 'Exact source quote.', summary: ''
      }],
      utilityReport: {
        version: 2, revision: 1, status: 'complete' as const, recommendation: 'reviewWithCaution' as const,
        blockingReasons: [], warnings: ['vendor-only'], dimensions: [], evaluationPlanVersion: 2,
        radarCriteria: [{
          criterionId: 'filter-topic', origin: 'radar' as const, dimension: 'topicAffinity',
          title: 'Промышленный контекст', statement: 'Сигнал относится к промышленному ТОиР.',
          mode: 'mustMatch' as const, status: 'matched' as const, verdict: 'СОВПАДАЕТ', effect: 'pass' as const,
          summary: 'Кейс описывает обслуживание промышленного оборудования.', settingRefs: ['filter-topic'],
          evidenceRefs: [{ materialId: 'm-1', fragmentId: 'f-1' }]
        }],
        projectCriteria: [],
        qualityChecks: [{
          checkId: 'source-posture', title: 'Позиция источника', status: 'partial', verdict: 'ТРЕБУЕТ ПРОВЕРКИ',
          effect: 'caution' as const, summary: 'Источник принадлежит поставщику.', classification: 'vendor',
          applicable: true, evidenceRefs: [{ materialId: 'm-1', fragmentId: 'f-1' }]
        }],
        notApplicableSettings: [],
        relationshipReport: { version: 1, status: 'notChecked' as const, canonicalSignalId: 'signal-edit', relations: [] }
      }
    };
    const controller = {
      expandedSignalId: signal.id,
      editingSignal: { ...signal, authorCorrection: '' },
      setExpandedSignalId: vi.fn(), startSignalEdit: vi.fn(), patchSignalDraft: vi.fn(),
      saveSignalDraft: vi.fn(), setEditingSignal: vi.fn()
    } as unknown as SignalsController;
    const workspace = { radars: [{ id: 'radar-1', title: 'Промышленные AI-кейсы' }] } as WorkspaceState;

    render(<SourceSignalCard projectId="project-ai" signal={signal} workspace={workspace} controller={controller}
      onApproveSignal={vi.fn()} onRejectSignal={vi.fn()} onArchiveSignal={vi.fn()} />);

    expect(screen.getByText('Мониторинг отклонений.')).toBeInTheDocument();
    expect(screen.getByText('Раннее вмешательство.')).toBeInTheDocument();
    expect(screen.getByText('Один пилот.')).toBeInTheDocument();
    expect(screen.getAllByText('Exact source quote.').length).toBeGreaterThan(0);
    expect(screen.getByText('Источник принадлежит поставщику.')).toBeInTheDocument();
    expect(screen.getByText('СОВПАДАЕТ')).toBeInTheDocument();
    expect(screen.queryByText('m-1/f-1')).not.toBeInTheDocument();
    expect(screen.getByTestId('signal-edit-form')).toBeInTheDocument();
    expect(screen.getAllByRole('textbox')).toHaveLength(3);
  });
});
