import type { SourceSignal, WorkspaceState } from '../../domain/editorialWorkspace';
import {
  duplicateRiskLabel,
  formatDate,
  radarFilterDimensionLabel,
  signalFilterEvaluationLabel,
  signalFilterStatusLabel,
  signalReviewStatusLabel
} from './helpers';
import type { SignalsController } from './useSignalsController';

export function SourceSignalCard({
  signal,
  workspace,
  controller,
  onApproveSignal,
  onRejectSignal,
  onArchiveSignal
}: {
  signal: SourceSignal;
  workspace: WorkspaceState;
  controller: SignalsController;
  onApproveSignal: (signal: SourceSignal) => void;
  onRejectSignal: (signal: SourceSignal) => void;
  onArchiveSignal: (signal: SourceSignal) => void;
}) {
  const radar = workspace.radars.find((item) => item.id === signal.radarId);
  const expanded = controller.expandedSignalId === signal.id;
  const editing = controller.editingSignal?.id === signal.id;

  return (
    <article className={`entity-row signal-card ${expanded ? 'expanded' : ''}`} data-testid="source-signal-row">
      <button className="signal-row-main" type="button" onClick={() => controller.setExpandedSignalId(expanded ? '' : signal.id)}>
        <span className="signal-row-top">
          <span className="sig signal-radar">{radar?.title ?? signal.source}</span>
          <span className={`pill signal-status ${signal.reviewStatus === 'approved' ? 'ok' : 'pin'}`}>
            <span>{signalReviewStatusLabel(signal.reviewStatus)}</span>
          </span>
        </span>
        <strong className="signal-title">{signal.title}</strong>
        <span className="signal-row-meta">
          <span className="signal-date">{formatDate(signal.capturedAt)}</span>
          <span className={`sc signal-risk risk-${signal.duplicateRisk ?? 'low'}`}>дубль {duplicateRiskLabel(signal.duplicateRisk ?? 'low')}</span>
          <span className={`sc signal-filter-status filter-status-${signal.filterStatus ?? 'passed'}`}>{signalFilterStatusLabel(signal.filterStatus)}</span>
        </span>
      </button>

      {expanded && !editing && (
        <div className="radar-details">
          <section className="signal-detail-section">
            <h4>Сводка</h4>
            <p>{signal.summary}</p>
          </section>
          <dl className="meta-list">
            <dt>Радар</dt>
            <dd>{radar?.title ?? signal.source}</dd>
            <dt>Дата</dt>
            <dd>{formatDate(signal.capturedAt)}</dd>
            <dt>Источник</dt>
            <dd>{signal.source}</dd>
            <dt>Что нашли</dt>
            <dd>{signal.rawNote}</dd>
            {signal.confidence && (
              <>
                <dt>Уверенность</dt>
                <dd>{signal.confidence}</dd>
              </>
            )}
            {signal.uncertainty && (
              <>
                <dt>Неопределённость</dt>
                <dd>{signal.uncertainty}</dd>
              </>
            )}
            {signal.mechanism && (
              <>
                <dt>Механизм</dt>
                <dd>{signal.mechanism}</dd>
              </>
            )}
            {signal.outcome && (
              <>
                <dt>Результат</dt>
                <dd>{signal.outcome}</dd>
              </>
            )}
            {(signal.limitations ?? []).length > 0 && (
              <>
                <dt>Ограничения</dt>
                <dd>{signal.limitations?.join('; ')}</dd>
              </>
            )}
            <dt>Поиск дублей</dt>
            <dd>{signal.searchNote ?? `Риск дубля: ${signal.duplicateRisk ?? 'low'}`}</dd>
            <dt>Правка автора</dt>
            <dd>{signal.authorCorrection || 'нет'}</dd>
          </dl>
          <FilterEvaluations signal={signal} />
          <EvidenceList signal={signal} />
          <div className="row-actions signal-actions entity-actions-footer">
            <button className="btn btn-pri btn-sm" type="button" onClick={() => onApproveSignal(signal)}>
              Утвердить сигнал
            </button>
            <button className="btn btn-sec btn-sm" type="button" onClick={() => controller.startSignalEdit(signal)}>
              Редактировать
            </button>
            <button className="btn btn-ghost btn-sm" type="button" onClick={() => onArchiveSignal(signal)}>
              В архив
            </button>
            <button className="btn btn-ghost btn-sm" type="button" onClick={() => onRejectSignal(signal)}>
              Отклонить
            </button>
          </div>
        </div>
      )}

      {expanded && editing && controller.editingSignal && (
        <div className="signal-edit-form">
          <label>
            <span>Инсайт</span>
            <input value={controller.editingSignal.title} onChange={(event) => controller.patchSignalDraft({ title: event.target.value })} />
          </label>
          <label>
            <span>Краткая сводка</span>
            <textarea value={controller.editingSignal.summary} onChange={(event) => controller.patchSignalDraft({ summary: event.target.value })} />
          </label>
          <label>
            <span>Что нашли</span>
            <textarea value={controller.editingSignal.rawNote} onChange={(event) => controller.patchSignalDraft({ rawNote: event.target.value })} />
          </label>
          <label>
            <span>Поиск дублей</span>
            <textarea value={controller.editingSignal.searchNote ?? ''} onChange={(event) => controller.patchSignalDraft({ searchNote: event.target.value })} />
          </label>
          <label>
            <span>Правка автора</span>
            <textarea value={controller.editingSignal.authorCorrection ?? ''} onChange={(event) => controller.patchSignalDraft({ authorCorrection: event.target.value })} />
          </label>
          <div className="row-actions signal-actions entity-actions-footer">
            <button className="btn btn-pri btn-sm" type="button" onClick={controller.saveSignalDraft}>
              Сохранить
            </button>
            <button className="btn btn-sec btn-sm" type="button" onClick={() => controller.setEditingSignal(null)}>
              Отменить
            </button>
          </div>
        </div>
      )}
    </article>
  );
}

function FilterEvaluations({ signal }: { signal: SourceSignal }) {
  return (
    <div className="radar-config-section signal-filter-evaluations" data-testid="signal-filter-evaluations">
      <h4>Фильтры отбора</h4>
      {(signal.filterEvaluations ?? []).length > 0 ? (
        <div className="signal-filter-list">
          {(signal.filterEvaluations ?? []).map((evaluation) => (
            <div className={`signal-filter-evaluation filter-eval-${evaluation.status}`} key={evaluation.filterId}>
              <span className={`sc filter-status-${evaluation.status}`}>{signalFilterEvaluationLabel(evaluation.status)}</span>
              <div>
                <strong>{radarFilterDimensionLabel(evaluation.dimension)} · {evaluation.score}%</strong>
                <p>{evaluation.summary}</p>
                <small>{evaluation.evidence}</small>
              </div>
            </div>
          ))}
        </div>
      ) : (
        <p className="muted">Для этого сигнала еще нет оценки фильтров.</p>
      )}
    </div>
  );
}

function EvidenceList({ signal }: { signal: SourceSignal }) {
  return (
    <div className="radar-config-section">
      <h4>Доказательства</h4>
      <div className="signal-evidence-list">
        {(signal.evidence ?? []).map((item) => (
          <div className="signal-evidence" key={item.id}>
            <span className="sig">{item.sourceTitle}</span>
            <p>{item.quote}</p>
            <small>{item.summary}</small>
          </div>
        ))}
      </div>
    </div>
  );
}
