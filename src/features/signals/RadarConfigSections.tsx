import type { RadarDefinition } from '../../domain/editorialWorkspace';
import {
  radarFilterDimensionLabel,
  radarFilterModeLabel,
  radarRuleOperatorLabel,
  radarSearchSourceTypeLabel,
  radarSourceDiscoveryModeLabel
} from './helpers';

export function RadarRulesSection({ radar }: { radar: RadarDefinition }) {
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

export function RadarSourcesSection({ radar }: { radar: RadarDefinition }) {
  return (
    <div className="radar-config-section">
      <h4>Источники поиска</h4>
      <p className="muted">Поверхность поиска: {radarSourceDiscoveryModeLabel(radar.sourceDiscoveryMode)}</p>
      {radar.sources.length > 0 ? (
        <div className="radar-object-list">
          {radar.sources.map((source) => (
            <div className="radar-object" key={source.id}>
              <span className="sig">{radarSearchSourceTypeLabel(source.type)}</span>
              <p><strong>{source.title}</strong><br />{source.value || source.notes}</p>
            </div>
          ))}
        </div>
      ) : (
        <p className="muted">Источники не заданы: поиск выберет поверхность по активным правилам.</p>
      )}
    </div>
  );
}

export function RadarFiltersSection({ radar }: { radar: RadarDefinition }) {
  const filters = (radar.filters ?? []).filter((filter) => filter.enabled);
  return (
    <div className="radar-config-section">
      <h4>Фильтры отбора</h4>
      {filters.length > 0 ? (
        <div className="radar-object-list">
          {filters.map((filter) => (
            <div className="radar-object" key={filter.id}>
              <span className="sig">{radarFilterDimensionLabel(filter.dimension)}</span>
              <p><strong>{radarFilterModeLabel(filter.mode)}</strong><br />{filter.instruction}</p>
            </div>
          ))}
        </div>
      ) : (
        <p className="muted">Фильтры не включены: найденный материал показывается без редакционной оценки.</p>
      )}
    </div>
  );
}
