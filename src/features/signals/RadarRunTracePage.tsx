import { useEffect, useMemo, useState } from 'react';
import { fetchRadarRunTrace, retryRadarRunSignalExtraction, type RadarRunTraceBundle } from '../../infrastructure/radarRunTraceClient';
import { Icon } from '../../shared/ui/Icon';
import {
  buildRadarRunTraceViewModel,
  displayRadarTraceValue,
  type RadarRunTraceViewModel,
  type RadarTraceDetail,
  type RadarTraceField,
  type RadarTraceItem,
  type RadarTraceTimelineItem
} from './radarRunTraceViewModel';

type DetailTab = 'readable' | 'json';

export function RadarRunTracePage() {
  const params = useMemo(() => new URLSearchParams(window.location.search), []);
  const initialRunId = params.get('runId') ?? '';
  const projectId = params.get('projectId') ?? undefined;
  const [runId, setRunId] = useState(initialRunId);
  const [trace, setTrace] = useState<RadarRunTraceBundle | null>(null);
  const [status, setStatus] = useState<'idle' | 'loading' | 'failed'>('idle');
  const [error, setError] = useState('');

  useEffect(() => {
    if (initialRunId) void loadTrace(initialRunId);
  }, [initialRunId]);

  async function loadTrace(targetRunId = runId) {
    setStatus('loading');
    setError('');
    try {
      setTrace(await fetchRadarRunTrace(targetRunId, projectId));
      setStatus('idle');
    } catch (caught) {
      setTrace(null);
      setError(caught instanceof Error ? caught.message : 'RadarRun trace request failed');
      setStatus('failed');
    }
  }

  return (
    <main className="ai-run-page radar-run-page fade-up">
      <section className="card ai-run-header">
        <div>
          <span className="rub">RadarRun trace</span>
          <h1>Трассировка радара</h1>
          <p>Введите RadarRun ID, чтобы увидеть карту поиска, операции, отбор источников и найденные материалы.</p>
        </div>
        <a className="btn btn-sec" href="/">
          В кабинет
        </a>
      </section>

      <section className="card ai-run-search">
        <label>
          <span className="k">RadarRun ID</span>
          <input
            aria-label="RadarRun ID"
            value={runId}
            onChange={(event) => setRunId(event.target.value)}
            placeholder="Например: radar-run-..."
          />
        </label>
        <button className="btn btn-pri" type="button" disabled={status === 'loading'} onClick={() => void loadTrace()}>
          <Icon name="search" size={16} />
          {status === 'loading' ? 'Загружаем' : 'Показать трассу'}
        </button>
      </section>

      {status === 'failed' ? <div className="card empty-state ai-run-error">{error}</div> : null}
      {trace ? <RadarRunTraceDetails trace={trace} /> : status !== 'failed' ? (
        <section className="card empty-state">Трассировка появится здесь после запроса.</section>
      ) : null}
    </main>
  );
}

function RadarRunTraceDetails({ trace }: { trace: RadarRunTraceBundle }) {
  const [currentTrace, setCurrentTrace] = useState(trace);
  const [retryStatus, setRetryStatus] = useState<'idle' | 'loading' | 'failed'>('idle');
  const viewModel = useMemo(() => buildRadarRunTraceViewModel(currentTrace), [currentTrace]);
  const [selectedDetailId, setSelectedDetailId] = useState(viewModel.initialDetailId);
  const selectedDetail = viewModel.details.find((detail) => detail.id === selectedDetailId) ?? viewModel.details[0];

  useEffect(() => {
    setSelectedDetailId(viewModel.initialDetailId);
  }, [viewModel.initialDetailId]);

  useEffect(() => setCurrentTrace(trace), [trace]);

  async function retryExtraction() {
    setRetryStatus('loading');
    try {
      setCurrentTrace(await retryRadarRunSignalExtraction(currentTrace));
      setRetryStatus('idle');
      setSelectedDetailId('signal-extraction');
    } catch {
      setRetryStatus('failed');
    }
  }

  return (
    <section className="ai-run-details radar-run-details" aria-label="RadarRun trace details">
      <div className="radar-run-trace-actions">
        <button className="btn btn-sec btn-sm" type="button" disabled={retryStatus === 'loading'} onClick={() => void retryExtraction()}>
          <Icon name="reset" size={16} />
          {retryStatus === 'loading' ? 'Повторяем извлечение' : 'Повторить извлечение сигналов'}
        </button>
        {retryStatus === 'failed' ? <span className="muted">Повтор извлечения не выполнен. Проверьте backend trace.</span> : null}
      </div>
      <RadarRunTraceSummary viewModel={viewModel} />
      <div className="ai-run-workbench radar-run-workbench">
        <RadarRunTimeline
          items={viewModel.timeline}
          selectedDetailId={selectedDetail?.id ?? ''}
          onSelect={setSelectedDetailId}
        />
        <RadarRunDetailPanel detail={selectedDetail} />
      </div>
    </section>
  );
}

function RadarRunTraceSummary({ viewModel }: { viewModel: RadarRunTraceViewModel }) {
  return (
    <section className="card ai-run-summary radar-run-summary" data-testid="radar-run-summary">
      {viewModel.summary.map((field) => (
        <div className="summary-item" key={field.label}>
          <b>{field.value}</b>
          <span>{field.label}</span>
        </div>
      ))}
    </section>
  );
}

function RadarRunTimeline({
  items,
  selectedDetailId,
  onSelect
}: {
  items: RadarTraceTimelineItem[];
  selectedDetailId: string;
  onSelect: (detailId: string) => void;
}) {
  return (
    <section className="card ai-run-panel ai-run-timeline radar-run-timeline" data-testid="radar-run-timeline">
      <span className="rub">Индекс трассы</span>
      <div className="ai-run-timeline-list">
        {items.map((item) => (
          <article className="ai-run-timeline-step" key={item.id}>
            <button
              className={selectedDetailId === item.detailId ? 'active' : ''}
              type="button"
              onClick={() => onSelect(item.detailId)}
            >
              <span className="ai-run-step-key">{item.id.replace('timeline-', '')}</span>
              <strong>{item.title}</strong>
              <span className={`ai-run-status ${item.status}`}>{item.status}</span>
            </button>
            <p className="radar-run-timeline-meta">{item.meta}</p>
          </article>
        ))}
      </div>
    </section>
  );
}

function RadarRunDetailPanel({ detail }: { detail?: RadarTraceDetail }) {
  const [tab, setTab] = useState<DetailTab>('readable');
  if (!detail) {
    return <section className="card ai-run-panel ai-run-detail-panel">Нет выбранного элемента.</section>;
  }
  return (
    <aside className="card ai-run-panel ai-run-detail-panel radar-run-detail-panel" data-testid="radar-run-detail-panel">
      <div className="ai-run-panel-head">
        <div>
          <span className="rub">Детали</span>
          <h2>{detail.title}</h2>
          <p>{detail.kicker}</p>
        </div>
        <button className="btn btn-sec btn-sm" type="button" onClick={() => void copyDetail(detail, tab)}>
          Копировать
        </button>
      </div>
      <div className="tabs ai-run-detail-tabs" role="tablist" aria-label="RadarRun detail tabs">
        <TraceTab active={tab === 'readable'} onClick={() => setTab('readable')}>Readable</TraceTab>
        <TraceTab active={tab === 'json'} onClick={() => setTab('json')}>JSON</TraceTab>
      </div>
      {tab === 'readable' ? (
        <div className="ai-run-readable-detail">
          <RadarTraceFields fields={detail.fields} />
          <RadarTraceItems items={detail.items} />
        </div>
      ) : (
        <pre className="ai-run-json-block" data-testid="radar-run-json">{displayRadarTraceValue(detail.jsonPayload)}</pre>
      )}
    </aside>
  );
}

function RadarTraceFields({ fields }: { fields: RadarTraceField[] }) {
  if (fields.length === 0) return null;
  return (
    <dl className="ai-run-fields">
      {fields.map((field) => (
        <div key={field.label}>
          <dt>{field.label}</dt>
          <dd>{field.value}</dd>
        </div>
      ))}
    </dl>
  );
}

function RadarTraceItems({ items }: { items: RadarTraceItem[] }) {
  if (items.length === 0) return <p className="muted radar-run-empty-detail">Нет детальных записей для этого раздела.</p>;
  return (
    <div className="radar-run-item-list">
      {items.map((item) => (
        <article className="radar-run-item" key={item.id}>
          <div>
            <span className="sig">{item.label}</span>
            {item.status ? <span className={`ai-run-status ${item.status}`}>{item.status}</span> : null}
          </div>
          <strong>{item.title}</strong>
          {item.body ? <p>{item.body}</p> : null}
          {item.meta?.length ? <RadarTraceFields fields={item.meta} /> : null}
        </article>
      ))}
    </div>
  );
}

function TraceTab({ active, children, onClick }: { active: boolean; children: string; onClick: () => void }) {
  return (
    <button className={`tab${active ? ' active' : ''}`} type="button" role="tab" aria-selected={active} onClick={onClick}>
      {children}
    </button>
  );
}

async function copyDetail(detail: RadarTraceDetail, tab: DetailTab) {
  if (!navigator.clipboard) return;
  const payload = tab === 'json' ? detail.jsonPayload : { fields: detail.fields, items: detail.items };
  await navigator.clipboard.writeText(displayRadarTraceValue(payload));
}
