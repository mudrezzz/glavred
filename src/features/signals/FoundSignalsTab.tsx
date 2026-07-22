import type { SignalReviewStatus, SignalUtilityRecommendation, SourceSignal, WorkspaceState } from '../../domain/editorialWorkspace';
import { EmptyState } from './helpers';
import { SignalsSidePanel } from './SignalsSidePanel';
import { SourceSignalCard } from './SourceSignalCard';
import type { SignalsController } from './useSignalsController';

export function FoundSignalsTab({
  projectId,
  workspace,
  controller,
  onApproveSignal,
  onRejectSignal,
  onArchiveSignal,
  onReopenSignal,
  onRestoreSignal,
  onRescoreSignal,
  onCreateInsight,
  onPlan
}: {
  projectId: string;
  workspace: WorkspaceState;
  controller: SignalsController;
  onApproveSignal: (signal: SourceSignal) => void;
  onRejectSignal: (signal: SourceSignal) => void;
  onArchiveSignal: (signal: SourceSignal) => void;
  onReopenSignal: (signal: SourceSignal) => void;
  onRestoreSignal: (signal: SourceSignal) => void;
  onRescoreSignal: (signal: SourceSignal) => void;
  onCreateInsight: () => void;
  onPlan: () => void;
}) {
  const currentSignals = controller.filteredSignals.filter((signal) => signal.legacyIntegrityStatus !== 'needsReExtraction');
  const currentIds = new Set(currentSignals.map((signal) => signal.id));
  const visibleCurrentSignals = currentSignals.filter((signal) => {
    const report = signal.relationshipReport ?? signal.utilityReport?.relationshipReport;
    return !report || report.canonicalSignalId === signal.id || !currentIds.has(report.canonicalSignalId);
  });
  return (
    <div className="memory-grid signals-workspace-grid">
      <section className="memory-main">
        <SignalFilterToolbar workspace={workspace} controller={controller} />
        <div className="entity-list signals-entity-list" data-testid="source-signal-list">
          {visibleCurrentSignals.map((signal) => (
            <SourceSignalCard
              projectId={projectId}
              key={signal.id}
              signal={signal}
              workspace={workspace}
              controller={controller}
              onApproveSignal={onApproveSignal}
              onRejectSignal={onRejectSignal}
              onArchiveSignal={onArchiveSignal}
              onReopenSignal={onReopenSignal}
              onRestoreSignal={onRestoreSignal}
              onRescoreSignal={onRescoreSignal}
            />
          ))}
          {controller.filteredSignals.some((signal) => signal.legacyIntegrityStatus === 'needsReExtraction') ? (
            <section className="legacy-signal-group" data-testid="legacy-signal-group">
              <h3>Требуется повторное извлечение</h3>
              <p>Старые сигналы отделены от актуальных: их прежняя клиентская оценка не считается текущим решением.</p>
              {controller.filteredSignals.filter((signal) => signal.legacyIntegrityStatus === 'needsReExtraction').map((signal) => (
                <SourceSignalCard
                  projectId={projectId}
                  key={signal.id}
                  signal={signal}
                  workspace={workspace}
                  controller={controller}
                  onApproveSignal={onApproveSignal}
                  onRejectSignal={onRejectSignal}
                  onArchiveSignal={onArchiveSignal}
                  onReopenSignal={onReopenSignal}
                  onRestoreSignal={onRestoreSignal}
                  onRescoreSignal={onRescoreSignal}
                />
              ))}
            </section>
          ) : null}
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
      <select
        aria-label="Фильтр отбора сигнала"
        data-testid="signal-filter-status-filter"
        value={controller.filterStatusFilter}
        onChange={(event) => controller.setFilterStatusFilter(event.target.value as 'all' | SignalUtilityRecommendation | 'unscored' | 'legacy')}
      >
        <option value="all">Любая полезность</option>
        <option value="recommended">Рекомендуются</option>
        <option value="reviewWithCaution">Проверить с осторожностью</option>
        <option value="notRecommended">Не рекомендуются</option>
        <option value="inconclusive">Оценка не завершена</option>
        <option value="unscored">Не оценены</option>
        <option value="legacy">Требуется повторное извлечение</option>
      </select>
    </div>
  );
}
