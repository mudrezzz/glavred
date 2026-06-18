import { useEffect, useMemo, useState } from 'react';
import { fetchAiRunTrace, type AiRunTrace } from '../../infrastructure/aiRunTraceClient';
import { Icon } from '../../shared/ui/Icon';

export function AiRunTracePage() {
  const initialRunId = useMemo(() => new URLSearchParams(window.location.search).get('runId') ?? '', []);
  const [runId, setRunId] = useState(initialRunId);
  const [trace, setTrace] = useState<AiRunTrace | null>(null);
  const [status, setStatus] = useState<'idle' | 'loading' | 'failed'>('idle');
  const [error, setError] = useState('');

  useEffect(() => {
    if (initialRunId) {
      void loadTrace(initialRunId);
    }
  }, [initialRunId]);

  async function loadTrace(targetRunId = runId) {
    setStatus('loading');
    setError('');
    try {
      setTrace(await fetchAiRunTrace(targetRunId));
      setStatus('idle');
    } catch (caught) {
      setTrace(null);
      setError(caught instanceof Error ? caught.message : 'AI run request failed');
      setStatus('failed');
    }
  }

  return (
    <main className="ai-run-page fade-up">
      <section className="card ai-run-header">
        <div>
          <span className="rub">AI run trace</span>
          <h1>Трассировка запуска</h1>
          <p>Введите run-id, чтобы посмотреть prompt/messages, provider metadata, результат и fallback context из backend audit.</p>
        </div>
        <a className="btn btn-sec" href="/">
          В кабинет
        </a>
      </section>

      <section className="card ai-run-search">
        <label>
          <span className="k">Run ID</span>
          <input
            aria-label="Run ID"
            value={runId}
            onChange={(event) => setRunId(event.target.value)}
            placeholder="Например: airun-..."
          />
        </label>
        <button className="btn btn-pri" type="button" disabled={status === 'loading'} onClick={() => void loadTrace()}>
          <Icon name="search" size={16} />
          {status === 'loading' ? 'Загружаем' : 'Показать трассировку'}
        </button>
      </section>

      {status === 'failed' ? <div className="card empty-state ai-run-error">{error}</div> : null}
      {trace ? <AiRunTraceDetails trace={trace} /> : status !== 'failed' ? (
        <section className="card empty-state">
          Трассировка появится здесь после запроса.
        </section>
      ) : null}
    </main>
  );
}

function AiRunTraceDetails({ trace }: { trace: AiRunTrace }) {
  return (
    <section className="ai-run-details">
      <div className="card ai-run-summary">
        <TraceMetric label="Capability" value={trace.capability} />
        <TraceMetric label="Status" value={trace.status} />
        <TraceMetric label="Provider" value={trace.provider} />
        <TraceMetric label="Model" value={trace.model ?? 'none'} />
        <TraceMetric label="Fallback" value={trace.fallbackUsed ? 'yes' : 'no'} />
        <TraceMetric label="Created" value={trace.createdAt} />
      </div>

      {trace.error ? (
        <section className="card ai-run-panel warning">
          <span className="rub">Error</span>
          <p>{trace.error}</p>
        </section>
      ) : null}

      <TraceJson title="Request payload" value={trace.requestPayload} />
      <TraceJson title="Result payload" value={trace.resultPayload ?? {}} />
    </section>
  );
}

function TraceMetric({ label, value }: { label: string; value: string }) {
  return (
    <div className="summary-item">
      <b>{value}</b>
      <span>{label}</span>
    </div>
  );
}

function TraceJson({ title, value }: { title: string; value: Record<string, unknown> }) {
  return (
    <section className="card ai-run-panel">
      <span className="rub">{title}</span>
      <pre>{JSON.stringify(value, null, 2)}</pre>
    </section>
  );
}
