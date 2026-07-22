import { useState } from 'react';
import type { RadarDefinition } from '../../domain/editorialWorkspace';
import {
  formatDate,
  radarAcceptancePolicyLabel,
  radarSourceTypeLabel,
  radarStatusLabel,
  radarTriggerModeLabel
} from './helpers';
import { RadarEditor } from './RadarEditor';
import { RadarFiltersSection, RadarRulesSection, RadarSourcesSection } from './RadarConfigSections';
import { RadarRunTraceSection } from './RadarRunTraceSection';
import type { SignalsController } from './useSignalsController';

type RadarDetailTab = 'settings' | 'trace';

export function RadarCard({
  radar,
  controller,
  signalCount,
  onDeleteRadar,
  onRunRadar,
  onToggleRadarStatus
}: {
  radar: RadarDefinition;
  controller: SignalsController;
  signalCount: number;
  onDeleteRadar: (radar: RadarDefinition) => void;
  onRunRadar: (radar: RadarDefinition) => void;
  onToggleRadarStatus: (radar: RadarDefinition) => void;
}) {
  const expanded = controller.expandedRadarId === radar.id;
  const editingThisRadar = controller.editingRadar?.id === radar.id && !controller.isNewRadar;
  const [detailTab, setDetailTab] = useState<RadarDetailTab>('settings');
  const latestRun = controller.latestRunsByRadar[radar.id];
  const runSummary = controller.radarRunSummaries[radar.id];
  const sourceHandles = controller.sourceHandlesByRadar[radar.id] ?? [];
  const foundMaterials = latestRun ? controller.foundMaterialsByRun[latestRun.id] ?? [] : [];

  return (
    <article className={`entity-row radar-card ${expanded || editingThisRadar ? 'expanded' : ''} ${editingThisRadar ? 'editing' : ''}`} data-testid="radar-row">
      <button
        className="radar-row-main"
        type="button"
        onClick={() => {
          if (editingThisRadar) return;
          if (!expanded) setDetailTab('settings');
          controller.setExpandedRadarId(expanded ? '' : radar.id);
        }}
      >
        <span className="radar-row-heading">
          <span className="sig radar-type">{radarSourceTypeLabel(radar.sourceType)}</span>
          <span className="radar-row-body">
            <strong className="radar-title">{radar.title}</strong>
            <span className="radar-row-sub">{radar.scope}</span>
          </span>
          <span className={`pill radar-status ${radar.status === 'active' ? 'ok' : 'pin'}`}>
            <i />
            <span>{radarStatusLabel(radar.status)}</span>
          </span>
        </span>
        <span className="radar-row-meta">
          <span><b>{signalCount}</b> сигналов</span>
          <span title={`Найдено: ${runSummary?.found ?? 0}; пропущено: ${runSummary?.skipped ?? 0}`}>
            <b>{runSummary?.found ?? 0}</b> материалов · {runSummary?.skipped ?? 0} пропущено
          </span>
          <span className="radar-date">Последний запуск: {radar.lastRunAt ? formatDate(radar.lastRunAt) : 'не запускался'}</span>
        </span>
      </button>

      {editingThisRadar && controller.editingRadar && (
        <RadarEditor
          radar={controller.editingRadar}
          isNew={false}
          embedded
          onPatch={controller.patchRadarDraft}
          onPatchRule={controller.patchRadarRule}
          onAddRule={controller.addRadarRule}
          onDeleteRule={controller.deleteRadarRule}
          onPatchSource={controller.patchRadarSource}
          onAddSource={controller.addRadarSource}
          onDeleteSource={controller.deleteRadarSource}
          onPatchFilter={controller.patchRadarFilter}
          onSave={controller.saveRadarDraft}
          onCancel={controller.cancelRadarDraft}
        />
      )}

      {expanded && !editingThisRadar && (
        <div className="radar-details">
          <div className="tabs compact-tabs radar-detail-tabs" role="tablist" aria-label="Разделы радара">
            <button className={`tab ${detailTab === 'settings' ? 'active' : ''}`} type="button" role="tab" aria-selected={detailTab === 'settings'} onClick={() => setDetailTab('settings')}>
              Настройка
            </button>
            <button className={`tab ${detailTab === 'trace' ? 'active' : ''}`} type="button" role="tab" aria-selected={detailTab === 'trace'} onClick={() => setDetailTab('trace')}>
              Трасса запуска
            </button>
          </div>
          {detailTab === 'settings' ? (
            <div className="radar-tab-panel" data-testid="radar-settings-panel">
              <p>{radar.scope}</p>
              <RadarRulesSection radar={radar} />
              <RadarSourcesSection radar={radar} />
              <RadarFiltersSection radar={radar} />
              <dl className="meta-list">
                <dt>Политика утверждения</dt>
                <dd>{radarAcceptancePolicyLabel(radar.acceptancePolicy)}</dd>
                <dt>Запуск</dt>
                <dd>{radarTriggerModeLabel(radar.triggerMode)}</dd>
              </dl>
              <div className="row-actions radar-actions entity-actions-footer">
                <button className="btn btn-sec btn-sm" type="button" onClick={() => controller.startRadarEdit(radar)}>
                  Редактировать
                </button>
                <button
                  className="btn btn-sec btn-sm"
                  type="button"
                  onClick={() => {
                    setDetailTab('trace');
                    onRunRadar(radar);
                  }}
                >
                  Запустить радар
                </button>
                <button className="btn btn-sec btn-sm" type="button" onClick={() => onToggleRadarStatus(radar)}>
                  {radar.status === 'paused' ? 'Запустить' : 'Остановить'}
                </button>
                <button
                  className="btn btn-ghost btn-sm"
                  type="button"
                  onClick={() => {
                    controller.setRadarFilter(radar.id);
                    controller.setTab('signals');
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
          ) : (
            <RadarRunTraceSection latestRun={latestRun} sourceHandles={sourceHandles} foundMaterials={foundMaterials} />
          )}
        </div>
      )}
    </article>
  );
}
