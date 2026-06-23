import { buildBriefSourceIntentPreview } from './briefSourceIntentPreview';

export function BriefSourceIntentEditor({
  value,
  onChange
}: {
  value: string;
  onChange: (value: string) => void;
}) {
  const preview = buildBriefSourceIntentPreview(value);

  return (
    <label className="brief-edit-wide brief-source-intent-editor">
      <span>Источники и исследовательские поручения</span>
      <textarea
        value={value}
        onChange={(event) => onChange(event.target.value)}
        placeholder={'url: https://...\nнайти: мнение лидеров мнений по этой теме\nпроверить: свежую статистику adoption\nне использовать: vendor blogs'}
      />
      <span className="field-hint">
        Можно указать URL, название источника или поручение обычным языком. Поддерживаются префиксы: url:, источник:, найти:, проверить:, не использовать:.
      </span>
      {preview.length > 0 ? (
        <div className="brief-source-preview" aria-label="Распознавание источников">
          {preview.map((item) => (
            <div className={`brief-source-preview-row kind-${item.kind}`} key={item.id}>
              <span className="pill">{item.label}</span>
              <span>{item.value}</span>
            </div>
          ))}
        </div>
      ) : null}
    </label>
  );
}
