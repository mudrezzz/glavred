import { useEffect, useMemo, useState } from 'react';
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
  const selected = items.find((item) => item.id === selectedId) ?? null;
  const [query, setQuery] = useState(selected?.title ?? '');

  useEffect(() => {
    setQuery(selected?.title ?? '');
  }, [selected?.id, selected?.title]);

  const matches = useMemo(() => {
    const normalized = query.trim().toLowerCase();
    if (!normalized) return items.slice(0, 5);
    return items
      .filter((item) => item.title.toLowerCase().includes(normalized))
      .slice(0, 5);
  }, [items, query]);

  return (
    <section className="card editorial-workbench-picker" data-testid="editorial-workbench-picker">
      <label>
        <span className="rub">Выбор поста</span>
        <input
          aria-label="Выбор поста"
          placeholder="Начните вводить название..."
          value={query}
          onChange={(event) => setQuery(event.target.value)}
        />
      </label>
      <div className="picker-results">
        {matches.map((item) => (
          <button
            className={`picker-result${item.id === selectedId ? ' active' : ''}`}
            key={item.id}
            type="button"
            onClick={() => {
              setQuery(item.title);
              onSelect(item.id);
            }}
          >
            <b>{item.title}</b>
            <span>{item.date} · {item.platform}</span>
          </button>
        ))}
      </div>
    </section>
  );
}
