import type { ContentPlanSettings } from '../../domain/editorialWorkspace';
import { createPlanningCalendarMonths, getPublishSelectionSummary } from './planningCalendar';

const WEEKDAY_LABELS = ['Пн', 'Вт', 'Ср', 'Чт', 'Пт', 'Сб', 'Вс'];

export function MiniPublishCalendar({
  settings,
  onToggleDate
}: {
  settings: ContentPlanSettings;
  onToggleDate: (date: string) => void;
}) {
  const months = createPlanningCalendarMonths(settings);
  const summary = getPublishSelectionSummary(settings);

  return (
    <section className="publish-calendar-panel" aria-label="Мини-календарь публикаций">
      <div className="publish-calendar-head">
        <div>
          <h3>Календарь публикаций</h3>
          <p>{selectionMessage(summary.remaining, summary.extra)}</p>
        </div>
        <span className="validation-run-state fresh">
          {summary.selected}/{summary.target} назначено
        </span>
      </div>
      <div className={`publish-calendar ${settings.period}`}>
        {months.map((month) => (
          <div className="publish-calendar-month" key={month.key}>
            <h4>{month.title}</h4>
            <div className="publish-calendar-weekdays">
              {WEEKDAY_LABELS.map((label) => <span key={label}>{label}</span>)}
            </div>
            <div className="publish-calendar-grid">
              {month.weeks.flat().map((day) => (
                <button
                  aria-pressed={day.isSelected}
                  className={[
                    'publish-calendar-day',
                    day.isSelected ? 'selected' : '',
                    day.inPeriod ? '' : 'outside',
                    day.isToday ? 'today' : ''
                  ].filter(Boolean).join(' ')}
                  disabled={!day.inPeriod}
                  key={day.date}
                  type="button"
                  onClick={() => onToggleDate(day.date)}
                >
                  {day.dayOfMonth}
                </button>
              ))}
            </div>
          </div>
        ))}
      </div>
    </section>
  );
}

function selectionMessage(remaining: number, extra: number): string {
  if (remaining > 0) return `Осталось назначить ${remaining} слотов.`;
  if (extra > 0) return `Выбрано на ${extra} слотов больше планового темпа.`;
  return 'Плановый темп закрыт выбранными датами.';
}
