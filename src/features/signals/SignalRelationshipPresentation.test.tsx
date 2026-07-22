import { render, screen } from '@testing-library/react';
import { describe, expect, it, vi } from 'vitest';
import type { SourceSignal, WorkspaceState } from '../../domain/editorialWorkspace';
import { FoundSignalsTab } from './FoundSignalsTab';
import type { SignalsController } from './useSignalsController';

describe('signal relationship presentation', () => {
  it('shows one canonical card and keeps the alias evidence human-readable', () => {
    const canonical = makeSignal('signal-advisor-a', 'Цифровой советчик как модуль поддержки решений в ТОиР');
    const alias = makeSignal('signal-advisor-b', 'Цифровой советчик как модуль поддержки решений ТОиР');
    canonical.relationshipReport = {
      version: 1,
      status: 'checked',
      canonicalSignalId: canonical.id,
      relations: [{
        otherSignalId: alias.id,
        kind: 'sameClaim',
        summary: 'Сигналы выражают один основной тезис.',
        evidenceRefs: [{ materialId: 'material-shared', fragmentId: 'fragment-b' }]
      }]
    };
    alias.relationshipReport = {
      version: 1,
      status: 'checked',
      canonicalSignalId: canonical.id,
      relations: [{
        otherSignalId: canonical.id,
        kind: 'sameClaim',
        summary: 'Сигналы выражают один основной тезис.',
        evidenceRefs: [{ materialId: 'material-shared', fragmentId: 'fragment-a' }]
      }]
    };
    canonical.utilityReport = utility(canonical.relationshipReport);
    alias.utilityReport = utility(alias.relationshipReport);
    const workspace = {
      radars: [{ id: 'radar-industrial', title: 'Промышленные AI-кейсы' }],
      sourceSignals: [canonical, alias],
      postCandidate: null
    } as unknown as WorkspaceState;
    const controller = {
      filteredSignals: [canonical, alias],
      expandedSignalId: canonical.id,
      editingSignal: null,
      setExpandedSignalId: vi.fn(),
      startSignalEdit: vi.fn(),
      signalSummary: { total: 2, new: 2, approved: 0, archived: 0, relationshipGroups: 1 },
      query: '', setQuery: vi.fn(), radarFilter: 'all', setRadarFilter: vi.fn(),
      statusFilter: 'all', setStatusFilter: vi.fn(), filterStatusFilter: 'all', setFilterStatusFilter: vi.fn()
    } as unknown as SignalsController;

    render(
      <FoundSignalsTab
        projectId="project-ai"
        workspace={workspace}
        controller={controller}
        onApproveSignal={vi.fn()}
        onRejectSignal={vi.fn()}
        onArchiveSignal={vi.fn()}
        onReopenSignal={vi.fn()}
        onRestoreSignal={vi.fn()}
        onRescoreSignal={vi.fn()}
        onCreateInsight={vi.fn()}
        onPlan={vi.fn()}
      />
    );

    expect(screen.getAllByTestId('source-signal-row')).toHaveLength(1);
    expect(screen.getByText('ОДИН ТЕЗИС')).toBeInTheDocument();
    expect(screen.getByText(alias.title)).toBeInTheDocument();
    expect(screen.getByText('Цитата для signal-advisor-b')).toBeInTheDocument();
    expect(screen.queryByText('material-shared/fragment-b')).not.toBeInTheDocument();
  });
});

function makeSignal(id: string, title: string): SourceSignal {
  const fragmentId = id.endsWith('a') ? 'fragment-a' : 'fragment-b';
  return {
    id,
    type: 'case',
    title,
    source: 'Промышленный отчет',
    capturedAt: '2026-07-20',
    summary: 'Источник описывает цифровой советчик для ТОиР.',
    rawNote: '',
    radarId: 'radar-industrial',
    radarRunId: 'run-industrial',
    reviewStatus: 'candidate',
    editorialLanguage: 'ru',
    evidenceRefs: [{ materialId: 'material-shared', fragmentId, quote: `Цитата для ${id}` }],
    evidence: [{
      id: `evidence-${id}`,
      materialId: 'material-shared',
      fragmentId,
      sourceTitle: 'Промышленный отчет',
      sourceUrl: 'https://example.test/industrial-report',
      quote: `Цитата для ${id}`,
      summary: ''
    }]
  };
}

function utility(relationshipReport: NonNullable<SourceSignal['relationshipReport']>): NonNullable<SourceSignal['utilityReport']> {
  return {
    version: 2,
    revision: 1,
    status: 'complete',
    recommendation: 'reviewWithCaution',
    dimensions: [],
    blockingReasons: [],
    warnings: [],
    evaluationPlanVersion: 2,
    radarCriteria: [],
    projectCriteria: [],
    qualityChecks: [],
    notApplicableSettings: [],
    relationshipReport
  };
}
