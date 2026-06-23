import type { Fabula } from '../../domain/editorialWorkspace';
import type { FabulaSizeIntent } from '../../domain/planning/publicationSize';

const SIZE_INTENT_LABELS: Record<FabulaSizeIntent, string> = {
  compact: 'Компактный',
  standard: 'Стандартный',
  deep: 'Глубокий'
};

export function FabulaSizeIntentSelect({
  fabula,
  onChange
}: {
  fabula: Fabula;
  onChange: (fabula: Fabula) => void;
}) {
  return (
    <label>
      Масштаб
      <select
        value={fabula.sizeIntent}
        onChange={(event) => onChange({ ...fabula, sizeIntent: event.target.value as FabulaSizeIntent })}
      >
        {Object.entries(SIZE_INTENT_LABELS).map(([value, label]) => (
          <option key={value} value={value}>
            {label}
          </option>
        ))}
      </select>
    </label>
  );
}

export function fabulaSizeIntentLabel(value: FabulaSizeIntent): string {
  return SIZE_INTENT_LABELS[value] ?? SIZE_INTENT_LABELS.standard;
}
