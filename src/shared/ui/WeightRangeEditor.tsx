import { normalizeWeightRange, type WeightRange } from '../../domain/editorialWorkspace';

export function WeightRangeEditor({ value, onChange }: { value: WeightRange; onChange: (value: WeightRange) => void }) {
  return (
    <div className="weight-editor">
      <label>
        Минимум, %
        <input
          min={0}
          max={100}
          type="number"
          value={value.min}
          onChange={(event) => onChange(normalizeWeightRange({ ...value, min: Number(event.target.value) }))}
        />
      </label>
      <label>
        Максимум, %
        <input
          min={0}
          max={100}
          type="number"
          value={value.max}
          onChange={(event) => onChange(normalizeWeightRange({ ...value, max: Number(event.target.value) }))}
        />
      </label>
    </div>
  );
}
