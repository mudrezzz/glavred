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

export function RadarEditor({
  radar,
  isNew,
  onPatch,
  onPatchRule,
  onAddRule,
  onDeleteRule,
  onPatchSource,
  onAddSource,
  onDeleteSource,
  onPatchFilter,
  onSave,
  onCancel,
  embedded = false
}: {
  radar: RadarDefinition;
  isNew: boolean;
  embedded?: boolean;
  onPatch: (patch: Partial<RadarDefinition>) => void;
  onPatchRule: (ruleId: string, patch: Partial<RadarSearchRule>) => void;
  onAddRule: () => void;
  onDeleteRule: (ruleId: string) => void;
  onPatchSource: (sourceId: string, patch: Partial<RadarSearchSource>) => void;
  onAddSource: () => void;
  onDeleteSource: (sourceId: string) => void;
  onPatchFilter: (filterId: string, patch: Partial<RadarEditorialFilterRule>) => void;
  onSave: () => void;
  onCancel: () => void;
}) {
  const sourceConfigInvalid = !isRadarSourceConfigurationValid(radar);

  return (
    <section className={`${embedded ? 'radar-editor radar-editor-inline' : 'card radar-editor'}`}>
      <div className="doc-head">
        <div>
          <span className="rub">{isNew ? 'Новый радар' : 'Редактирование радара'}</span>
          <h3>{radar.title || 'Радар без названия'}</h3>
        </div>
        <span className="pill pin">local-first</span>
      </div>
      <div className="signal-edit-form">
        <label>
          <span>Название</span>
          <input value={radar.title} onChange={(event) => onPatch({ title: event.target.value })} />
        </label>
        <label>
          <span>Описание поиска</span>
          <textarea value={radar.scope} onChange={(event) => onPatch({ scope: event.target.value })} />
        </label>
        <div className="form-grid-3">
          <label>
            <span>Утверждение</span>
            <select
              value={radar.acceptancePolicy}
              onChange={(event) => onPatch({ acceptancePolicy: event.target.value as RadarDefinition['acceptancePolicy'] })}
            >
              <option value="manual">Вручную</option>
              <option value="automatic">Автоматически</option>
              <option value="automaticWithReview">Авто + review</option>
            </select>
          </label>
          <label>
            <span>Запуск</span>
            <select
              value={radar.triggerMode}
              onChange={(event) => onPatch({ triggerMode: event.target.value as RadarDefinition['triggerMode'] })}
            >
              <option value="manual">Вручную</option>
              <option value="scheduled">По расписанию</option>
              <option value="deficitDriven">По дефициту плана</option>
            </select>
          </label>
          <label>
            <span>Статус</span>
            <select value={radar.status} onChange={(event) => onPatch({ status: event.target.value as RadarDefinition['status'] })}>
              <option value="active">Активен</option>
              <option value="paused">Пауза</option>
              <option value="needsReview">Нужен review</option>
            </select>
          </label>
        </div>
      </div>

      <div className="radar-config-section">
        <div className="list-toolbar compact">
          <h4>Правила срабатывания</h4>
          <button className="btn btn-sec btn-sm" type="button" onClick={onAddRule}>
            + Правило
          </button>
        </div>
        {radar.rules.map((rule) => (
          <div className="radar-rule-edit" key={rule.id}>
            <select value={rule.operator} onChange={(event) => onPatchRule(rule.id, { operator: event.target.value as RadarSearchRule['operator'] })}>
              <option value="and">И</option>
              <option value="or">ИЛИ</option>
            </select>
            <label className="check-row">
              <input type="checkbox" checked={rule.negate} onChange={(event) => onPatchRule(rule.id, { negate: event.target.checked })} />
              NOT
            </label>
            <textarea
              placeholder="Одна инструкция поиска"
              value={rule.statement}
              onChange={(event) => onPatchRule(rule.id, { statement: event.target.value })}
            />
            <button className="btn btn-ghost btn-sm" type="button" onClick={() => onDeleteRule(rule.id)}>
              Удалить
            </button>
          </div>
        ))}
      </div>

      <div className="radar-config-section">
        <div className="list-toolbar compact">
          <h4>Источники поиска</h4>
          <button className="btn btn-sec btn-sm" type="button" onClick={onAddSource}>
            + Источник
          </button>
        </div>
        <div className="radar-source-mode" data-testid="radar-source-discovery-mode">
          {(['specifiedOnly', 'specifiedAndAdditional', 'autonomous'] as RadarSourceDiscoveryMode[]).map((mode) => (
            <label className={`source-mode-option ${radar.sourceDiscoveryMode === mode ? 'active' : ''}`} key={mode}>
              <input
                type="radio"
                checked={(radar.sourceDiscoveryMode ?? 'autonomous') === mode}
                onChange={() => onPatch({ sourceDiscoveryMode: mode })}
              />
              <span>{radarSourceDiscoveryModeLabel(mode)}</span>
            </label>
          ))}
        </div>
        {sourceConfigInvalid && (
          <p className="validation-warning" role="alert">
            Для режима "Только указанные" нужен хотя бы один источник или другой режим поиска.
          </p>
        )}
        {radar.sources.map((source) => (
          <div className="radar-source-edit" key={source.id}>
            <select value={source.type} onChange={(event) => onPatchSource(source.id, { type: event.target.value as RadarSearchSource['type'] })}>
              <option value="authorArchive">Архив автора</option>
              <option value="externalUrl">URL</option>
              <option value="mcpServer">MCP</option>
              <option value="api">API</option>
              <option value="searchKeywords">Ключевые слова</option>
              <option value="manualSource">Ручной источник</option>
              <option value="socialProfile">Соцпрофиль</option>
              <option value="document">Документ</option>
              <option value="openWeb">Открытый web</option>
            </select>
            <input placeholder="Название" value={source.title} onChange={(event) => onPatchSource(source.id, { title: event.target.value })} />
            <textarea placeholder="URL/API/MCP/ключевые слова" value={source.value} onChange={(event) => onPatchSource(source.id, { value: event.target.value })} />
            <button className="btn btn-ghost btn-sm" type="button" onClick={() => onDeleteSource(source.id)}>
              Удалить
            </button>
          </div>
        ))}
        {radar.sources.length === 0 && <p className="muted">Источники можно не задавать: тогда правила описывают, что искать, а поверхность поиска будет выбрана позднее.</p>}
      </div>

      <div className="radar-config-section" data-testid="radar-filter-section">
        <div className="list-toolbar compact">
          <h4>Фильтры отбора</h4>
          <p className="muted">Проверяют найденный сигнал против издательства, автора, аудитории, позиции, целей, запретов и тем.</p>
        </div>
        {(radar.filters ?? []).map((filter) => (
          <div className={`radar-filter-edit ${filter.enabled ? 'active' : ''}`} key={filter.id}>
            <label className="check-row radar-filter-toggle">
              <input
                type="checkbox"
                checked={filter.enabled}
                onChange={(event) => onPatchFilter(filter.id, { enabled: event.target.checked })}
              />
              {radarFilterDimensionLabel(filter.dimension)}
            </label>
            <div className="radar-filter-controls">
              <select
                value={filter.mode}
                onChange={(event) => onPatchFilter(filter.id, { mode: event.target.value as RadarEditorialFilterMode })}
                disabled={!filter.enabled}
              >
                <option value="mustMatch">Должно совпадать</option>
                <option value="shouldMatch">Желательно совпадение</option>
                <option value="mustNotMatch">Не должно совпадать</option>
                <option value="seekTension">Искать напряжение</option>
              </select>
              <textarea
                placeholder="Дополнительное правило фильтра"
                value={filter.instruction}
                onChange={(event) => onPatchFilter(filter.id, { instruction: event.target.value })}
                disabled={!filter.enabled}
              />
            </div>
          </div>
        ))}
      </div>

      <div className="row-actions">
        <button className="btn btn-pri btn-sm" type="button" disabled={!radar.title.trim() || sourceConfigInvalid} onClick={onSave}>
          Сохранить
        </button>
        <button className="btn btn-sec btn-sm" type="button" onClick={onCancel}>
          Отменить
        </button>
      </div>
    </section>
  );
}
