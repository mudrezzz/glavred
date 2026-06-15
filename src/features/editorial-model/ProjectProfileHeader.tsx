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

export function ProjectProfileHeader({
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
