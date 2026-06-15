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

export function PublisherRulesView({
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

function EmptyState({ text }: { text: string }) {
  return <div className="card empty-state">{text}</div>;
}
