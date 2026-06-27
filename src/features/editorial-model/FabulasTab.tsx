import { useEffect, useState } from 'react';
import type { ContextChatIntent } from '../../application/contextChat';
import {
  addFabula,
  addTopic,
  completeTopicFabulaMatrix,
  createEditorialRule,
  createFabulaDraft,
  createTopicDraft,
  deleteFabula,
  deleteEditorialRule,
  deleteTopic,
  getTopicFabulaWarnings,
  normalizeWeightRange,
  updateEditorialRule,
  type EditorialModel,
  type EditorialRule,
  type EditorialRuleGroup,
  type Fabula,
  type ProjectProfile,
  type Topic,
  type TopicFabulaMatrixEntry,
  type WorkspaceState
} from '../../domain/editorialWorkspace';
import { WeightRangeEditor } from '../../shared/ui/WeightRangeEditor';
import { FabulaSizeIntentSelect, fabulaSizeIntentLabel } from './FabulaSizeIntentSelect';
import { FabulaResearchDepthSelect, fabulaResearchDepthLabel } from './FabulaResearchDepthSelect';
import { FabulaResearchStrategyEditor } from './FabulaResearchStrategyEditor';
import { EditorialValidationPanel, ValidationBadge } from './ValidationPanel';
import {
  EDITORIAL_TABS,
  RULE_SECTIONS,
  countCompatibleFabulas,
  countCompatibleTopics,
  editorialRuleGroupLabel,
  getReferencedFabulaIds,
  getReferencedTopicIds,
  isMatrixEnabled,
  sameMatrix,
  splitLines
} from './helpers';
import type { EditorialModelTab } from './types';

export function FabulaListView({
  chatIntent,
  fabulas,
  topics,
  matrix,
  referencedFabulaIds,
  onCreate,
  onChatIntentConsumed,
  onDelete,
  onSave
}: {
  chatIntent: Extract<ContextChatIntent, { actionType: 'addFabula' }> | null;
  fabulas: Fabula[];
  topics: Topic[];
  matrix: TopicFabulaMatrixEntry[];
  referencedFabulaIds: Set<string>;
  onCreate: (fabula: Fabula) => void;
  onChatIntentConsumed: () => void;
  onDelete: (fabulaId: string) => void;
  onSave: (fabula: Fabula) => void;
}) {
  const [expandedId, setExpandedId] = useState<string | null>(fabulas[0]?.id ?? null);
  const [editingId, setEditingId] = useState<string | null>(null);
  const [draft, setDraft] = useState<Fabula | null>(null);

  function startEdit(fabula: Fabula) {
    setExpandedId(fabula.id);
    setEditingId(fabula.id);
    setDraft({ ...fabula, rules: [...fabula.rules], structure: [...fabula.structure], proofRequirements: [...fabula.proofRequirements] });
  }

  function startCreate() {
    if (editingId === 'new' && draft) {
      setExpandedId(draft.id);
      return;
    }

    const fabula = createFabulaDraft();
    setExpandedId(fabula.id);
    setEditingId('new');
    setDraft(fabula);
  }

  useEffect(() => {
    if (!chatIntent) return;

    const fabula = {
      ...createFabulaDraft(),
      ...chatIntent.payload,
      rules: chatIntent.payload.rules ? [...chatIntent.payload.rules] : [],
      structure: chatIntent.payload.structure ? [...chatIntent.payload.structure] : [],
      proofRequirements: chatIntent.payload.proofRequirements ? [...chatIntent.payload.proofRequirements] : []
    };
    setExpandedId(fabula.id);
    setEditingId('new');
    setDraft(fabula);
    onChatIntentConsumed();
  }, [chatIntent, onChatIntentConsumed]);

  function save() {
    if (!draft) return;
    const normalized = { ...draft, weightRange: normalizeWeightRange(draft.weightRange) };
    if (editingId === 'new') {
      onCreate(normalized);
      setExpandedId(normalized.id);
    } else {
      onSave(normalized);
    }
    setEditingId(null);
    setDraft(null);
  }

  function remove(fabula: Fabula) {
    const hasProductionReferences = referencedFabulaIds.has(fabula.id);
    const message = hasProductionReferences
      ? `Фабула "${fabula.title}" уже используется в текущих производственных артефактах. Удаление уберет фабулу и ее связи в матрице, но не перепишет уже созданные инсайты, планы или фабулы постов. Удалить?`
      : `Удалить фабулу "${fabula.title}" и все ее связи в матрице?`;

    if (!window.confirm(message)) return;

    onDelete(fabula.id);
    if (expandedId === fabula.id) setExpandedId(null);
    if (editingId === fabula.id) {
      setEditingId(null);
      setDraft(null);
    }
  }

  return (
    <div className="entity-list">
      <div className="entity-list-toolbar">
        <span className="mono-label">{fabulas.length} фабул</span>
        <button className="btn btn-sec btn-sm" type="button" onClick={startCreate}>
          + Фабула
        </button>
      </div>
      {editingId === 'new' && draft ? (
        <article className="card entity-row">
          <div className="entity-row-main">
            <span className="entity-title-placeholder">{draft.title.trim() || 'Новая фабула'}</span>
            <div className="entity-row-meta">
              <span className="entity-meta-chip">{draft.weightRange.min}-{draft.weightRange.max}%</span>
              <span className="entity-meta-chip">{fabulaSizeIntentLabel(draft.sizeIntent)}</span>
              <span className="entity-meta-chip">{fabulaResearchDepthLabel(draft.researchDepth)}</span>
              <span className={`status-chip ${draft.status}`}>{draft.status === 'active' ? 'активно' : 'пауза'}</span>
              <span className="entity-meta-chip">{draft.rules.length} правил</span>
              <span className="entity-meta-chip">{draft.proofRequirements.length} proof</span>
              <span className="entity-meta-chip">{topics.length} тем</span>
            </div>
            <ValidationBadge status={draft.title.trim() ? 'green' : 'yellow'} />
          </div>
          <FabulaEditor
            fabula={draft}
            onCancel={() => {
              setEditingId(null);
              setDraft(null);
              setExpandedId(fabulas[0]?.id ?? null);
            }}
            onChange={setDraft}
            onSave={save}
          />
        </article>
      ) : null}
      {fabulas.map((fabula) => {
        const compatibleCount = countCompatibleTopics(fabula.id, matrix);
        const isExpanded = expandedId === fabula.id;
        const isEditing = editingId === fabula.id && draft;
        return (
          <article className="card entity-row" key={fabula.id}>
            <div className="entity-row-main">
              <button
                className="entity-title-button"
                type="button"
                onClick={() => setExpandedId(isExpanded ? null : fabula.id)}
              >
                {fabula.title}
              </button>
              <div className="entity-row-meta">
                <span className="entity-meta-chip">{fabula.weightRange.min}-{fabula.weightRange.max}%</span>
                <span className="entity-meta-chip">{fabulaSizeIntentLabel(fabula.sizeIntent)}</span>
                <span className="entity-meta-chip">{fabulaResearchDepthLabel(fabula.researchDepth)}</span>
                <span className={`status-chip ${fabula.status}`}>{fabula.status === 'active' ? 'активно' : 'пауза'}</span>
                <span className="entity-meta-chip">{fabula.rules.length} правил</span>
                <span className="entity-meta-chip">{fabula.proofRequirements.length} proof</span>
                <span className="entity-meta-chip">{compatibleCount} тем</span>
              </div>
              <ValidationBadge status={compatibleCount > 0 ? 'green' : 'red'} />
            </div>
            {isExpanded ? (
              isEditing ? (
                <FabulaEditor
                  fabula={draft}
                  onCancel={() => {
                    setEditingId(null);
                    setDraft(null);
                  }}
                  onChange={setDraft}
                  onSave={save}
                />
              ) : (
                <div className="entity-details">
                  <div className="entity-details-scroll">
                    <p>{fabula.description}</p>
                    <dl className="entity-detail-list">
                      <dt>Драматургия</dt>
                      <dd>{fabula.dramaturgy}</dd>
                      <dt>Структура</dt>
                      <dd>{fabula.structure.join('; ')}</dd>
                      <dt>Proof requirements</dt>
                      <dd>{fabula.proofRequirements.join('; ')}</dd>
                      <dt>Правила</dt>
                      <dd>{fabula.rules.join('; ')}</dd>
                      <dt>Масштаб</dt>
                      <dd>{fabulaSizeIntentLabel(fabula.sizeIntent)}</dd>
                      <dt>Глубина исследования</dt>
                      <dd>{fabulaResearchDepthLabel(fabula.researchDepth)}</dd>
                      <dt>Источники</dt>
                      <dd>{fabula.researchStrategy.mode === 'auto' ? 'Автоопределение' : `${fabula.researchStrategy.instructions.length} поруч.`}</dd>
                      <dt>Применимые темы</dt>
                      <dd>{topics.filter((topic) => isMatrixEnabled(topic.id, fabula.id, matrix)).map((topic) => topic.title).join(', ')}</dd>
                    </dl>
                  </div>
                  <div className="inline-actions">
                    <button className="btn btn-sec btn-sm" type="button" onClick={() => startEdit(fabula)}>
                      Редактировать
                    </button>
                    <button className="btn btn-sec btn-sm danger-text" type="button" onClick={() => remove(fabula)}>
                      Удалить
                    </button>
                  </div>
                </div>
              )
            ) : null}
          </article>
        );
      })}
    </div>
  );
}

function FabulaEditor({
  fabula,
  onChange,
  onSave,
  onCancel
}: {
  fabula: Fabula;
  onChange: (fabula: Fabula) => void;
  onSave: () => void;
  onCancel: () => void;
}) {
  return (
    <div className="entity-edit-form">
      <div className="entity-edit-scroll">
        <label>
          Название
          <input value={fabula.title} onChange={(event) => onChange({ ...fabula, title: event.target.value })} />
        </label>
        <label>
          Описание
          <textarea value={fabula.description} onChange={(event) => onChange({ ...fabula, description: event.target.value })} />
        </label>
        <label>
          Драматургия
          <textarea value={fabula.dramaturgy} onChange={(event) => onChange({ ...fabula, dramaturgy: event.target.value })} />
        </label>
        <WeightRangeEditor value={fabula.weightRange} onChange={(weightRange) => onChange({ ...fabula, weightRange })} />
        <FabulaSizeIntentSelect fabula={fabula} onChange={onChange} />
        <FabulaResearchDepthSelect fabula={fabula} onChange={onChange} />
        <FabulaResearchStrategyEditor fabula={fabula} onChange={onChange} />
        <label>
          Структура
          <textarea value={fabula.structure.join('\n')} onChange={(event) => onChange({ ...fabula, structure: splitLines(event.target.value) })} />
        </label>
        <label>
          Proof requirements
          <textarea
            value={fabula.proofRequirements.join('\n')}
            onChange={(event) => onChange({ ...fabula, proofRequirements: splitLines(event.target.value) })}
          />
        </label>
        <label>
          Правила
          <textarea value={fabula.rules.join('\n')} onChange={(event) => onChange({ ...fabula, rules: splitLines(event.target.value) })} />
        </label>
      </div>
      <div className="inline-actions">
        <button className="btn btn-sec btn-sm" type="button" onClick={onCancel}>
          Отменить
        </button>
        <button className="btn btn-pri btn-sm" type="button" onClick={onSave} disabled={!fabula.title.trim()}>
          Сохранить
        </button>
      </div>
    </div>
  );
}
