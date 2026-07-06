import { useMemo, useState } from 'react';
import type { RunTraceBundle } from '../../infrastructure/runTraceClient';
import { Icon } from '../../shared/ui/Icon';
import {
  buildRunTraceViewModel,
  prettyTraceValue,
  type RunTraceViewModel,
  type TraceDetail,
  type TraceMessage,
  type TraceScorecardModel,
  type TraceSemanticSection,
  type TraceStepOperation,
  type TraceTimelineStep
} from './runTraceViewModel';
import { buildQualityFidelityViewModel, type QualityFidelityViewModel } from './qualityFidelityViewModel';

type MainTab = 'trace' | 'semantic';
type DetailTab = 'readable' | 'json' | 'raw';

export function AiRunTraceDetails({ trace }: { trace: RunTraceBundle }) {
  const viewModel = useMemo(() => buildRunTraceViewModel(trace), [trace]);
  const qualityFidelity = useMemo(() => buildQualityFidelityViewModel(trace), [trace]);
  const [mainTab, setMainTab] = useState<MainTab>('trace');
  const [selectedDetailId, setSelectedDetailId] = useState(viewModel.initialDetailId);
  const selectedDetail = viewModel.details.find((detail) => detail.id === selectedDetailId) ?? viewModel.details[0];

  return (
    <section className="ai-run-details" aria-label="Run trace details">
      <AiRunTraceSummary viewModel={viewModel} />
      {qualityFidelity ? <AiRunQualityFidelityPanel quality={qualityFidelity} /> : null}
      <div className="tabs ai-run-main-tabs" role="tablist" aria-label="Trace view tabs">
        <TraceTab active={mainTab === 'trace'} onClick={() => setMainTab('trace')}>Трейс</TraceTab>
        <TraceTab active={mainTab === 'semantic'} onClick={() => setMainTab('semantic')}>Смысловой результат</TraceTab>
      </div>
      {mainTab === 'trace' ? (
        <div className="ai-run-workbench">
          <AiRunTimeline
            steps={viewModel.timeline}
            selectedDetailId={selectedDetail?.id ?? ''}
            onSelect={setSelectedDetailId}
          />
          <AiRunDetailPanel detail={selectedDetail} />
        </div>
      ) : (
        <AiRunSemanticSections sections={viewModel.semanticSections} />
      )}
    </section>
  );
}

function AiRunQualityFidelityPanel({ quality }: { quality: QualityFidelityViewModel }) {
  return (
    <section className={`card ai-run-quality-panel ${quality.tone}`} data-testid="ai-run-quality-fidelity">
      <div className="ai-run-panel-head">
        <div>
          <span className="rub">Quality/fidelity</span>
          <h2>{quality.overallVerdict}</h2>
          <p>Technical, provider, evidence and editorial verdicts are separated for this run.</p>
        </div>
        <span className={`ai-run-status ${quality.tone}`}>{quality.editorialStatus}</span>
      </div>
      <div className="ai-run-quality-grid">
        <article>
          <span>Technical health</span>
          <strong>{quality.technicalStatus}</strong>
        </article>
        <article>
          <span>Provider recovery</span>
          <strong>{quality.providerRecoveryStatus}</strong>
        </article>
        <article>
          <span>Evidence fidelity</span>
          <strong>{quality.evidenceCoverage}</strong>
        </article>
        <article>
          <span>Editorial verdict</span>
          <strong>{quality.editorialStatus}</strong>
        </article>
      </div>
      <div className="ai-run-quality-columns">
        <TraceFields fields={quality.providerFields} />
        <TraceFields fields={quality.evidenceFields} />
        <TraceFields fields={quality.editorialFields} />
      </div>
    </section>
  );
}

function AiRunTraceSummary({ viewModel }: { viewModel: RunTraceViewModel }) {
  return (
    <section className="card ai-run-summary">
      {viewModel.summary.map((field) => (
        <div className="summary-item" key={field.label}>
          <b>{field.value}</b>
          <span>{field.label}</span>
        </div>
      ))}
    </section>
  );
}

function AiRunTimeline({
  steps,
  selectedDetailId,
  onSelect
}: {
  steps: TraceTimelineStep[];
  selectedDetailId: string;
  onSelect: (detailId: string) => void;
}) {
  return (
    <section className="card ai-run-panel ai-run-timeline" data-testid="ai-run-timeline">
      <span className="rub">Логические шаги</span>
      <div className="ai-run-timeline-list">
        {steps.map((step) => (
          <article className="ai-run-timeline-step" key={step.id}>
            <button
              className={selectedDetailId === step.detailId ? 'active' : ''}
              type="button"
              onClick={() => onSelect(step.detailId)}
            >
              <span className="ai-run-step-key">{step.key}</span>
              <strong>{step.title}</strong>
              <span className={`ai-run-status ${step.status}`}>{step.status}</span>
            </button>
            {step.error ? <p className="ai-run-step-error">{step.error}</p> : null}
            {step.operations.length > 0 ? <AiRunOperations operations={step.operations} /> : null}
            {step.childCalls.length > 0 ? (
              <div className="ai-run-child-calls">
                {step.childCalls.map((call) => (
                  <button
                    className={`${selectedDetailId === call.detailId ? 'active' : ''}${call.kind === 'artifact' ? ' artifact' : ''}`}
                    type="button"
                    key={call.id}
                    onClick={() => onSelect(call.detailId)}
                  >
                    <span className="ai-run-call-icon">
                      <Icon name="spark" size={14} />
                    </span>
                    <span className="ai-run-call-body">
                      <strong>{call.title}</strong>
                      <span className="ai-run-call-meta">
                        {call.meta && call.meta.length > 0 ? (
                          call.meta.map((field) => (
                            <small key={field.label}>
                              <span>{field.label}</span> {field.value}
                            </small>
                          ))
                        ) : (
                          <>
                            <small>{call.provider} · {call.model}</small>
                            <small>fallback {call.fallback}</small>
                            <code>{call.id}</code>
                          </>
                        )}
                      </span>
                    </span>
                  </button>
                ))}
              </div>
            ) : null}
          </article>
        ))}
      </div>
    </section>
  );
}

function AiRunOperations({ operations }: { operations: TraceStepOperation[] }) {
  return (
    <div className="ai-run-operations" aria-label="Step operations">
      {operations.map((operation) => (
        <article className={`ai-run-operation ${operation.status}`} key={operation.id}>
          <span className="ai-run-operation-dot" aria-hidden="true" />
          <div>
            <strong>{operation.label}</strong>
            <p>
              {operation.kind} · {operation.status}
              {operation.aiRunId ? <> · <code>{operation.aiRunId}</code></> : null}
            </p>
            {operation.target ? <small>{operation.target}</small> : null}
            {operation.error ? <small className="ai-run-step-error">{operation.error}</small> : null}
          </div>
        </article>
      ))}
    </div>
  );
}

function AiRunDetailPanel({ detail }: { detail?: TraceDetail }) {
  const [tab, setTab] = useState<DetailTab>('readable');
  if (!detail) {
    return <section className="card ai-run-panel ai-run-detail-panel">Нет выбранного элемента.</section>;
  }

  return (
    <aside className="card ai-run-panel ai-run-detail-panel" data-testid="ai-run-detail-panel">
      <div className="ai-run-panel-head">
        <div>
          <span className="rub">Детали</span>
          <h2>{detail.title}</h2>
          <p>{detail.kicker}</p>
        </div>
        <button className="btn btn-sec btn-sm" type="button" onClick={() => void copyPayload(detail, tab)}>
          Копировать
        </button>
      </div>
      <div className="tabs ai-run-detail-tabs" role="tablist" aria-label="Detail tabs">
        <TraceTab active={tab === 'readable'} onClick={() => setTab('readable')}>Readable</TraceTab>
        <TraceTab active={tab === 'json'} onClick={() => setTab('json')}>JSON</TraceTab>
        <TraceTab active={tab === 'raw'} onClick={() => setTab('raw')}>Raw</TraceTab>
      </div>
      {tab === 'readable' ? (
        <AiRunReadableDetail detail={detail} />
      ) : (
        <pre className="ai-run-json-block" data-testid="ai-run-json">
          {prettyTraceValue(tab === 'json' ? detail.jsonPayload : detail.rawPayload)}
        </pre>
      )}
    </aside>
  );
}

function AiRunReadableDetail({ detail }: { detail: TraceDetail }) {
  return (
    <div className="ai-run-readable-detail">
      <TraceFields fields={detail.summary} />
      {detail.messages.length > 0 ? <AiRunMessages messages={detail.messages} /> : null}
      <AiRunSemanticGrid sections={detail.sections} compact />
    </div>
  );
}

function AiRunMessages({ messages }: { messages: TraceMessage[] }) {
  const [selectedMessageId, setSelectedMessageId] = useState(messages[0]?.id ?? '');
  const selected = messages.find((message) => message.id === selectedMessageId) ?? messages[0];

  return (
    <section className="ai-run-message-detail" data-testid="ai-run-message-list">
      <div className="ai-run-message-rows">
        {messages.map((message) => (
          <button
            className={message.id === selected?.id ? 'active' : ''}
            type="button"
            key={message.id}
            onClick={() => setSelectedMessageId(message.id)}
          >
            <span className="ai-run-message-index">{message.index}</span>
            <span className={`ai-run-role ${message.role}`}>{message.role}</span>
            <span className="ai-run-message-preview">{message.preview}</span>
          </button>
        ))}
      </div>
      {selected ? (
        <article className="ai-run-selected-message">
          <div className="ai-run-selected-meta">
            <span>{selected.index}</span>
            <span className={`ai-run-role ${selected.role}`}>{selected.role}</span>
          </div>
          <pre>{selected.content}</pre>
        </article>
      ) : null}
    </section>
  );
}

function AiRunSemanticSections({ sections }: { sections: TraceSemanticSection[] }) {
  return (
    <section className="card ai-run-panel">
      <span className="rub">Смысловой результат</span>
      <AiRunSemanticGrid sections={sections} />
    </section>
  );
}

function AiRunSemanticGrid({ sections, compact = false }: { sections: TraceSemanticSection[]; compact?: boolean }) {
  return (
    <div className={compact ? 'ai-run-semantic-grid compact' : 'ai-run-semantic-grid'} data-testid="ai-run-semantic-grid">
      {sections.map((section) => (
        <article className="ai-run-semantic-card" key={section.id}>
          <h2>{section.title}</h2>
          <TraceFields fields={section.fields} />
          {section.kind === 'scorecard' && section.scorecard ? (
            <AiRunScorecardTable scorecard={section.scorecard} />
          ) : null}
          {section.body ? <p className="ai-run-body-text">{section.body}</p> : null}
        </article>
      ))}
    </div>
  );
}

function AiRunScorecardTable({ scorecard }: { scorecard: TraceScorecardModel }) {
  return (
    <div className="ai-run-scorecard" data-testid="ai-run-scorecard">
      <div className="ai-run-scorecard-head">
        <span>{scorecard.rows.length} candidates</span>
        <span>Winner spread {scorecard.scoreSpread || 'n/a'}</span>
      </div>
      <div className="ai-run-scorecard-list" aria-label="Draft candidate scorecard">
        {scorecard.rows.map((row) => (
          <article className={`ai-run-scorecard-card${row.selected ? ' selected' : ''}`} key={row.candidateId}>
            <div className="ai-run-scorecard-candidate">
              <strong>{row.title}</strong>
              <code>{row.candidateId}</code>
              {row.selected ? <em>selected</em> : null}
              {row.selectionReasons ? <small>{row.selectionReasons}</small> : null}
            </div>
            <div className="ai-run-scorecard-metrics">
              <ScoreMetric label="Status" value={row.selectionStatus || 'legacy'} />
              <ScoreMetric label="Penalty" value={row.selectionPenalty} />
              <ScoreMetric label="Total" value={row.total} strong />
              <ScoreMetric label="Hard" value={row.hardConstraintFit} />
              <ScoreMetric label="Evidence" value={row.evidenceGrounding} />
              <ScoreMetric label="Topic" value={row.topicFit} />
              <ScoreMetric label="Fabula" value={row.fabulaFit} />
              <ScoreMetric label="Value" value={row.audienceValue} />
              <ScoreMetric label="Risk" value={row.riskPenalty} />
            </div>
          </article>
        ))}
      </div>
    </div>
  );
}

function ScoreMetric({ label, value, strong = false }: { label: string; value: string; strong?: boolean }) {
  return (
    <span className={strong ? 'primary' : ''}>
      <small>{label}</small>
      <b>{value || 'n/a'}</b>
    </span>
  );
}

function TraceFields({ fields }: { fields: Array<{ label: string; value: string }> }) {
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

function TraceTab({
  active,
  children,
  onClick
}: {
  active: boolean;
  children: string;
  onClick: () => void;
}) {
  return (
    <button className={`tab${active ? ' active' : ''}`} type="button" role="tab" aria-selected={active} onClick={onClick}>
      {children}
    </button>
  );
}

async function copyPayload(detail: TraceDetail, tab: DetailTab) {
  if (!navigator.clipboard) return;
  const payload = tab === 'readable' ? detail.jsonPayload : tab === 'json' ? detail.jsonPayload : detail.rawPayload;
  await navigator.clipboard.writeText(prettyTraceValue(payload));
}
