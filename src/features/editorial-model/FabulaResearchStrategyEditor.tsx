import type { Fabula } from '../../domain/editorialWorkspace';
import { buildBriefSourceIntentPreview } from '../../application/sourceIntentPreview';

type Props = {
  fabula: Fabula;
  onChange: (fabula: Fabula) => void;
};

export function FabulaResearchStrategyEditor({ fabula, onChange }: Props) {
  const strategy = fabula.researchStrategy;
  const instructions = strategy.instructions.join('\n');
  const preview = buildBriefSourceIntentPreview(instructions);

  function updateMode(mode: 'auto' | 'manual') {
    onChange({ ...fabula, researchStrategy: { ...strategy, mode } });
  }

  function updateInstructions(value: string) {
    onChange({
      ...fabula,
      researchStrategy: {
        ...strategy,
        mode: 'manual',
        instructions: value.split(/\r?\n/)
      }
    });
  }

  return (
    <section className="fabula-research-editor">
      <div className="field-group-header">
        <span>Исследовательская стратегия</span>
        <small>Defaults для будущих рабочих фабул</small>
      </div>
      <div className="tabs" role="tablist" aria-label="Режим исследовательской стратегии">
        <button
          className={`tab ${strategy.mode === 'auto' ? 'active' : ''}`}
          type="button"
          onClick={() => updateMode('auto')}
        >
          Автоопределение
        </button>
        <button
          className={`tab ${strategy.mode === 'manual' ? 'active' : ''}`}
          type="button"
          onClick={() => updateMode('manual')}
        >
          Задать вручную
        </button>
      </div>
      {strategy.mode === 'auto' ? (
        <p className="field-hint">
          При создании рабочей фабулы Glavred предложит источники из темы, фабулы, сигнала, кандидата и proof requirements. В редактуре их можно будет заменить.
        </p>
      ) : (
        <label>
          Поручения для источников
          <textarea
            value={instructions}
            onChange={(event) => updateInstructions(event.target.value)}
            placeholder={'найти: мнение лидеров мнений по этой теме\nпроверить: свежую статистику adoption\nне использовать: vendor blogs'}
          />
        </label>
      )}
      {preview.length > 0 ? (
        <div className="brief-source-preview" aria-label="Распознавание исследовательской стратегии">
          {preview.map((item) => (
            <div className={`brief-source-preview-row kind-${item.kind}`} key={item.id}>
              <span className="pill">{item.label}</span>
              <span>{item.value}</span>
            </div>
          ))}
        </div>
      ) : null}
    </section>
  );
}
