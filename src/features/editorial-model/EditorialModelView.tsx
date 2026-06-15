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
  validatorDefinitionTitle,
  type EditorialModel,
  type EditorialRule,
  type EditorialRuleGroup,
  type EditorialValidationRun,
  type Fabula,
  type ProjectProfile,
  type Topic,
  type TopicFabulaMatrixEntry,
  type ValidatorResult,
  type WorkspaceState
} from '../../domain/editorialWorkspace';
import { WeightRangeEditor } from '../../shared/ui/WeightRangeEditor';
import type { EditorialModelTab } from './types';

const EDITORIAL_TABS: Array<[EditorialModelTab, string]> = [
  ['publisher', 'Издательство'],
  ['topics', 'Темы'],
  ['fabulas', 'Фабулы'],
  ['matrix', 'Матрица']
];

export function EditorialModelView({
  activeTab,
  chatIntent,
  workspace,
  projectProfile,
  editorialRules,
  topics,
  fabulas,
  matrix,
  onProjectProfileChange,
  onEditorialRulesChange,
  onTopicsChange,
  onFabulasChange,
  onMatrixChange,
  onTopicsAndMatrixChange,
  onFabulasAndMatrixChange,
  onChangeTab,
  onChatIntentConsumed,
  onRunValidation
}: {
  activeTab: EditorialModelTab;
  chatIntent: ContextChatIntent | null;
  workspace: WorkspaceState;
  model: EditorialModel;
  projectProfile: ProjectProfile;
  editorialRules: EditorialRule[];
  topics: Topic[];
  fabulas: Fabula[];
  matrix: TopicFabulaMatrixEntry[];
  onModelChange: (model: EditorialModel) => void;
  onProjectProfileChange: (profile: ProjectProfile) => void;
  onEditorialRulesChange: (rules: EditorialRule[]) => void;
  onTopicsChange: (topics: Topic[]) => void;
  onFabulasChange: (fabulas: Fabula[]) => void;
  onMatrixChange: (matrix: TopicFabulaMatrixEntry[]) => void;
  onTopicsAndMatrixChange: (topics: Topic[], matrix: TopicFabulaMatrixEntry[]) => void;
  onFabulasAndMatrixChange: (fabulas: Fabula[], matrix: TopicFabulaMatrixEntry[]) => void;
  onChangeTab: (tab: EditorialModelTab) => void;
  onChatIntentConsumed: () => void;
  onRunValidation: () => void;
}) {
  const tab = activeTab;
  const setTab = onChangeTab;
  const warnings = getTopicFabulaWarnings(topics, fabulas, matrix);
  const enabledPairs = matrix.filter((entry) => entry.enabled).length;

  function saveRule(rule: EditorialRule) {
    const exists = editorialRules.some((item) => item.id === rule.id);
    onEditorialRulesChange(exists ? updateEditorialRule(editorialRules, rule) : [rule, ...editorialRules]);
  }

  function removeRule(ruleId: string) {
    onEditorialRulesChange(deleteEditorialRule(editorialRules, ruleId));
  }

  function updateTopic(topic: Topic) {
    onTopicsChange(topics.map((item) => (item.id === topic.id ? topic : item)));
  }

  function createTopic(topic: Topic) {
    const nextTopics = addTopic(topics, topic);
    onTopicsAndMatrixChange(nextTopics, completeTopicFabulaMatrix(nextTopics, fabulas, matrix));
  }

  function removeTopic(topicId: string) {
    const result = deleteTopic(topics, matrix, topicId);
    onTopicsAndMatrixChange(result.topics, result.matrix);
  }

  function updateFabula(fabula: Fabula) {
    onFabulasChange(fabulas.map((item) => (item.id === fabula.id ? fabula : item)));
  }

  function createFabula(fabula: Fabula) {
    const nextFabulas = addFabula(fabulas, fabula);
    onFabulasAndMatrixChange(nextFabulas, completeTopicFabulaMatrix(topics, nextFabulas, matrix));
  }

  function removeFabula(fabulaId: string) {
    const result = deleteFabula(fabulas, matrix, fabulaId);
    onFabulasAndMatrixChange(result.fabulas, result.matrix);
  }

  return (
    <div className="page wide fade-up">
      <ProjectProfileHeader
        enabledPairs={enabledPairs}
        fabulaCount={fabulas.length}
        profile={projectProfile}
        topicCount={topics.length}
        warningCount={warnings.length}
        onSave={onProjectProfileChange}
      />
      <div className="tabs memory-tabs model-tabs" role="tablist" aria-label="Редакционная модель">
        {EDITORIAL_TABS.map(([id, label]) => (
          <button
            aria-selected={tab === id}
            className={`tab${tab === id ? ' active' : ''}`}
            key={id}
            role="tab"
            type="button"
            onClick={() => setTab(id)}
          >
            {label}
          </button>
        ))}
      </div>
      <div className="editorial-workspace">
        <div className="editorial-main">
          {tab === 'publisher' ? (
            <PublisherRulesView
              chatIntent={chatIntent?.actionType === 'addEditorialRule' ? chatIntent : null}
              rules={editorialRules}
              onChatIntentConsumed={onChatIntentConsumed}
              onDelete={removeRule}
              onSave={saveRule}
            />
          ) : null}
          {tab === 'topics' ? (
            <TopicListView
              chatIntent={chatIntent?.actionType === 'addTopic' ? chatIntent : null}
              fabulas={fabulas}
              matrix={matrix}
              referencedTopicIds={getReferencedTopicIds(workspace)}
              topics={topics}
              onCreate={createTopic}
              onChatIntentConsumed={onChatIntentConsumed}
              onDelete={removeTopic}
              onSave={updateTopic}
            />
          ) : null}
          {tab === 'fabulas' ? (
            <FabulaListView
              chatIntent={chatIntent?.actionType === 'addFabula' ? chatIntent : null}
              fabulas={fabulas}
              matrix={matrix}
              referencedFabulaIds={getReferencedFabulaIds(workspace)}
              topics={topics}
              onCreate={createFabula}
              onChatIntentConsumed={onChatIntentConsumed}
              onDelete={removeFabula}
              onSave={updateFabula}
            />
          ) : null}
          {tab === 'matrix' ? (
            <TopicFabulaMatrixView fabulas={fabulas} matrix={matrix} topics={topics} onSave={onMatrixChange} />
          ) : null}
        </div>
        <EditorialValidationPanel
          activeTab={tab}
          currentRevision={workspace.editorialSetupRevision ?? 0}
          validationRun={workspace.editorialValidationRun}
          onRunValidation={onRunValidation}
        />
      </div>
    </div>
  );
}

const RULE_SECTIONS: Array<{ title: string; description: string; groups: EditorialRuleGroup[] }> = [
  {
    title: 'Автор',
    description: 'Характеристики образа автора, которые потом должны проверяться в тексте.',
    groups: ['author']
  },
  {
    title: 'Аудитория',
    description: 'Кому пишем и какую пользу читатель должен получать.',
    groups: ['audience']
  },
  {
    title: 'Позиция',
    description: 'Что автор утверждает, с чем спорит и какую оптику удерживает.',
    groups: ['positioning']
  },
  {
    title: 'Стиль',
    description: 'Голос, язык, ритм, anti-AI-паттерны и запрещенные формулировки.',
    groups: ['styleVoice', 'styleLanguage', 'styleRhythm', 'antiAiPattern']
  },
  {
    title: 'Цели',
    description: 'Зачем существует блог и что должно поддерживаться каждым выпуском.',
    groups: ['goal']
  },
  {
    title: 'Запреты',
    description: 'Темы, углы и обещания, которые нельзя протаскивать в публикации.',
    groups: ['forbiddenTopic']
  }
];

function ProjectProfileHeader({
  profile,
  topicCount,
  fabulaCount,
  enabledPairs,
  warningCount,
  onSave
}: {
  profile: ProjectProfile;
  topicCount: number;
  fabulaCount: number;
  enabledPairs: number;
  warningCount: number;
  onSave: (profile: ProjectProfile) => void;
}) {
  const [editing, setEditing] = useState(false);
  const [draft, setDraft] = useState(profile);

  useEffect(() => {
    if (!editing) setDraft(profile);
  }, [editing, profile]);

  function save() {
    onSave(draft);
    setEditing(false);
  }

  return (
    <section className="card project-profile-header">
      <div className="project-profile-main">
        <span className="mono-label">Проект</span>
        {editing ? (
          <div className="profile-edit-grid">
            <label>
              Название
              <input value={draft.name} onChange={(event) => setDraft({ ...draft, name: event.target.value })} />
            </label>
            <label>
              Описание
              <textarea
                value={draft.description}
                onChange={(event) => setDraft({ ...draft, description: event.target.value })}
              />
            </label>
            <label>
              Статус настройки
              <select
                value={draft.setupStatus}
                onChange={(event) =>
                  setDraft({ ...draft, setupStatus: event.target.value as ProjectProfile['setupStatus'] })
                }
              >
                <option value="draft">Черновик</option>
                <option value="needsReview">Нужна проверка</option>
                <option value="validated">Проверено</option>
              </select>
            </label>
          </div>
        ) : (
          <>
            <h2>{profile.name}</h2>
            <p>{profile.description}</p>
          </>
        )}
      </div>
      <div className="project-profile-meta">
        <div>
          <b>{topicCount}</b>
          <span>тем</span>
        </div>
        <div>
          <b>{fabulaCount}</b>
          <span>фабул</span>
        </div>
        <div>
          <b>{enabledPairs}</b>
          <span>активных связок</span>
        </div>
        <div className={warningCount > 0 ? 'warn' : 'ok'}>
          <b>{warningCount}</b>
          <span>предупреждений</span>
        </div>
      </div>
      <div className="inline-actions">
        {editing ? (
          <>
            <button className="btn btn-sec btn-sm" type="button" onClick={() => setEditing(false)}>
              Отменить
            </button>
            <button className="btn btn-pri btn-sm" type="button" onClick={save}>
              Сохранить
            </button>
          </>
        ) : (
          <button className="btn btn-sec btn-sm" type="button" onClick={() => setEditing(true)}>
            Редактировать проект
          </button>
        )}
      </div>
    </section>
  );
}

function PublisherRulesView({
  chatIntent,
  rules,
  onChatIntentConsumed,
  onSave,
  onDelete
}: {
  chatIntent: Extract<ContextChatIntent, { actionType: 'addEditorialRule' }> | null;
  rules: EditorialRule[];
  onChatIntentConsumed: () => void;
  onSave: (rule: EditorialRule) => void;
  onDelete: (ruleId: string) => void;
}) {
  return (
    <div className="rule-sections">
      {RULE_SECTIONS.map((section) => (
        <RuleSection
          chatIntent={chatIntent && section.groups.includes(chatIntent.payload.group) ? chatIntent : null}
          key={section.title}
          rules={rules}
          section={section}
          onChatIntentConsumed={onChatIntentConsumed}
          onDelete={onDelete}
          onSave={onSave}
        />
      ))}
    </div>
  );
}

function RuleSection({
  chatIntent,
  section,
  rules,
  onChatIntentConsumed,
  onSave,
  onDelete
}: {
  chatIntent: Extract<ContextChatIntent, { actionType: 'addEditorialRule' }> | null;
  section: { title: string; description: string; groups: EditorialRuleGroup[] };
  rules: EditorialRule[];
  onChatIntentConsumed: () => void;
  onSave: (rule: EditorialRule) => void;
  onDelete: (ruleId: string) => void;
}) {
  const sectionRules = rules.filter((rule) => section.groups.includes(rule.group));
  const [editingId, setEditingId] = useState<string | null>(null);
  const [draft, setDraft] = useState<EditorialRule | null>(null);

  function startAdd() {
    const group = section.groups[0];
    setEditingId('new');
    setDraft(createEditorialRule(group, '', ''));
  }

  useEffect(() => {
    if (!chatIntent) return;

    setEditingId('new');
    setDraft(createEditorialRule(chatIntent.payload.group, chatIntent.payload.title, chatIntent.payload.statement));
    onChatIntentConsumed();
  }, [chatIntent, onChatIntentConsumed]);

  function startEdit(rule: EditorialRule) {
    setEditingId(rule.id);
    setDraft({ ...rule });
  }

  function cancel() {
    setEditingId(null);
    setDraft(null);
  }

  function save() {
    if (!draft) return;
    onSave(draft);
    cancel();
  }

  return (
    <section className="card rule-section">
      <div className="rule-section-head">
        <div>
          <span className="mono-label">{section.title}</span>
          <p>{section.description}</p>
        </div>
        <button className="btn btn-sec btn-sm" type="button" onClick={startAdd}>
          + Правило
        </button>
      </div>
      <div className="rule-list">
        {editingId === 'new' && draft ? (
          <RuleEditor
            availableGroups={section.groups}
            rule={draft}
            onCancel={cancel}
            onChange={setDraft}
            onSave={save}
          />
        ) : null}
        {sectionRules.map((rule) =>
          editingId === rule.id && draft ? (
            <RuleEditor
              availableGroups={section.groups}
              key={rule.id}
              rule={draft}
              onCancel={cancel}
              onChange={setDraft}
              onSave={save}
            />
          ) : (
            <article className="rule-card" key={rule.id}>
              <div className="rule-card-main">
                <div className="rule-head">
                  <b>{rule.title}</b>
                  <span className={`status-chip ${rule.status}`}>{rule.status === 'active' ? 'активно' : 'пауза'}</span>
                </div>
                <p>{rule.statement}</p>
                <span className="sub">{editorialRuleGroupLabel(rule.group)}</span>
              </div>
              <div className="inline-actions">
                <button className="btn btn-sec btn-sm" type="button" onClick={() => startEdit(rule)}>
                  Редактировать
                </button>
                <button className="btn btn-sec btn-sm danger-text" type="button" onClick={() => onDelete(rule.id)}>
                  Удалить
                </button>
              </div>
            </article>
          )
        )}
        {sectionRules.length === 0 && editingId !== 'new' ? <EmptyState text="В этом блоке пока нет правил." /> : null}
      </div>
    </section>
  );
}

function RuleEditor({
  rule,
  availableGroups,
  onChange,
  onSave,
  onCancel
}: {
  rule: EditorialRule;
  availableGroups: EditorialRuleGroup[];
  onChange: (rule: EditorialRule) => void;
  onSave: () => void;
  onCancel: () => void;
}) {
  return (
    <article className="rule-card rule-edit">
      <label>
        Тип правила
        <select
          value={rule.group}
          onChange={(event) => onChange({ ...rule, group: event.target.value as EditorialRuleGroup })}
        >
          {availableGroups.map((group) => (
            <option key={group} value={group}>
              {editorialRuleGroupLabel(group)}
            </option>
          ))}
        </select>
      </label>
      <label>
        Название
        <input value={rule.title} onChange={(event) => onChange({ ...rule, title: event.target.value })} />
      </label>
      <label>
        Правило
        <textarea value={rule.statement} onChange={(event) => onChange({ ...rule, statement: event.target.value })} />
      </label>
      <label>
        Статус
        <select
          value={rule.status}
          onChange={(event) => onChange({ ...rule, status: event.target.value as EditorialRule['status'] })}
        >
          <option value="active">Активно</option>
          <option value="paused">Пауза</option>
        </select>
      </label>
      <div className="inline-actions">
        <button className="btn btn-sec btn-sm" type="button" onClick={onCancel}>
          Отменить
        </button>
        <button className="btn btn-pri btn-sm" type="button" onClick={onSave} disabled={!rule.title.trim() || !rule.statement.trim()}>
          Сохранить
        </button>
      </div>
    </article>
  );
}

function TopicListView({
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

function FabulaListView({
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

function TopicFabulaMatrixView({
  topics,
  fabulas,
  matrix,
  onSave
}: {
  topics: Topic[];
  fabulas: Fabula[];
  matrix: TopicFabulaMatrixEntry[];
  onSave: (matrix: TopicFabulaMatrixEntry[]) => void;
}) {
  const [draft, setDraft] = useState(matrix);
  const isDirty = !sameMatrix(draft, matrix);

  useEffect(() => {
    setDraft(matrix);
  }, [matrix]);

  function toggle(topicId: string, fabulaId: string) {
    setDraft((current) =>
      current.map((entry) =>
        entry.topicId === topicId && entry.fabulaId === fabulaId ? { ...entry, enabled: !entry.enabled } : entry
      )
    );
  }

  return (
    <section className="card matrix-card">
      <div className="matrix-head">
        <div>
          <h3>Матрица совместимости</h3>
          <p>Связки определяют, какие фабулы допустимы для каждой темы. Изменения применяются только после сохранения.</p>
        </div>
        <div className="matrix-actions">
          {isDirty ? <span className="dirty-note">Есть несохраненные изменения</span> : null}
          <button className="btn btn-sec btn-sm" type="button" onClick={() => setDraft(matrix)} disabled={!isDirty}>
            Отменить
          </button>
          <button className="btn btn-pri btn-sm" type="button" onClick={() => onSave(draft)} disabled={!isDirty}>
            Сохранить матрицу
          </button>
        </div>
      </div>
      <div className="matrix-scroll" data-testid="topic-fabula-matrix-scroll">
        <table className="matrix-table">
          <thead>
            <tr>
              <th className="matrix-sticky matrix-topic-head" scope="col">Тема</th>
              {fabulas.map((fabula) => (
                <th className="matrix-fabula-head" key={fabula.id} scope="col">{fabula.title}</th>
              ))}
            </tr>
          </thead>
          <tbody>
            {topics.map((topic) => (
              <tr key={topic.id}>
                <th className="matrix-sticky matrix-topic-cell" scope="row">{topic.title}</th>
                {fabulas.map((fabula) => {
                  const entry = draft.find((item) => item.topicId === topic.id && item.fabulaId === fabula.id);
                  return (
                    <td className="matrix-toggle-cell" key={fabula.id}>
                      <label className="matrix-check">
                        <input
                          aria-label={`${topic.title} · ${fabula.title}`}
                          checked={Boolean(entry?.enabled)}
                          type="checkbox"
                          onChange={() => toggle(topic.id, fabula.id)}
                        />
                      </label>
                    </td>
                  );
                })}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </section>
  );
}

function EditorialValidationPanel({
  validationRun,
  currentRevision,
  activeTab,
  onRunValidation
}: {
  validationRun: EditorialValidationRun | null;
  currentRevision: number;
  activeTab: EditorialModelTab;
  onRunValidation: () => void;
}) {
  const validation = validationRun?.summary ?? null;
  const validatorResults = validationRun?.results ?? [];
  const aggregateStatus = validationRun?.aggregateStatus ?? validation?.status ?? null;
  const aggregateScore = validationRun?.aggregateScore ?? 0;
  const isStale = Boolean(validationRun && validationRun.revision !== currentRevision);
  const runState = !validationRun ? 'Еще не проверено' : isStale ? 'Требует повторной проверки' : 'Проверено';

  return (
    <aside className="card validation-panel">
      <div className="validation-head">
        <span className="mono-label">Проверка</span>
        <span className={`validation-run-state ${!validationRun ? 'empty' : isStale ? 'stale' : 'fresh'}`}>
          {runState}
        </span>
        {aggregateStatus ? <ValidationBadge status={aggregateStatus} /> : null}
        <h3>{validation?.title ?? 'Проверка еще не запускалась'}</h3>
        <p>
          {validation
            ? validation.summary
            : 'Заполните или отредактируйте правила, темы, фабулы и матрицу, затем запустите проверку вручную.'}
        </p>
        {isStale ? (
          <p className="validation-stale-note">
            После последней проверки были сохранены изменения. Запустите проверку повторно, чтобы получить актуальный вывод.
          </p>
        ) : null}
        <button className="btn btn-pri btn-sm" type="button" onClick={onRunValidation}>
          Проверить
        </button>
      </div>
      {validation ? (
        <div className="validator-summary">
          <div>
            <span className="mono-label">Score</span>
            <strong>{Math.round(aggregateScore * 100)}%</strong>
          </div>
          <div>
            <span className="mono-label">Validators</span>
            <strong>{validatorResults.length || validation.items.length}</strong>
          </div>
        </div>
      ) : null}
      {validatorResults.length > 0 ? (
        <div className="validation-items validator-cards">
          {validatorResults.map((result) => (
            <ValidatorCard key={result.id} result={result} />
          ))}
        </div>
      ) : validation ? (
        <div className="validation-items">
          {validation.items.map((item) => (
            <article className="validation-item" key={item.id}>
              <div>
                <ValidationBadge status={item.status} />
                <b>{item.title}</b>
              </div>
              <p>{item.summary}</p>
              <small>{item.recommendation}</small>
            </article>
          ))}
        </div>
      ) : null}
      <p className="validation-note">
        Вкладка: {editorialTabLabel(activeTab)}. Проверка deterministic, без AI provider. Результат обновляется только по кнопке.
      </p>
      {validationRun ? <p className="validation-note">Последняя проверка: {formatDateTime(validationRun.checkedAt)}</p> : null}
    </aside>
  );
}

function ValidatorCard({ result }: { result: ValidatorResult }) {
  return (
    <article className="validation-item validator-card">
      <div className="validator-card-head">
        <ValidationBadge status={result.status} />
        <div>
          <b>{validatorDefinitionTitle(result.validatorId)}</b>
          <span>{result.validatorId}</span>
        </div>
        <strong>{Math.round(result.score * 100)}%</strong>
      </div>
      <p>{result.summary}</p>
      <details className="validator-details">
        <summary>Evidence и рекомендации</summary>
        <div className="validator-detail-block">
          <span className="mono-label">Evidence</span>
          {result.evidence.length > 0 ? (
            result.evidence.map((item) => (
              <blockquote key={item.id}>
                <b>{item.title}</b>
                <p>{item.quote}</p>
                <small>{item.reason}</small>
              </blockquote>
            ))
          ) : (
            <p className="muted-text">Evidence пока нет.</p>
          )}
        </div>
        <div className="validator-detail-block">
          <span className="mono-label">Suggestions</span>
          {result.suggestions.length > 0 ? (
            result.suggestions.map((item) => (
              <div className={`validator-suggestion ${item.severity}`} key={item.id}>
                <b>{item.title}</b>
                <p>{item.description}</p>
              </div>
            ))
          ) : (
            <p className="muted-text">Рекомендаций нет.</p>
          )}
        </div>
      </details>
    </article>
  );
}

function ValidationBadge({ status }: { status: 'green' | 'yellow' | 'red' }) {
  const label = status === 'green' ? 'ок' : status === 'yellow' ? 'внимание' : 'риск';
  return <span className={`validation-badge ${status}`}>{label}</span>;
}

function editorialRuleGroupLabel(group: EditorialRuleGroup): string {
  const labels: Record<EditorialRuleGroup, string> = {
    author: 'Образ автора',
    audience: 'Аудитория',
    positioning: 'Позиция',
    styleVoice: 'Голос',
    styleLanguage: 'Язык',
    styleRhythm: 'Ритм',
    antiAiPattern: 'Anti-AI',
    goal: 'Цель',
    forbiddenTopic: 'Запрет'
  };
  return labels[group];
}

function editorialTabLabel(tab: EditorialModelTab): string {
  if (tab === 'publisher') return 'Издательство';
  if (tab === 'topics') return 'Темы';
  if (tab === 'fabulas') return 'Фабулы';
  return 'Матрица';
}

function getReferencedTopicIds(workspace: WorkspaceState): Set<string> {
  return new Set(
    [workspace.insightCard?.topicId, workspace.contentPlanItem?.topicId, workspace.postBrief?.topicId].filter(
      Boolean
    ) as string[]
  );
}

function getReferencedFabulaIds(workspace: WorkspaceState): Set<string> {
  return new Set(
    [workspace.insightCard?.fabulaId, workspace.contentPlanItem?.fabulaId, workspace.postBrief?.fabulaId].filter(
      Boolean
    ) as string[]
  );
}

function countCompatibleFabulas(topicId: string, matrix: TopicFabulaMatrixEntry[]): number {
  return matrix.filter((entry) => entry.topicId === topicId && entry.enabled).length;
}

function countCompatibleTopics(fabulaId: string, matrix: TopicFabulaMatrixEntry[]): number {
  return matrix.filter((entry) => entry.fabulaId === fabulaId && entry.enabled).length;
}

function isMatrixEnabled(topicId: string, fabulaId: string, matrix: TopicFabulaMatrixEntry[]): boolean {
  return matrix.some((entry) => entry.topicId === topicId && entry.fabulaId === fabulaId && entry.enabled);
}

function sameMatrix(left: TopicFabulaMatrixEntry[], right: TopicFabulaMatrixEntry[]): boolean {
  if (left.length !== right.length) return false;
  return left.every((entry) => {
    const other = right.find((item) => item.topicId === entry.topicId && item.fabulaId === entry.fabulaId);
    return other ? other.enabled === entry.enabled : false;
  });
}
function EmptyState({ text }: { text: string }) {
  return <div className="card empty-state">{text}</div>;
}

function splitLines(value: string): string[] {
  return value
    .split('\n')
    .map((item) => item.trim())
    .filter(Boolean);
}

function formatDateTime(value: string): string {
  return new Date(value).toLocaleString('ru-RU', {
    day: '2-digit',
    month: '2-digit',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  });
}
