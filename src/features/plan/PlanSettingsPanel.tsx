import { useEffect, useMemo, useState } from 'react';
import {
  getPlanningHorizonDays,
  normalizeContentPlanSettings,
  type BroadcastGridDemandSummary,
  type ContentPlanSettings
} from '../../domain/editorialWorkspace';

const WEEKDAYS = [
  { value: 1, label: 'Пн' },
  { value: 2, label: 'Вт' },
  { value: 3, label: 'Ср' },
  { value: 4, label: 'Чт' },
  { value: 5, label: 'Пт' },
  { value: 6, label: 'Сб' },
  { value: 0, label: 'Вс' }
];

export function PlanSettingsPanel({
  demandSummary,
  hasCurrentPlan,
  settings,
  onGenerate,
  onSave
}: {
  demandSummary: BroadcastGridDemandSummary;
  hasCurrentPlan: boolean;
  settings: ContentPlanSettings;
  onGenerate: () => void;
  onSave: (settings: ContentPlanSettings) => void;
}) {
  const [draft, setDraft] = useState(settings);
  const [timesText, setTimesText] = useState(settings.publishingTimes.join(', '));

  useEffect(() => {
    setDraft(settings);
    setTimesText(settings.publishingTimes.join(', '));
  }, [settings]);

  const normalizedDraft = useMemo(
    () => normalizeContentPlanSettings({ ...draft, publishingTimes: parseTimes(timesText) }, settings),
    [draft, settings, timesText]
  );
  const dirty = JSON.stringify(normalizedDraft) !== JSON.stringify(settings);

  function toggleDay(day: number) {
    setDraft((current) => {
      const days = current.publishingDays.includes(day)
        ? current.publishingDays.filter((item) => item !== day)
        : [...current.publishingDays, day];
      return { ...current, publishingDays: days };
    });
  }

  function save() {
    onSave(normalizedDraft);
  }

  return (
    <section className="card import-toolbar-panel plan-settings-panel" data-testid="plan-settings-panel">
      <div className="plan-settings-grid">
        <label>
          Период
          <select
            value={draft.period}
            onChange={(event) =>
              setDraft((current) => ({
                ...current,
                period: event.target.value as ContentPlanSettings['period'],
                planningHorizonDays: getPlanningHorizonDays(event.target.value as ContentPlanSettings['period'])
              }))
            }
          >
            <option value="week">Неделя</option>
            <option value="month">Месяц</option>
            <option value="quarter">Квартал</option>
          </select>
        </label>
        <label>
          Темп
          <input
            type="number"
            min={1}
            max={21}
            value={draft.postsPerWeek}
            onChange={(event) => setDraft((current) => ({ ...current, postsPerWeek: Number(event.target.value) }))}
          />
        </label>
        <label>
          Площадка
          <input
            value={draft.defaultPlatform}
            onChange={(event) => setDraft((current) => ({ ...current, defaultPlatform: event.target.value }))}
          />
        </label>
        <label>
          Политика сигналов
          <select
            value={draft.signalSelectionPolicy}
            onChange={(event) =>
              setDraft((current) => ({
                ...current,
                signalSelectionPolicy: event.target.value as ContentPlanSettings['signalSelectionPolicy']
              }))
            }
          >
            <option value="hitl-only">Только HITL</option>
            <option value="automatic">Автоматически</option>
            <option value="automatic-with-review">Авто с ревью</option>
          </select>
        </label>
        <label>
          Мин. кандидатов на слот
          <input
            type="number"
            min={1}
            max={10}
            value={draft.minCandidatesPerSlot}
            onChange={(event) =>
              setDraft((current) => ({ ...current, minCandidatesPerSlot: Number(event.target.value) }))
            }
          />
        </label>
        <label>
          Макс. кандидатов на слот
          <input
            type="number"
            min={1}
            max={20}
            value={draft.maxCandidatesPerSlot}
            onChange={(event) =>
              setDraft((current) => ({ ...current, maxCandidatesPerSlot: Number(event.target.value) }))
            }
          />
        </label>
        <fieldset className="plan-settings-days">
          <legend>Дни публикаций</legend>
          <div className="segmented plan-day-toggle">
            {WEEKDAYS.map((day) => (
              <button
                className={draft.publishingDays.includes(day.value) ? 'active' : ''}
                type="button"
                key={day.value}
                onClick={() => toggleDay(day.value)}
              >
                {day.label}
              </button>
            ))}
          </div>
        </fieldset>
        <label className="plan-settings-wide">
          Время публикаций
          <input
            value={timesText}
            placeholder="10:00, 17:30"
            onChange={(event) => setTimesText(event.target.value)}
          />
        </label>
      </div>
      <div className="plan-settings-summary">
        <div><strong>{demandSummary.slotCount}</strong><span>слотов в каркасе</span></div>
        <div><strong>{demandSummary.availableCandidateCount}</strong><span>доступных кандидатов</span></div>
        <div><strong>{demandSummary.approvedConceptCount}</strong><span>утвержденных концептов</span></div>
      </div>
      {hasCurrentPlan && dirty ? (
        <p className="plan-settings-warning">
          После сохранения текущая сетка и следующие production-артефакты будут сброшены как устаревшие.
        </p>
      ) : null}
      <div className="entity-actions">
        <button className="btn btn-pri" type="button" onClick={save} disabled={!dirty}>
          Сохранить настройку
        </button>
        <button className="btn btn-sec" type="button" onClick={onGenerate}>
          Собрать сетку
        </button>
      </div>
    </section>
  );
}

function parseTimes(value: string): string[] {
  return value.split(',').map((item) => item.trim()).filter(Boolean);
}
