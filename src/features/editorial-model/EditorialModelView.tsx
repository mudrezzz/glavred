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
import { FabulaListView, ProjectProfileHeader, PublisherRulesView, TopicFabulaMatrixView, TopicListView } from './EditorialModelParts';


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
