import type {
  BroadcastGridDemandSummary,
  ContentPlanItem,
  PlanWeightWarning
} from '../../domain/editorialWorkspace';

export function BroadcastGridAside({
  demandSummary,
  fabulaDistribution,
  items,
  topicDistribution,
  warnings
}: {
  demandSummary: BroadcastGridDemandSummary;
  fabulaDistribution: Array<{ title: string; count: number; share: number }>;
  items: ContentPlanItem[];
  topicDistribution: Array<{ title: string; count: number; share: number }>;
  warnings: PlanWeightWarning[];
}) {
  const activeWarnings = warnings.filter((warning) => warning.severity !== 'green');

  return (
    <aside className="aside broadcast-aside">
      <div className="panel validation-panel">
        <div className="validation-head">
          <h3>Сетка вещания</h3>
          <span className={`validation-run-state ${activeWarnings.length > 0 ? 'stale' : 'fresh'}`}>
            {activeWarnings.length > 0 ? 'Есть конфликты' : 'Баланс OK'}
          </span>
          <p>
            Настройки задают календарный каркас. План можно собрать даже при дефиците кандидатов, но summary показывает,
            хватает ли сырья для редакционного выбора.
          </p>
        </div>
        <div className="validator-summary">
          <div><strong>{demandSummary.slotCount}</strong><span>слотов</span></div>
          <div><strong>{demandSummary.availableCandidateCount}</strong><span>доступно</span></div>
          <div><strong>{demandSummary.approvedConceptCount}</strong><span>утвержд.</span></div>
          <div><strong>{items.length}</strong><span>в плане</span></div>
        </div>
        <div className={`plan-demand-state ${demandSummary.status}`}>
          {demandSummary.status === 'deficit'
            ? `Дефицит: ${demandSummary.deficit} кандидатов до минимума`
            : demandSummary.status === 'surplus'
              ? `Профицит: ${demandSummary.surplus} кандидатов сверх лимита`
              : 'Кандидатов достаточно для выбранной сетки'}
        </div>
        <DistributionList title="Темы" items={topicDistribution} />
        <DistributionList title="Фабулы" items={fabulaDistribution} />
        {activeWarnings.length > 0 ? (
          <div className="validation-warnings">
            {activeWarnings.slice(0, 6).map((warning) => <p key={warning.id}>{warning.message}</p>)}
          </div>
        ) : null}
      </div>
    </aside>
  );
}

function DistributionList({ title, items }: { title: string; items: Array<{ title: string; count: number; share: number }> }) {
  return (
    <div className="plan-distribution">
      <h4>{title}</h4>
      {items.length > 0 ? (
        items.map((item) => (
          <div className="plan-distribution-row" key={item.title}>
            <span>{item.title}</span>
            <b>{Math.round(item.share)}%</b>
          </div>
        ))
      ) : (
        <p className="panel-note">Нет слотов для расчета.</p>
      )}
    </div>
  );
}
