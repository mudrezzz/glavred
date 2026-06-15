import {
  validatorDefinitionTitle,
  type EditorialValidationRun,
  type ValidatorResult
} from '../../domain/editorialWorkspace';
import { editorialTabLabel, formatDateTime } from './helpers';
import type { EditorialModelTab } from './types';

export function EditorialValidationPanel({
  validationRun,
  currentRevision,
  activeTab,
  onRunValidation
}: {
  validationRun: EditorialValidationRun | null;
  currentRevision: number;
  activeTab: EditorialModelTab;
  onRunValidation: () => void;
}) {
  const validation = validationRun?.summary ?? null;
  const validatorResults = validationRun?.results ?? [];
  const aggregateStatus = validationRun?.aggregateStatus ?? validation?.status ?? null;
  const aggregateScore = validationRun?.aggregateScore ?? 0;
  const isStale = Boolean(validationRun && validationRun.revision !== currentRevision);
  const runState = !validationRun ? 'Еще не проверено' : isStale ? 'Требует повторной проверки' : 'Проверено';

  return (
    <aside className="card validation-panel">
      <div className="validation-head">
        <span className="mono-label">Проверка</span>
        <span className={`validation-run-state ${!validationRun ? 'empty' : isStale ? 'stale' : 'fresh'}`}>
          {runState}
        </span>
        {aggregateStatus ? <ValidationBadge status={aggregateStatus} /> : null}
        <h3>{validation?.title ?? 'Проверка еще не запускалась'}</h3>
        <p>
          {validation
            ? validation.summary
            : 'Заполните или отредактируйте правила, темы, фабулы и матрицу, затем запустите проверку вручную.'}
        </p>
        {isStale ? (
          <p className="validation-stale-note">
            После последней проверки были сохранены изменения. Запустите проверку повторно, чтобы получить актуальный вывод.
          </p>
        ) : null}
        <button className="btn btn-pri btn-sm" type="button" onClick={onRunValidation}>
          Проверить
        </button>
      </div>
      {validation ? (
        <div className="validator-summary">
          <div>
            <span className="mono-label">Score</span>
            <strong>{Math.round(aggregateScore * 100)}%</strong>
          </div>
          <div>
            <span className="mono-label">Validators</span>
            <strong>{validatorResults.length || validation.items.length}</strong>
          </div>
        </div>
      ) : null}
      {validatorResults.length > 0 ? (
        <div className="validation-items validator-cards">
          {validatorResults.map((result) => (
            <ValidatorCard key={result.id} result={result} />
          ))}
        </div>
      ) : validation ? (
        <div className="validation-items">
          {validation.items.map((item) => (
            <article className="validation-item" key={item.id}>
              <div>
                <ValidationBadge status={item.status} />
                <b>{item.title}</b>
              </div>
              <p>{item.summary}</p>
              <small>{item.recommendation}</small>
            </article>
          ))}
        </div>
      ) : null}
      <p className="validation-note">
        Вкладка: {editorialTabLabel(activeTab)}. Проверка deterministic, без AI provider. Результат обновляется только по кнопке.
      </p>
      {validationRun ? <p className="validation-note">Последняя проверка: {formatDateTime(validationRun.checkedAt)}</p> : null}
    </aside>
  );
}

function ValidatorCard({ result }: { result: ValidatorResult }) {
  return (
    <article className="validation-item validator-card">
      <div className="validator-card-head">
        <ValidationBadge status={result.status} />
        <div>
          <b>{validatorDefinitionTitle(result.validatorId)}</b>
          <span>{result.validatorId}</span>
        </div>
        <strong>{Math.round(result.score * 100)}%</strong>
      </div>
      <p>{result.summary}</p>
      <details className="validator-details">
        <summary>Evidence и рекомендации</summary>
        <div className="validator-detail-block">
          <span className="mono-label">Evidence</span>
          {result.evidence.length > 0 ? (
            result.evidence.map((item) => (
              <blockquote key={item.id}>
                <b>{item.title}</b>
                <p>{item.quote}</p>
                <small>{item.reason}</small>
              </blockquote>
            ))
          ) : (
            <p className="muted-text">Evidence пока нет.</p>
          )}
        </div>
        <div className="validator-detail-block">
          <span className="mono-label">Suggestions</span>
          {result.suggestions.length > 0 ? (
            result.suggestions.map((item) => (
              <div className={`validator-suggestion ${item.severity}`} key={item.id}>
                <b>{item.title}</b>
                <p>{item.description}</p>
              </div>
            ))
          ) : (
            <p className="muted-text">Рекомендаций нет.</p>
          )}
        </div>
      </details>
    </article>
  );
}

export function ValidationBadge({ status }: { status: 'green' | 'yellow' | 'red' }) {
  const label = status === 'green' ? 'ок' : status === 'yellow' ? 'внимание' : 'риск';
  return <span className={`validation-badge ${status}`}>{label}</span>;
}
