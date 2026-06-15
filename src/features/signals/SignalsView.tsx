import { useMemo, useState } from 'react';
import {
  createRadarDraft,
  isRadarSourceConfigurationValid,
  type ImportRiskLevel,
  type RadarDefinition,
  type RadarEditorialFilterMode,
  type RadarEditorialFilterRule,
  type RadarSearchRule,
  type RadarSearchSource,
  type RadarSourceDiscoveryMode,
  type SignalFilterStatus,
  type SignalReviewStatus,
  type SourceSignal,
  type WorkspaceState
} from '../../domain/editorialWorkspace';
import { Icon } from '../../shared/ui/Icon';
import {
  EmptyState,
  SummaryItem,
  duplicateRiskLabel,
  formatDate,
  radarAcceptancePolicyLabel,
  radarFilterDimensionLabel,
  radarFilterModeLabel,
  radarRuleOperatorLabel,
  radarSearchSourceTypeLabel,
  radarSourceDiscoveryModeLabel,
  radarSourceTypeLabel,
  radarStatusLabel,
  radarTriggerModeLabel,
  signalFilterEvaluationLabel,
  signalFilterStatusLabel,
  signalReviewStatusLabel,
  type SignalsTab
} from './helpers';
import { RadarEditor } from './RadarEditor';
import { SignalsSidePanel } from './SignalsSidePanel';

export function SignalsView({
  workspace,
  onSaveRadar,
  onDeleteRadar,
  onToggleRadarStatus,
  onApproveSignal,
  onRejectSignal,
  onArchiveSignal,
  onCorrectSignal,
  onCreateInsight,
  onPlan
}: {
  workspace: WorkspaceState;
  onSaveRadar: (radar: RadarDefinition, isNew: boolean) => void;
  onDeleteRadar: (radar: RadarDefinition) => void;
  onToggleRadarStatus: (radar: RadarDefinition) => void;
  onApproveSignal: (signal: SourceSignal) => void;
  onRejectSignal: (signal: SourceSignal) => void;
  onArchiveSignal: (signal: SourceSignal) => void;
  onCorrectSignal: (signal: SourceSignal, patch: Partial<SourceSignal>) => void;
  onCreateInsight: () => void;
  onPlan: () => void;
}) {
  const [tab, setTab] = useState<'radars' | 'signals' | 'candidates'>('radars');
  const [expandedRadarId, setExpandedRadarId] = useState(workspace.radars[0]?.id ?? '');
  const [expandedSignalId, setExpandedSignalId] = useState(workspace.sourceSignals[0]?.id ?? '');
  const [editingRadar, setEditingRadar] = useState<RadarDefinition | null>(null);
  const [isNewRadar, setIsNewRadar] = useState(false);
  const [editingSignal, setEditingSignal] = useState<SourceSignal | null>(null);
  const [radarFilter, setRadarFilter] = useState('all');
  const [statusFilter, setStatusFilter] = useState<'all' | SignalReviewStatus>('all');
  const [filterStatusFilter, setFilterStatusFilter] = useState<'all' | SignalFilterStatus>('all');
  const [riskFilter, setRiskFilter] = useState<'all' | ImportRiskLevel>('all');
  const [query, setQuery] = useState('');

  const signalCountsByRadar = useMemo(() => {
    return workspace.sourceSignals.reduce<Record<string, number>>((counts, signal) => {
      if (!signal.radarId) return counts;
      return { ...counts, [signal.radarId]: (counts[signal.radarId] ?? 0) + 1 };
    }, {});
  }, [workspace.sourceSignals]);

  const filteredSignals = workspace.sourceSignals.filter((signal) => {
    const haystack = [
      signal.title,
      signal.summary,
      signal.rawNote,
      signal.source,
      signal.searchNote ?? '',
      ...(signal.evidence ?? []).flatMap((item) => [item.sourceTitle, item.quote, item.summary])
    ]
      .join(' ')
      .toLowerCase();

    if (radarFilter !== 'all' && signal.radarId !== radarFilter) return false;
    if (statusFilter !== 'all' && signal.reviewStatus !== statusFilter) return false;
    if (filterStatusFilter !== 'all' && signal.filterStatus !== filterStatusFilter) return false;
    if (riskFilter !== 'all' && signal.duplicateRisk !== riskFilter) return false;
    if (query.trim() && !haystack.includes(query.trim().toLowerCase())) return false;
    return true;
  });

  const signalSummary = {
    total: workspace.sourceSignals.length,
    new: workspace.sourceSignals.filter((signal) => !signal.reviewStatus || signal.reviewStatus === 'new').length,
    approved: workspace.sourceSignals.filter((signal) => signal.reviewStatus === 'approved').length,
    archived: workspace.sourceSignals.filter((signal) => signal.reviewStatus === 'archived').length,
    highRisk: workspace.sourceSignals.filter((signal) => signal.duplicateRisk === 'high').length
  };

  function openNewRadar() {
    if (editingRadar && isNewRadar) return;
    setEditingRadar(createRadarDraft());
    setIsNewRadar(true);
    setExpandedRadarId('');
  }

  function startRadarEdit(radar: RadarDefinition) {
    setEditingRadar(structuredClone(radar));
    setIsNewRadar(false);
    setExpandedRadarId(radar.id);
  }

  function saveRadarDraft() {
    if (!editingRadar || !editingRadar.title.trim()) return;
    if (!isRadarSourceConfigurationValid(editingRadar)) return;
    onSaveRadar(editingRadar, isNewRadar);
    setExpandedRadarId(editingRadar.id);
    setEditingRadar(null);
    setIsNewRadar(false);
  }

  function patchRadarDraft(patch: Partial<RadarDefinition>) {
    setEditingRadar((current) => (current ? { ...current, ...patch } : current));
  }

  function patchRadarRule(ruleId: string, patch: Partial<RadarSearchRule>) {
    setEditingRadar((current) =>
      current
        ? {
            ...current,
            rules: current.rules.map((rule) => (rule.id === ruleId ? { ...rule, ...patch } : rule))
          }
        : current
    );
  }

  function patchRadarFilter(filterId: string, patch: Partial<RadarEditorialFilterRule>) {
    setEditingRadar((current) =>
      current
        ? {
            ...current,
            filters: (current.filters ?? []).map((filter) => (filter.id === filterId ? { ...filter, ...patch } : filter))
          }
        : current
    );
  }

  function addRadarRule() {
    setEditingRadar((current) =>
      current
        ? {
            ...current,
            rules: [
              ...current.rules,
              {
                id: `radar-rule-${Date.now()}`,
                operator: 'and',
                negate: false,
                statement: '',
                status: 'active'
              }
            ]
          }
        : current
    );
  }

  function deleteRadarRule(ruleId: string) {
    setEditingRadar((current) =>
      current ? { ...current, rules: current.rules.filter((rule) => rule.id !== ruleId) } : current
    );
  }

  function patchRadarSource(sourceId: string, patch: Partial<RadarSearchSource>) {
    setEditingRadar((current) =>
      current
        ? {
            ...current,
            sources: current.sources.map((source) => (source.id === sourceId ? { ...source, ...patch } : source))
          }
        : current
    );
  }

  function addRadarSource() {
    setEditingRadar((current) =>
      current
        ? {
            ...current,
            sources: [
              ...current.sources,
              {
                id: `radar-source-${Date.now()}`,
                type: 'openWeb',
                title: '',
                value: '',
                notes: '',
                status: 'active'
              }
            ]
          }
        : current
    );
  }

  function deleteRadarSource(sourceId: string) {
    setEditingRadar((current) =>
      current ? { ...current, sources: current.sources.filter((source) => source.id !== sourceId) } : current
    );
  }

  function startSignalEdit(signal: SourceSignal) {
    setEditingSignal({ ...signal });
    setExpandedSignalId(signal.id);
  }

  function patchSignalDraft(patch: Partial<SourceSignal>) {
    setEditingSignal((current) => (current ? { ...current, ...patch } : current));
  }

  function saveSignalDraft() {
    if (!editingSignal) return;
    onCorrectSignal(editingSignal, {
      title: editingSignal.title,
      summary: editingSignal.summary,
      rawNote: editingSignal.rawNote,
      searchNote: editingSignal.searchNote,
      authorCorrection: editingSignal.authorCorrection
    });
    setEditingSignal(null);
  }

  return (
    <div className="page wide signals-page fade-up">
      <section className="card project-profile-header signals-section-header" data-testid="signals-section-header">
        <div className="project-profile-main">
          <span className="mono-label">Материал</span>
          <h2>Сигналы</h2>
          <p>Радары собирают сырой материал для постов. Автор утверждает, архивирует или правит сигнал до того, как он станет кандидатом поста.</p>
        </div>
        <div className="project-profile-meta signals-header-stats">
          <div>
            <b>{workspace.radars.length}</b>
            <span>радаров</span>
          </div>
          <div>
            <b>{signalSummary.new}</b>
            <span>новых</span>
          </div>
          <div>
            <b>{signalSummary.approved}</b>
            <span>утверждено</span>
          </div>
        </div>
      </section>

      <div className="tabs signal-tabs" role="tablist" aria-label="Сигналы">
        <button className={`tab ${tab === 'radars' ? 'active' : ''}`} type="button" onClick={() => setTab('radars')}>
          Радары
        </button>
        <button className={`tab ${tab === 'signals' ? 'active' : ''}`} type="button" onClick={() => setTab('signals')}>
          Найденные сигналы
          <span className="tab-count">{signalSummary.new}</span>
        </button>
        <button className={`tab ${tab === 'candidates' ? 'active' : ''}`} type="button" onClick={() => setTab('candidates')}>
          Кандидаты постов
        </button>
      </div>

      {tab === 'radars' && (
        <div className="memory-grid signals-workspace-grid">
          <section className="memory-main">
            <div className="entity-list-toolbar signals-entity-toolbar" data-testid="signals-radar-toolbar">
              <div className="entity-toolbar-copy">
                <h2>{workspace.radars.length} радара</h2>
                <p>Настраиваемые поисковики</p>
              </div>
              <button className="btn btn-sec btn-sm" data-testid="add-radar-button" type="button" onClick={openNewRadar}>
                + Радар
              </button>
            </div>

            {editingRadar && isNewRadar && (
              <RadarEditor
                radar={editingRadar}
                isNew={isNewRadar}
                onPatch={patchRadarDraft}
                onPatchRule={patchRadarRule}
                onAddRule={addRadarRule}
                onDeleteRule={deleteRadarRule}
                onPatchSource={patchRadarSource}
                onAddSource={addRadarSource}
                onDeleteSource={deleteRadarSource}
                onPatchFilter={patchRadarFilter}
                onSave={saveRadarDraft}
                onCancel={() => {
                  setEditingRadar(null);
                  setIsNewRadar(false);
                }}
              />
            )}

            <div className="entity-list signals-entity-list" data-testid="radar-list">
              {workspace.radars.map((radar) => {
                const expanded = expandedRadarId === radar.id;
                const editingThisRadar = editingRadar?.id === radar.id && !isNewRadar;
                const signalCount = signalCountsByRadar[radar.id] ?? 0;

                return (
                  <article className={`entity-row radar-card ${expanded || editingThisRadar ? 'expanded' : ''} ${editingThisRadar ? 'editing' : ''}`} data-testid="radar-row" key={radar.id}>
                    <button
                      className="radar-row-main"
                      type="button"
                      onClick={() => {
                        if (editingThisRadar) return;
                        setExpandedRadarId(expanded ? '' : radar.id);
                      }}
                    >
                      <span className="sig radar-type">{radarSourceTypeLabel(radar.sourceType)}</span>
                      <span className="radar-row-body">
                        <strong className="radar-title">{radar.title}</strong>
                        <span className="radar-row-sub">{radar.scope}</span>
                      </span>
                      <span className="radar-row-meta">
                        <span className={`pill radar-status ${radar.status === 'active' ? 'ok' : 'pin'}`}>
                          <i />
                          <span>{radarStatusLabel(radar.status)}</span>
                        </span>
                        <span className="count-dot radar-count">{signalCount}</span>
                        <span className="radar-date">last run {radar.lastRunAt ? formatDate(radar.lastRunAt) : 'не запускался'}</span>
                      </span>
                    </button>

                    {editingThisRadar && editingRadar && (
                      <RadarEditor
                        radar={editingRadar}
                        isNew={false}
                        embedded
                        onPatch={patchRadarDraft}
                        onPatchRule={patchRadarRule}
                        onAddRule={addRadarRule}
                        onDeleteRule={deleteRadarRule}
                        onPatchSource={patchRadarSource}
                        onAddSource={addRadarSource}
                        onDeleteSource={deleteRadarSource}
                        onPatchFilter={patchRadarFilter}
                        onSave={saveRadarDraft}
                        onCancel={() => {
                          setEditingRadar(null);
                          setIsNewRadar(false);
                        }}
                      />
                    )}

                    {expanded && !editingThisRadar && (
                      <div className="radar-details">
                        <p>{radar.scope}</p>
                        <div className="radar-config-section">
                          <h4>Правила срабатывания</h4>
                          <div className="radar-object-list">
                            {radar.rules.map((rule) => (
                              <div className="radar-object" key={rule.id}>
                                <span className="sig">{rule.negate ? 'NOT' : radarRuleOperatorLabel(rule.operator)}</span>
                                <p>{rule.statement}</p>
                              </div>
                            ))}
                          </div>
                        </div>
                        <div className="radar-config-section">
                          <h4>Источники поиска</h4>
                          <p className="muted">Поверхность поиска: {radarSourceDiscoveryModeLabel(radar.sourceDiscoveryMode)}</p>
                          {radar.sources.length > 0 ? (
                            <div className="radar-object-list">
                              {radar.sources.map((source) => (
                                <div className="radar-object" key={source.id}>
                                  <span className="sig">{radarSearchSourceTypeLabel(source.type)}</span>
                                  <p>
                                    <strong>{source.title}</strong>
                                    <br />
                                    {source.value || source.notes}
                                  </p>
                                </div>
                              ))}
                            </div>
                          ) : (
                            <p className="muted">Источники не заданы: будущий AI-адаптер сможет сам выбрать поверхность поиска по правилам.</p>
                          )}
                        </div>
                        <div className="radar-config-section">
                          <h4>Фильтры отбора</h4>
                          {(radar.filters ?? []).filter((filter) => filter.enabled).length > 0 ? (
                            <div className="radar-object-list">
                              {(radar.filters ?? [])
                                .filter((filter) => filter.enabled)
                                .map((filter) => (
                                  <div className="radar-object" key={filter.id}>
                                    <span className="sig">{radarFilterDimensionLabel(filter.dimension)}</span>
                                    <p>
                                      <strong>{radarFilterModeLabel(filter.mode)}</strong>
                                      <br />
                                      {filter.instruction}
                                    </p>
                                  </div>
                                ))}
                            </div>
                          ) : (
                            <p className="muted">Фильтры не включены: радар покажет найденный материал без редакционного отсева.</p>
                          )}
                        </div>
                        <dl className="meta-list">
                          <dt>Политика утверждения</dt>
                          <dd>{radarAcceptancePolicyLabel(radar.acceptancePolicy)}</dd>
                          <dt>Запуск</dt>
                          <dd>{radarTriggerModeLabel(radar.triggerMode)}</dd>
                        </dl>
                        <div className="row-actions radar-actions entity-actions-footer">
                          <button className="btn btn-sec btn-sm" type="button" onClick={() => startRadarEdit(radar)}>
                            Редактировать
                          </button>
                          <button className="btn btn-sec btn-sm" type="button" onClick={() => onToggleRadarStatus(radar)}>
                            {radar.status === 'paused' ? 'Запустить' : 'Остановить'}
                          </button>
                          <button
                            className="btn btn-ghost btn-sm"
                            type="button"
                            onClick={() => {
                              setRadarFilter(radar.id);
                              setTab('signals');
                            }}
                          >
                            Открыть сигналы
                          </button>
                          <button
                            className="btn btn-ghost btn-sm"
                            type="button"
                            onClick={() => {
                              if (window.confirm('Удалить радар? Найденные сигналы останутся в истории разбора.')) {
                                onDeleteRadar(radar);
                              }
                            }}
                          >
                            Удалить
                          </button>
                        </div>
                      </div>
                    )}
                  </article>
                );
              })}
            </div>
          </section>

          <SignalsSidePanel workspace={workspace} summary={signalSummary} onCreateInsight={onCreateInsight} onPlan={onPlan} />
        </div>
      )}

      {tab === 'signals' && (
        <div className="memory-grid signals-workspace-grid">
          <section className="memory-main">
            <div className="signal-filter-row" data-testid="signal-filter-toolbar">
              <input
                className="search-input compact"
                placeholder="Поиск по сигналам, evidence, источникам"
                value={query}
                onChange={(event) => setQuery(event.target.value)}
              />
              <select
                aria-label="Фильтр радара сигнала"
                value={radarFilter}
                onChange={(event) => setRadarFilter(event.target.value)}
              >
                <option value="all">Все радары</option>
                {workspace.radars.map((radar) => (
                  <option key={radar.id} value={radar.id}>
                    {radar.title}
                  </option>
                ))}
              </select>
              <select
                aria-label="Фильтр статуса сигнала"
                value={statusFilter}
                onChange={(event) => setStatusFilter(event.target.value as 'all' | SignalReviewStatus)}
              >
                <option value="all">Все статусы</option>
                <option value="new">Новые</option>
                <option value="approved">Утвержденные</option>
                <option value="corrected">С правкой</option>
                <option value="archived">В архиве</option>
                <option value="rejected">Отклоненные</option>
              </select>
              <select
                aria-label="Фильтр риска дубля сигнала"
                value={riskFilter}
                onChange={(event) => setRiskFilter(event.target.value as 'all' | ImportRiskLevel)}
              >
                <option value="all">Любой дубль-риск</option>
                <option value="low">low</option>
                <option value="medium">medium</option>
                <option value="high">high</option>
              </select>
              <select
                aria-label="Фильтр фильтров отбора сигнала"
                data-testid="signal-filter-status-filter"
                value={filterStatusFilter}
                onChange={(event) => setFilterStatusFilter(event.target.value as 'all' | SignalFilterStatus)}
              >
                <option value="all">Все по фильтрам</option>
                <option value="passed">Прошли</option>
                <option value="warning">С предупреждением</option>
                <option value="rejected">Отсечены</option>
              </select>
            </div>

            <div className="entity-list signals-entity-list" data-testid="source-signal-list">
              {filteredSignals.map((signal) => {
                const radar = workspace.radars.find((item) => item.id === signal.radarId);
                const expanded = expandedSignalId === signal.id;
                const editing = editingSignal?.id === signal.id;

                return (
                  <article className={`entity-row signal-card ${expanded ? 'expanded' : ''}`} data-testid="source-signal-row" key={signal.id}>
                    <button className="signal-row-main" type="button" onClick={() => setExpandedSignalId(expanded ? '' : signal.id)}>
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
                        <span className={`sc signal-filter-status filter-status-${signal.filterStatus ?? 'passed'}`}>
                          {signalFilterStatusLabel(signal.filterStatus)}
                        </span>
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
                          <dt>Поиск дублей</dt>
                          <dd>{signal.searchNote ?? `Риск дубля: ${signal.duplicateRisk ?? 'low'}`}</dd>
                          <dt>Правка автора</dt>
                          <dd>{signal.authorCorrection || 'нет'}</dd>
                        </dl>
                        <div className="radar-config-section signal-filter-evaluations" data-testid="signal-filter-evaluations">
                          <h4>Фильтры отбора</h4>
                          {(signal.filterEvaluations ?? []).length > 0 ? (
                            <div className="signal-filter-list">
                              {(signal.filterEvaluations ?? []).map((evaluation) => (
                                <div className={`signal-filter-evaluation filter-eval-${evaluation.status}`} key={evaluation.filterId}>
                                  <span className={`sc filter-status-${evaluation.status}`}>
                                    {signalFilterEvaluationLabel(evaluation.status)}
                                  </span>
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
                        <div className="radar-config-section">
                          <h4>Evidence</h4>
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
                        <div className="row-actions signal-actions entity-actions-footer">
                          <button className="btn btn-pri btn-sm" type="button" onClick={() => onApproveSignal(signal)}>
                            Утвердить сигнал
                          </button>
                          <button className="btn btn-sec btn-sm" type="button" onClick={() => startSignalEdit(signal)}>
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

                    {expanded && editing && editingSignal && (
                      <div className="signal-edit-form">
                        <label>
                          <span>Инсайт</span>
                          <input value={editingSignal.title} onChange={(event) => patchSignalDraft({ title: event.target.value })} />
                        </label>
                        <label>
                          <span>Краткая сводка</span>
                          <textarea value={editingSignal.summary} onChange={(event) => patchSignalDraft({ summary: event.target.value })} />
                        </label>
                        <label>
                          <span>Что нашли</span>
                          <textarea value={editingSignal.rawNote} onChange={(event) => patchSignalDraft({ rawNote: event.target.value })} />
                        </label>
                        <label>
                          <span>Поиск дублей</span>
                          <textarea value={editingSignal.searchNote ?? ''} onChange={(event) => patchSignalDraft({ searchNote: event.target.value })} />
                        </label>
                        <label>
                          <span>Правка автора</span>
                          <textarea
                            value={editingSignal.authorCorrection ?? ''}
                            onChange={(event) => patchSignalDraft({ authorCorrection: event.target.value })}
                          />
                        </label>
                        <div className="row-actions signal-actions entity-actions-footer">
                          <button className="btn btn-pri btn-sm" type="button" onClick={saveSignalDraft}>
                            Сохранить
                          </button>
                          <button className="btn btn-sec btn-sm" type="button" onClick={() => setEditingSignal(null)}>
                            Отменить
                          </button>
                        </div>
                      </div>
                    )}
                  </article>
                );
              })}
              {filteredSignals.length === 0 && <EmptyState text="По выбранным фильтрам сигналов нет." />}
            </div>
          </section>

          <SignalsSidePanel workspace={workspace} summary={signalSummary} onCreateInsight={onCreateInsight} onPlan={onPlan} />
        </div>
      )}

      {tab === 'candidates' && (
        <div className="memory-grid signals-workspace-grid">
          <section className="card draft-start">
            <span className="rub">Slice 1.6</span>
            <h2>Кандидаты постов появятся после утверждения сигналов</h2>
            <p>
              Следующий слой соберет комбинации «Сигнал + Тема + Фабула + ЦА + Ценность».
              Пока сигналы остаются сырьем: их нужно принять, отклонить, архивировать или уточнить.
            </p>
            <div className="signal-summary-grid">
              <SummaryItem label="Утверждено" value={signalSummary.approved} />
              <SummaryItem label="Новые" value={signalSummary.new} />
              <SummaryItem label="Дубль high" value={signalSummary.highRisk} />
            </div>
          </section>
          <SignalsSidePanel workspace={workspace} summary={signalSummary} onCreateInsight={onCreateInsight} onPlan={onPlan} />
        </div>
      )}
    </div>
  );
}
