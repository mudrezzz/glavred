import type { Fabula } from '../../domain/editorialWorkspace';
import {
  FABULA_RESEARCH_DEPTH_LABELS,
  fabulaResearchDepthLabel,
  type FabulaResearchDepth
} from '../../domain/editorial-model/researchDepth';

export function FabulaResearchDepthSelect({
  fabula,
  onChange
}: {
  fabula: Fabula;
  onChange: (fabula: Fabula) => void;
}) {
  return (
    <label>
      Глубина исследования
      <select
        value={fabula.researchDepth}
        onChange={(event) => onChange({ ...fabula, researchDepth: event.target.value as FabulaResearchDepth })}
      >
        {Object.entries(FABULA_RESEARCH_DEPTH_LABELS).map(([value, label]) => (
          <option key={value} value={value}>
            {label}
          </option>
        ))}
      </select>
    </label>
  );
}

export { fabulaResearchDepthLabel };
