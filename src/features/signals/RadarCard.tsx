import type { RadarDefinition } from '../../domain/editorialWorkspace';
import {
  formatDate,
  radarAcceptancePolicyLabel,
  radarFilterDimensionLabel,
  radarFilterModeLabel,
  radarRuleOperatorLabel,
  radarSearchSourceTypeLabel,
  radarSourceDiscoveryModeLabel,
  radarSourceTypeLabel,
  radarStatusLabel,
  radarTriggerModeLabel
} from './helpers';
import { RadarEditor } from './RadarEditor';
import type { SignalsController } from './useSignalsController';

export function RadarCard({
  radar,
  controller,
  signalCount,
  onDeleteRadar,
  onToggleRadarStatus
}: {
  radar: RadarDefinition;
  controller: SignalsController;
  signalCount: number;
  onDeleteRadar: (radar: RadarDefinition) => void;
  onToggleRadarStatus: (radar: RadarDefinition) => void;
}) {
  const expanded = controller.expandedRadarId === radar.id;
  const editingThisRadar = controller.editingRadar?.id === radar.id && !controller.isNewRadar;

  return (
    <article className={`entity-row radar-card ${expanded || editingThisRadar ? 'expanded' : ''} ${editingThisRadar ? 'editing' : ''}`} data-testid="radar-row">
      <button
        className="radar-row-main"
        type="button"
        onClick={() => {
          if (editingThisRadar) return;
          controller.setExpandedRadarId(expanded ? '' : radar.id);
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
      )}
    </article>
  );
}

function RadarRulesSection({ radar }: { radar: RadarDefinition }) {
  return (
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
  );
}

function RadarSourcesSection({ radar }: { radar: RadarDefinition }) {
  return (
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
  );
}

function RadarFiltersSection({ radar }: { radar: RadarDefinition }) {
  const filters = (radar.filters ?? []).filter((filter) => filter.enabled);
  return (
    <div className="radar-config-section">
      <h4>Фильтры отбора</h4>
      {filters.length > 0 ? (
        <div className="radar-object-list">
          {filters.map((filter) => (
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
  );
}
