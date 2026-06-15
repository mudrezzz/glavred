import type { SignalsTab } from './helpers';

export function SignalsTabs({
  tab,
  newCount,
  onChange
}: {
  tab: SignalsTab;
  newCount: number;
  onChange: (tab: SignalsTab) => void;
}) {
  return (
    <div className="tabs signal-tabs" role="tablist" aria-label="Сигналы">
      <button className={`tab ${tab === 'radars' ? 'active' : ''}`} type="button" onClick={() => onChange('radars')}>
        Радары
      </button>
      <button className={`tab ${tab === 'signals' ? 'active' : ''}`} type="button" onClick={() => onChange('signals')}>
        Найденные сигналы
        <span className="tab-count">{newCount}</span>
      </button>
      <button className={`tab ${tab === 'candidates' ? 'active' : ''}`} type="button" onClick={() => onChange('candidates')}>
        Кандидаты постов
      </button>
    </div>
  );
}
