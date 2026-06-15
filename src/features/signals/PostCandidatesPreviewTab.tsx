import type { WorkspaceState } from '../../domain/editorialWorkspace';
import { SummaryItem } from './helpers';
import { SignalsSidePanel } from './SignalsSidePanel';
import type { SignalsController } from './useSignalsController';

export function PostCandidatesPreviewTab({
  workspace,
  controller,
  onCreateInsight,
  onPlan
}: {
  workspace: WorkspaceState;
  controller: SignalsController;
  onCreateInsight: () => void;
  onPlan: () => void;
}) {
  return (
    <div className="memory-grid signals-workspace-grid">
      <section className="card draft-start">
        <span className="rub">Slice 1.6</span>
        <h2>Кандидаты постов появятся после утверждения сигналов</h2>
        <p>
          Следующий слой соберет комбинации «Сигнал + Тема + Фабула + ЦА + Ценность».
          Пока сигналы остаются сырьем: их нужно принять, отклонить, архивировать или уточнить.
        </p>
        <div className="signal-summary-grid">
          <SummaryItem label="Утверждено" value={controller.signalSummary.approved} />
          <SummaryItem label="Новые" value={controller.signalSummary.new} />
          <SummaryItem label="Дубль high" value={controller.signalSummary.highRisk} />
        </div>
      </section>
      <SignalsSidePanel workspace={workspace} summary={controller.signalSummary} onCreateInsight={onCreateInsight} onPlan={onPlan} />
    </div>
  );
}
