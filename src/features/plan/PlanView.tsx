import { useMemo, useState } from 'react';
import { detectBroadcastPlanConflicts, type ContentPlanItem, type WorkspaceState } from '../../domain/editorialWorkspace';
import { Icon } from '../../shared/ui/Icon';
import { EmptyState, HitlGate } from '../../shared/ui/WorkflowPrimitives';
import { statusLabel } from '../../shared/format/production';

export function PlanView({
  workspace,
  onGenerate,
  onItemChange,
  onApprove,
  onBrief
}: {
  workspace: WorkspaceState;
  onGenerate: () => void;
  onItemChange: (item: ContentPlanItem) => void;
  onApprove: (itemId: string) => void;
  onBrief: (item: ContentPlanItem) => void;
}) {
  const [expandedId, setExpandedId] = useState<string | null>(workspace.contentPlanItems[0]?.id ?? null);
  const [editingItem, setEditingItem] = useState<ContentPlanItem | null>(null);
  const items = workspace.contentPlanItems;
  const warnings = useMemo(
    () => detectBroadcastPlanConflicts(workspace, items),
    [workspace, items]
  );
  const activeWarnings = warnings.filter((warning) => warning.severity !== 'green');
  const topicDistribution = getPlanDistribution(items, 'topicTitle');
  const fabulaDistribution = getPlanDistribution(items, 'fabulaTitle');

  function startEdit(item: ContentPlanItem) {
    setExpandedId(item.id);
    setEditingItem({ ...item });
  }

  function saveEdit() {
    if (!editingItem) return;
    onItemChange({ ...editingItem, manualOverride: true });
    setExpandedId(editingItem.id);
    setEditingItem(null);
  }

  function updateEditingItem(patch: Partial<ContentPlanItem>) {
    setEditingItem((current) => (current ? { ...current, ...patch } : current));
  }

  function updateEditingTopic(topicId: string) {
    const topic = workspace.topics.find((item) => item.id === topicId);
    updateEditingItem({ topicId, topicTitle: topic?.title ?? '' });
  }

  function updateEditingFabula(fabulaId: string) {
    const fabula = workspace.fabulas.find((item) => item.id === fabulaId);
    updateEditingItem({ fabulaId, fabulaTitle: fabula?.title ?? '' });
  }

  return (
    <div className="page wide fade-up">
      <div className="broadcast-layout">
        <section className="broadcast-main">
          <HitlGate
            tag="HITL · Gate 1 — Сетка вещания"
            title="Соберите и утвердите слоты контент-плана"
            subtitle="Сетка распределяет темы и фабулы по датам, форматам и площадкам. Ручные правки важнее весов, но конфликты подсвечиваются."
            action={items.length > 0 ? 'Пересобрать сетку' : 'Собрать сетку'}
            onAction={onGenerate}
          />
          {items.length > 0 ? (
            <div className="broadcast-list" data-testid="broadcast-grid">
              <div className="broadcast-toolbar">
                <div>
                  <h2>Сетка на {workspace.contentPlanSettings.planningHorizonDays} дней</h2>
                  <p>{workspace.contentPlanSettings.postsPerWeek} поста в неделю · {items.length} слотов</p>
                </div>
                <span className={`validation-run-state ${activeWarnings.length > 0 ? 'stale' : 'fresh'}`}>
                  {activeWarnings.length > 0 ? `${activeWarnings.length} предупрежд.` : 'OK'}
                </span>
              </div>
              {items.map((item) => {
                const isExpanded = expandedId === item.id;
                const isEditing = editingItem?.id === item.id;
                const itemWarnings = warnings.filter((warning) =>
                  warning.targetType === 'slot' && warning.targetId === item.id
                );
                const current = isEditing ? editingItem : item;

                return (
                  <article className={`card broadcast-row${isExpanded ? ' expanded' : ''}`} key={item.id}>
                    <button
                      className="broadcast-row-main"
                      type="button"
                      onClick={() => setExpandedId(isExpanded ? null : item.id)}
                    >
                      <span className="broadcast-date">{formatPlanDate(item.date)}</span>
                      <span className="broadcast-title">{item.title}</span>
                      <span className="broadcast-meta">{item.platform}</span>
                      <span className="broadcast-meta">{item.format}</span>
                      <span className="broadcast-meta">{item.topicTitle}</span>
                      <span className="broadcast-meta">{item.fabulaTitle}</span>
                      <span className={`pill ${item.approvalStatus === 'approved' ? 'ok' : 'pin'}`}>
                        <i />
                        {statusLabel(item.approvalStatus)}
                      </span>
                      {itemWarnings.length > 0 ? <span className="validation-badge yellow">warning</span> : null}
                    </button>
                    {isExpanded ? (
                      <div className="broadcast-details">
                        {isEditing && current ? (
                          <div className="broadcast-edit-grid">
                            <label>
                              Заголовок
                              <input
                                value={current.title}
                                onChange={(event) => updateEditingItem({ title: event.target.value })}
                              />
                            </label>
                            <label>
                              Дата
                              <input
                                type="date"
                                value={current.date}
                                onChange={(event) => updateEditingItem({ date: event.target.value })}
                              />
                            </label>
                            <label>
                              Площадка
                              <input
                                value={current.platform}
                                onChange={(event) => updateEditingItem({ platform: event.target.value })}
                              />
                            </label>
                            <label>
                              Формат
                              <select
                                value={current.format}
                                onChange={(event) => updateEditingItem({ format: event.target.value })}
                              >
                                {workspace.contentPlanSettings.allowedFormats.map((format) => (
                                  <option value={format} key={format}>{format}</option>
                                ))}
                              </select>
                            </label>
                            <label>
                              Тема
                              <select value={current.topicId ?? ''} onChange={(event) => updateEditingTopic(event.target.value)}>
                                {workspace.topics.map((topic) => (
                                  <option value={topic.id} key={topic.id}>{topic.title}</option>
                                ))}
                              </select>
                            </label>
                            <label>
                              Фабула
                              <select value={current.fabulaId ?? ''} onChange={(event) => updateEditingFabula(event.target.value)}>
                                {workspace.fabulas.map((fabula) => (
                                  <option value={fabula.id} key={fabula.id}>{fabula.title}</option>
                                ))}
                              </select>
                            </label>
                            <label>
                              Приоритет
                              <input
                                value={current.priority}
                                onChange={(event) => updateEditingItem({ priority: event.target.value })}
                              />
                            </label>
                            <label className="broadcast-edit-wide">
                              Ожидаемый эффект
                              <textarea
                                value={current.expectedEffect}
                                onChange={(event) => updateEditingItem({ expectedEffect: event.target.value })}
                              />
                            </label>
                            <div className="entity-actions broadcast-edit-actions">
                              <button className="btn btn-pri" type="button" onClick={saveEdit}>
                                Сохранить
                              </button>
                              <button className="btn btn-sec" type="button" onClick={() => setEditingItem(null)}>
                                Отменить
                              </button>
                            </div>
                          </div>
                        ) : (
                          <>
                            <dl className="entity-detail-list">
                              <div>
                                <dt>Ожидаемый эффект</dt>
                                <dd>{item.expectedEffect}</dd>
                              </div>
                              <div>
                                <dt>Связка</dt>
                                <dd>{item.topicTitle} · {item.fabulaTitle}</dd>
                              </div>
                              <div>
                                <dt>Источник</dt>
                                <dd>{item.sourceSignalId ?? item.insightId}</dd>
                              </div>
                              <div>
                                <dt>Режим</dt>
                                <dd>{item.manualOverride ? 'Ручная правка сетки' : 'Собрано deterministic-сервисом'}</dd>
                              </div>
                            </dl>
                            {itemWarnings.length > 0 ? (
                              <div className="matrix-warnings">
                                {itemWarnings.map((warning) => <p key={warning.id}>{warning.message}</p>)}
                              </div>
                            ) : null}
                            <div className="entity-actions">
                              <button className="btn btn-sec" type="button" onClick={() => startEdit(item)}>
                                Редактировать
                              </button>
                              <button
                                className="btn btn-sec"
                                type="button"
                                disabled={item.approvalStatus === 'approved'}
                                onClick={() => onApprove(item.id)}
                              >
                                Утвердить
                              </button>
                              <button
                                className="btn btn-pri"
                                type="button"
                                disabled={item.approvalStatus !== 'approved'}
                                onClick={() => onBrief(item)}
                              >
                                <Icon name="brief" size={16} />
                                Подготовить фабулу поста
                              </button>
                            </div>
                          </>
                        )}
                      </div>
                    ) : null}
                  </article>
                );
              })}
            </div>
          ) : (
            <EmptyState text="Соберите сетку вещания из текущего радара, тем и фабул редакционной модели." />
          )}
        </section>
        <aside className="aside broadcast-aside">
          <div className="panel validation-panel">
            <div className="validation-head">
              <h3>Сетка вещания</h3>
              <span className={`validation-run-state ${activeWarnings.length > 0 ? 'stale' : 'fresh'}`}>
                {activeWarnings.length > 0 ? 'Есть конфликты' : 'Баланс OK'}
              </span>
              <p>Ручные правки слотов сохраняются, даже если выходят за declared weights. Конфликт нужен как сигнал редактору.</p>
            </div>
            <div className="validator-summary">
              <div><strong>{items.length}</strong><span>слотов</span></div>
              <div><strong>{workspace.contentPlanSettings.postsPerWeek}</strong><span>в неделю</span></div>
              <div><strong>{topicDistribution.length}</strong><span>тем</span></div>
              <div><strong>{fabulaDistribution.length}</strong><span>фабул</span></div>
            </div>
            <DistributionList title="Темы" items={topicDistribution} />
            <DistributionList title="Фабулы" items={fabulaDistribution} />
            {activeWarnings.length > 0 ? (
              <div className="validation-warnings">
                {activeWarnings.slice(0, 6).map((warning) => <p key={warning.id}>{warning.message}</p>)}
              </div>
            ) : null}
          </div>
        </aside>
      </div>
    </div>
  );
}

function DistributionList({ title, items }: { title: string; items: Array<{ title: string; count: number; share: number }> }) {
  return (
    <div className="plan-distribution">
      <h4>{title}</h4>
      {items.length > 0 ? (
        items.map((item) => (
          <div className="plan-distribution-row" key={item.title}>
            <span>{item.title}</span>
            <b>{Math.round(item.share)}%</b>
          </div>
        ))
      ) : (
        <p className="panel-note">Нет слотов для расчета.</p>
      )}
    </div>
  );
}

function getPlanDistribution(
  items: ContentPlanItem[],
  field: 'topicTitle' | 'fabulaTitle'
): Array<{ title: string; count: number; share: number }> {
  const total = Math.max(items.length, 1);
  const counts = new Map<string, number>();
  items.forEach((item) => {
    const title = item[field] ?? 'Не задано';
    counts.set(title, (counts.get(title) ?? 0) + 1);
  });

  return Array.from(counts.entries()).map(([title, count]) => ({
    title,
    count,
    share: (count / total) * 100
  }));
}

function formatPlanDate(date: string): string {
  if (!date) return 'Без даты';
  const parsed = new Date(`${date}T00:00:00`);
  if (Number.isNaN(parsed.getTime())) return date;
  return parsed.toLocaleDateString('ru-RU', { day: '2-digit', month: 'short' });
}
