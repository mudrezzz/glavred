import { useMemo } from 'react';
import type { ContentPlanItem, PlanWeightWarning, WorkspaceState } from '../../domain/editorialWorkspace';
import { EmptyState } from '../../shared/ui/WorkflowPrimitives';
import { BroadcastGridRow } from './BroadcastGridRow';
import {
  getInitialBroadcastCalendarDate,
  groupBroadcastItemsByDate,
  withBroadcastItemSlots
} from './broadcastGridCalendar';
import { createPlanningCalendarMonths } from './planningCalendar';

const WEEKDAY_LABELS = ['Пн', 'Вт', 'Ср', 'Чт', 'Пт', 'Сб', 'Вс'];

export function BroadcastGridCalendarView({
  items,
  selectedDate,
  workspace,
  warnings,
  onSelectDate,
  onItemChange,
  onApprove
}: {
  items: ContentPlanItem[];
  selectedDate: string;
  workspace: WorkspaceState;
  warnings: PlanWeightWarning[];
  onSelectDate: (date: string) => void;
  onItemChange: (item: ContentPlanItem) => void;
  onApprove: (itemId: string) => void;
}) {
  const itemsByDate = useMemo(() => groupBroadcastItemsByDate(items), [items]);
  const calendarSettings = useMemo(
    () => withBroadcastItemSlots(workspace.contentPlanSettings, items),
    [items, workspace.contentPlanSettings]
  );
  const months = useMemo(() => createPlanningCalendarMonths(calendarSettings), [calendarSettings]);
  const activeDate = selectedDate || getInitialBroadcastCalendarDate(items, calendarSettings);
  const activeItems = activeDate ? itemsByDate.get(activeDate) ?? [] : [];

  if (items.length === 0) {
    return (
      <EmptyState text="Сохраните настройку сетки и соберите план: календарь покажет даты публикаций и кандидатов по каждой дате." />
    );
  }

  return (
    <div className="broadcast-calendar-view" data-testid="broadcast-calendar-view">
      <section className="publish-calendar-panel broadcast-calendar-panel" aria-label="Календарь сетки кандидатов">
        <div className="publish-calendar-head">
          <div>
            <h3>{calendarTitle(workspace.contentPlanSettings.period)}</h3>
            <p>Клик по дате показывает кандидатов на эту публикацию под календарем.</p>
          </div>
          <span className="validation-run-state fresh">
            {items.length} кандидатов
          </span>
        </div>
        <div className={`publish-calendar ${workspace.contentPlanSettings.period}`}>
          {months.map((month) => (
            <div className="publish-calendar-month" key={month.key}>
              <h4>{month.title}</h4>
              <div className="publish-calendar-weekdays">
                {WEEKDAY_LABELS.map((label) => <span key={label}>{label}</span>)}
              </div>
              <div className="publish-calendar-grid">
                {month.weeks.flat().map((day) => {
                  const count = itemsByDate.get(day.date)?.length ?? 0;
                  return (
                    <button
                      aria-pressed={activeDate === day.date}
                      className={[
                        'publish-calendar-day',
                        'broadcast-calendar-day',
                        day.isSelected ? 'selected' : '',
                        activeDate === day.date ? 'active' : '',
                        day.inPeriod ? '' : 'outside',
                        day.isToday ? 'today' : '',
                        count > 0 ? 'has-candidates' : ''
                      ].filter(Boolean).join(' ')}
                      disabled={!day.inPeriod}
                      key={day.date}
                      type="button"
                      onClick={() => onSelectDate(day.date)}
                    >
                      <span>{day.dayOfMonth}</span>
                      <span className="broadcast-calendar-count">{count}</span>
                    </button>
                  );
                })}
              </div>
            </div>
          ))}
        </div>
      </section>
      <section className="broadcast-calendar-date-list" aria-live="polite">
        <div className="entity-list-toolbar compact">
          <div className="entity-toolbar-copy">
            <h2>{activeDate ? formatDateLabel(activeDate) : 'Дата не выбрана'}</h2>
            <p>{activeItems.length} кандидатов на дату</p>
          </div>
        </div>
        {activeItems.length > 0 ? (
          <div className="broadcast-list" data-testid="broadcast-calendar-date-list">
            {activeItems.map((item, index) => (
              <BroadcastGridRow
                defaultExpanded={index === 0}
                item={item}
                itemWarnings={warnings.filter((warning) => warning.targetType === 'slot' && warning.targetId === item.id)}
                key={item.id}
                workspace={workspace}
                onApprove={onApprove}
                onItemChange={onItemChange}
              />
            ))}
          </div>
        ) : (
          <EmptyState text="На выбранную дату пока нет кандидатов после текущих фильтров." />
        )}
      </section>
    </div>
  );
}

function calendarTitle(period: WorkspaceState['contentPlanSettings']['period']): string {
  if (period === 'week') return 'Календарь на неделю';
  if (period === 'quarter') return 'Календарь на квартал';
  return 'Календарь на месяц';
}

function formatDateLabel(date: string): string {
  return new Date(`${date}T00:00:00`).toLocaleDateString('ru-RU', {
    day: '2-digit',
    month: 'long',
    year: 'numeric'
  });
}
