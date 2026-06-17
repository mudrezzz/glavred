import { useEffect, useMemo, useState } from 'react';
import {
  getPlanningHorizonDays,
  normalizeContentPlanSettings,
  type BroadcastGridDemandSummary,
  type ContentPlanSettings
} from '../../domain/editorialWorkspace';
import { MiniPublishCalendar } from './MiniPublishCalendar';
import { getWeekdaysFromSlots, togglePublishSlot } from './planningCalendar';

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

  const parsedTimes = useMemo(() => parseTimes(timesText), [timesText]);
  const normalizedDraft = useMemo(
    () => normalizeDraft(draft, parsedTimes, settings),
    [draft, parsedTimes, settings]
  );
  const dirty = JSON.stringify(normalizedDraft) !== JSON.stringify(settings);

  function updatePeriod(period: ContentPlanSettings['period']) {
    setDraft((current) => ({
      ...current,
      period,
      planningHorizonDays: getPlanningHorizonDays(period),
      publishSlots: []
    }));
  }

  function toggleDate(date: string) {
    setDraft((current) => ({
      ...current,
      publishSlots: togglePublishSlot(current, date, parsedTimes[0] ?? '10:00')
    }));
  }

  return (
    <section className="card import-toolbar-panel plan-settings-panel" data-testid="plan-settings-panel">
      <div className="plan-settings-grid">
        <label>
          Период
          <select value={draft.period} onChange={(event) => updatePeriod(event.target.value as ContentPlanSettings['period'])}>
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
          <input value={draft.defaultPlatform} onChange={(event) => setDraft((current) => ({ ...current, defaultPlatform: event.target.value }))} />
        </label>
        <label>
          Политика сигналов
          <select
            value={draft.signalSelectionPolicy}
            onChange={(event) => setDraft((current) => ({
              ...current,
              signalSelectionPolicy: event.target.value as ContentPlanSettings['signalSelectionPolicy']
            }))}
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
            onChange={(event) => setDraft((current) => ({ ...current, minCandidatesPerSlot: Number(event.target.value) }))}
          />
        </label>
        <label>
          Макс. кандидатов на слот
          <input
            type="number"
            min={1}
            max={20}
            value={draft.maxCandidatesPerSlot}
            onChange={(event) => setDraft((current) => ({ ...current, maxCandidatesPerSlot: Number(event.target.value) }))}
          />
        </label>
        <label className="plan-settings-wide">
          Время публикаций
          <input value={timesText} placeholder="10:00, 17:30" onChange={(event) => setTimesText(event.target.value)} />
        </label>
      </div>
      <MiniPublishCalendar settings={normalizedDraft} onToggleDate={toggleDate} />
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
      <div className="inline-actions plan-settings-actions">
        <button className="btn btn-pri" type="button" onClick={() => onSave(normalizedDraft)} disabled={!dirty}>
          Сохранить настройку
        </button>
        <button className="btn btn-sec" type="button" onClick={onGenerate}>
          Собрать сетку
        </button>
      </div>
    </section>
  );
}

function normalizeDraft(
  draft: ContentPlanSettings,
  publishingTimes: string[],
  fallback: ContentPlanSettings
): ContentPlanSettings {
  const time = publishingTimes[0] ?? fallback.publishingTimes[0] ?? '10:00';
  const publishSlots = draft.publishSlots.map((slot) => ({ ...slot, time }));
  return normalizeContentPlanSettings({
    ...draft,
    publishingDays: getWeekdaysFromSlots(publishSlots),
    publishingTimes,
    publishSlots
  }, fallback);
}

function parseTimes(value: string): string[] {
  return value.split(',').map((item) => item.trim()).filter(Boolean);
}
