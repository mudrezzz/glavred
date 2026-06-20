import { useEffect, useMemo, useState } from 'react';
import { fetchRunTrace, type RunTraceBundle } from '../../infrastructure/runTraceClient';
import { Icon } from '../../shared/ui/Icon';
import { AiRunTraceDetails } from './AiRunTraceDetails';

export function AiRunTracePage() {
  const initialRunId = useMemo(() => new URLSearchParams(window.location.search).get('runId') ?? '', []);
  const [runId, setRunId] = useState(initialRunId);
  const [trace, setTrace] = useState<RunTraceBundle | null>(null);
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
      setTrace(await fetchRunTrace(targetRunId));
      setStatus('idle');
    } catch (caught) {
      setTrace(null);
      setError(caught instanceof Error ? caught.message : 'Run trace request failed');
      setStatus('failed');
    }
  }

  return (
    <main className="ai-run-page fade-up">
      <section className="card ai-run-header">
        <div>
          <span className="rub">AI run trace</span>
          <h1>Трассировка запуска</h1>
          <p>
            Введите DraftRun ID, чтобы увидеть весь агентный пайплайн, или AiRun ID,
            чтобы разобрать один provider call.
          </p>
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
            placeholder="Например: draftrun-... или airun-..."
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
