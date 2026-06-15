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

export function TopicListView({
  chatIntent,
  topics,
  fabulas,
  matrix,
  referencedTopicIds,
  onCreate,
  onChatIntentConsumed,
  onDelete,
  onSave
}: {
  chatIntent: Extract<ContextChatIntent, { actionType: 'addTopic' }> | null;
  topics: Topic[];
  fabulas: Fabula[];
  matrix: TopicFabulaMatrixEntry[];
  referencedTopicIds: Set<string>;
  onCreate: (topic: Topic) => void;
  onChatIntentConsumed: () => void;
  onDelete: (topicId: string) => void;
  onSave: (topic: Topic) => void;
}) {
  const [expandedId, setExpandedId] = useState<string | null>(topics[0]?.id ?? null);
  const [editingId, setEditingId] = useState<string | null>(null);
  const [draft, setDraft] = useState<Topic | null>(null);

  function startEdit(topic: Topic) {
    setExpandedId(topic.id);
    setEditingId(topic.id);
    setDraft({ ...topic, rules: [...topic.rules], forbiddenAngles: [...topic.forbiddenAngles] });
  }

  function startCreate() {
    if (editingId === 'new' && draft) {
      setExpandedId(draft.id);
      return;
    }

    const topic = createTopicDraft();
    setExpandedId(topic.id);
    setEditingId('new');
    setDraft(topic);
  }

  useEffect(() => {
    if (!chatIntent) return;

    const topic = {
      ...createTopicDraft(),
      ...chatIntent.payload,
      rules: chatIntent.payload.rules ? [...chatIntent.payload.rules] : [],
      forbiddenAngles: chatIntent.payload.forbiddenAngles ? [...chatIntent.payload.forbiddenAngles] : []
    };
    setExpandedId(topic.id);
    setEditingId('new');
    setDraft(topic);
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

  function remove(topic: Topic) {
    const hasProductionReferences = referencedTopicIds.has(topic.id);
    const message = hasProductionReferences
      ? `Тема "${topic.title}" уже используется в текущих производственных артефактах. Удаление уберет тему и ее связи в матрице, но не перепишет уже созданные инсайты, планы или фабулы постов. Удалить?`
      : `Удалить тему "${topic.title}" и все ее связи в матрице?`;

    if (!window.confirm(message)) return;

    onDelete(topic.id);
    if (expandedId === topic.id) setExpandedId(null);
    if (editingId === topic.id) {
      setEditingId(null);
      setDraft(null);
    }
  }

  return (
    <div className="entity-list">
      <div className="entity-list-toolbar">
        <span className="mono-label">{topics.length} тем</span>
        <button className="btn btn-sec btn-sm" type="button" onClick={startCreate}>
          + Тема
        </button>
      </div>
      {editingId === 'new' && draft ? (
        <article className="card entity-row">
          <div className="entity-row-main">
            <span className="entity-title-placeholder">{draft.title.trim() || 'Новая тема'}</span>
            <div className="entity-row-meta">
              <span className="entity-meta-chip">{draft.weightRange.min}-{draft.weightRange.max}%</span>
              <span className={`status-chip ${draft.status}`}>{draft.status === 'active' ? 'активно' : 'пауза'}</span>
              <span className="entity-meta-chip">{draft.rules.length} правил</span>
              <span className="entity-meta-chip">{fabulas.length} фабул</span>
            </div>
            <ValidationBadge status={draft.title.trim() ? 'green' : 'yellow'} />
          </div>
          <TopicEditor
            topic={draft}
            onCancel={() => {
              setEditingId(null);
              setDraft(null);
              setExpandedId(topics[0]?.id ?? null);
            }}
            onChange={setDraft}
            onSave={save}
          />
        </article>
      ) : null}
      {topics.map((topic) => {
        const compatibleCount = countCompatibleFabulas(topic.id, matrix);
        const isExpanded = expandedId === topic.id;
        const isEditing = editingId === topic.id && draft;
        return (
          <article className="card entity-row" key={topic.id}>
            <div className="entity-row-main">
              <button
                className="entity-title-button"
                type="button"
                onClick={() => setExpandedId(isExpanded ? null : topic.id)}
              >
                {topic.title}
              </button>
              <div className="entity-row-meta">
                <span className="entity-meta-chip">{topic.weightRange.min}-{topic.weightRange.max}%</span>
                <span className={`status-chip ${topic.status}`}>{topic.status === 'active' ? 'активно' : 'пауза'}</span>
                <span className="entity-meta-chip">{topic.rules.length} правил</span>
                <span className="entity-meta-chip">{compatibleCount} фабул</span>
              </div>
              <ValidationBadge status={compatibleCount > 0 ? 'green' : 'red'} />
            </div>
            {isExpanded ? (
              isEditing ? (
                <TopicEditor
                  topic={draft}
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
                    <p>{topic.description}</p>
                    <dl className="entity-detail-list">
                      <dt>Зачем</dt>
                      <dd>{topic.purpose}</dd>
                      <dt>Ценность</dt>
                      <dd>{topic.audienceValue}</dd>
                      <dt>Позиция автора</dt>
                      <dd>{topic.authorStance}</dd>
                      <dt>Правила</dt>
                      <dd>{topic.rules.join('; ')}</dd>
                      <dt>Запреты</dt>
                      <dd>{topic.forbiddenAngles.join('; ')}</dd>
                      <dt>Совместимые фабулы</dt>
                      <dd>{fabulas.filter((fabula) => isMatrixEnabled(topic.id, fabula.id, matrix)).map((fabula) => fabula.title).join(', ')}</dd>
                    </dl>
                  </div>
                  <div className="inline-actions">
                    <button className="btn btn-sec btn-sm" type="button" onClick={() => startEdit(topic)}>
                      Редактировать
                    </button>
                    <button className="btn btn-sec btn-sm danger-text" type="button" onClick={() => remove(topic)}>
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

function TopicEditor({
  topic,
  onChange,
  onSave,
  onCancel
}: {
  topic: Topic;
  onChange: (topic: Topic) => void;
  onSave: () => void;
  onCancel: () => void;
}) {
  return (
    <div className="entity-edit-form">
      <div className="entity-edit-scroll">
        <label>
          Название
          <input value={topic.title} onChange={(event) => onChange({ ...topic, title: event.target.value })} />
        </label>
        <label>
          Описание
          <textarea value={topic.description} onChange={(event) => onChange({ ...topic, description: event.target.value })} />
        </label>
        <label>
          Зачем эта тема
          <textarea value={topic.purpose} onChange={(event) => onChange({ ...topic, purpose: event.target.value })} />
        </label>
        <label>
          Ценность для аудитории
          <textarea value={topic.audienceValue} onChange={(event) => onChange({ ...topic, audienceValue: event.target.value })} />
        </label>
        <label>
          Позиция автора
          <textarea value={topic.authorStance} onChange={(event) => onChange({ ...topic, authorStance: event.target.value })} />
        </label>
        <WeightRangeEditor value={topic.weightRange} onChange={(weightRange) => onChange({ ...topic, weightRange })} />
        <label>
          Правила
          <textarea value={topic.rules.join('\n')} onChange={(event) => onChange({ ...topic, rules: splitLines(event.target.value) })} />
        </label>
        <label>
          Запреты
          <textarea
            value={topic.forbiddenAngles.join('\n')}
            onChange={(event) => onChange({ ...topic, forbiddenAngles: splitLines(event.target.value) })}
          />
        </label>
      </div>
      <div className="inline-actions">
        <button className="btn btn-sec btn-sm" type="button" onClick={onCancel}>
          Отменить
        </button>
        <button className="btn btn-pri btn-sm" type="button" onClick={onSave} disabled={!topic.title.trim()}>
          Сохранить
        </button>
      </div>
    </div>
  );
}
