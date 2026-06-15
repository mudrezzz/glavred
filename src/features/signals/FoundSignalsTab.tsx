import type { ImportRiskLevel, SignalFilterStatus, SignalReviewStatus, SourceSignal, WorkspaceState } from '../../domain/editorialWorkspace';
import { EmptyState } from './helpers';
import { SignalsSidePanel } from './SignalsSidePanel';
import { SourceSignalCard } from './SourceSignalCard';
import type { SignalsController } from './useSignalsController';

export function FoundSignalsTab({
  workspace,
  controller,
  onApproveSignal,
  onRejectSignal,
  onArchiveSignal,
  onCreateInsight,
  onPlan
}: {
  workspace: WorkspaceState;
  controller: SignalsController;
  onApproveSignal: (signal: SourceSignal) => void;
  onRejectSignal: (signal: SourceSignal) => void;
  onArchiveSignal: (signal: SourceSignal) => void;
  onCreateInsight: () => void;
  onPlan: () => void;
}) {
  return (
    <div className="memory-grid signals-workspace-grid">
      <section className="memory-main">
        <SignalFilterToolbar workspace={workspace} controller={controller} />
        <div className="entity-list signals-entity-list" data-testid="source-signal-list">
          {controller.filteredSignals.map((signal) => (
            <SourceSignalCard
              key={signal.id}
              signal={signal}
              workspace={workspace}
              controller={controller}
              onApproveSignal={onApproveSignal}
              onRejectSignal={onRejectSignal}
              onArchiveSignal={onArchiveSignal}
            />
          ))}
          {controller.filteredSignals.length === 0 && <EmptyState text="По выбранным фильтрам сигналов нет." />}
        </div>
      </section>

      <SignalsSidePanel workspace={workspace} summary={controller.signalSummary} onCreateInsight={onCreateInsight} onPlan={onPlan} />
    </div>
  );
}

function SignalFilterToolbar({
  workspace,
  controller
}: {
  workspace: WorkspaceState;
  controller: SignalsController;
}) {
  return (
    <div className="signal-filter-row" data-testid="signal-filter-toolbar">
      <input
        className="search-input compact"
        placeholder="Поиск по сигналам, evidence, источникам"
        value={controller.query}
        onChange={(event) => controller.setQuery(event.target.value)}
      />
      <select aria-label="Фильтр радара сигнала" value={controller.radarFilter} onChange={(event) => controller.setRadarFilter(event.target.value)}>
        <option value="all">Все радары</option>
        {workspace.radars.map((radar) => (
          <option key={radar.id} value={radar.id}>
            {radar.title}
          </option>
        ))}
      </select>
      <select aria-label="Фильтр статуса сигнала" value={controller.statusFilter} onChange={(event) => controller.setStatusFilter(event.target.value as 'all' | SignalReviewStatus)}>
        <option value="all">Все статусы</option>
        <option value="new">Новые</option>
        <option value="approved">Утвержденные</option>
        <option value="corrected">С правкой</option>
        <option value="archived">В архиве</option>
        <option value="rejected">Отклоненные</option>
      </select>
      <select aria-label="Фильтр риска дубля сигнала" value={controller.riskFilter} onChange={(event) => controller.setRiskFilter(event.target.value as 'all' | ImportRiskLevel)}>
        <option value="all">Любой дубль-риск</option>
        <option value="low">low</option>
        <option value="medium">medium</option>
        <option value="high">high</option>
      </select>
      <select
        aria-label="Фильтр отбора сигнала"
        data-testid="signal-filter-status-filter"
        value={controller.filterStatusFilter}
        onChange={(event) => controller.setFilterStatusFilter(event.target.value as 'all' | SignalFilterStatus)}
      >
        <option value="all">Все по фильтрам</option>
        <option value="passed">Прошли</option>
        <option value="warning">С предупреждением</option>
        <option value="rejected">Отсечены</option>
      </select>
    </div>
  );
}
