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

export function TopicFabulaMatrixView({
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
