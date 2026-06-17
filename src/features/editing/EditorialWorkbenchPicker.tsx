import type { EditorialWorkItem } from '../../domain/editorialWorkspace';

export function EditorialWorkbenchPicker({
  items,
  selectedId,
  onSelect
}: {
  items: EditorialWorkItem[];
  selectedId: string | null;
  onSelect: (itemId: string) => void;
}) {
  return (
    <section className="card editorial-workbench-picker" data-testid="editorial-workbench-picker">
      <label>
        <span className="rub">Выбор поста</span>
        <select
          aria-label="Выбор поста"
          value={selectedId ?? ''}
          onChange={(event) => {
            if (event.target.value) onSelect(event.target.value);
          }}
        >
          <option value="" disabled>
            Выберите пост
          </option>
          {items.map((item) => (
            <option key={item.id} value={item.id}>
              {item.title} · {item.date} · {item.platform}
            </option>
          ))}
        </select>
      </label>
    </section>
  );
}
