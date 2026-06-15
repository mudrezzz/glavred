import { useMemo, useState } from 'react';
import {
  createContextChatReply,
  createContextChatSuggestions,
  createInitialContextChatMessages,
  type AddEditorialRulePayload,
  type AddFabulaPayload,
  type AddTopicPayload,
  type ContextChatIntent,
  type ContextChatMessage,
  type ContextChatSuggestion
} from '../application/contextChat';
import {
  createEditorialValidationRun,
  type WorkspaceSection,
  type WorkspaceState
} from '../domain/editorialWorkspace';
import type { MemoryInternalTab } from '../features/author-memory/types';
import type { EditorialModelTab } from '../features/editorial-model/types';
import {
  getContextChatScope,
  type ContextChatTab
} from './contextChatScope';
import type { WorkspaceSetter } from './useWorkspacePersistence';

type ContextChatControllerParams = {
  active: WorkspaceSection;
  editorialModelTab: EditorialModelTab;
  memoryTab: MemoryInternalTab;
  setEditorialModelTab: (tab: EditorialModelTab) => void;
  setToast: (message: string) => void;
  setWorkspace: WorkspaceSetter;
  workspace: WorkspaceState;
};

export function useContextChatController({
  active,
  editorialModelTab,
  memoryTab,
  setEditorialModelTab,
  setToast,
  setWorkspace,
  workspace
}: ContextChatControllerParams) {
  const [contextChatOpen, setContextChatOpen] = useState(false);
  const [contextChatTab, setContextChatTab] = useState<ContextChatTab>('chat');
  const [contextChatMessages, setContextChatMessages] = useState<ContextChatMessage[]>(() =>
    createInitialContextChatMessages('memory')
  );
  const [contextChatIntent, setContextChatIntent] = useState<ContextChatIntent | null>(null);
  const [dismissedContextSuggestionIds, setDismissedContextSuggestionIds] = useState<string[]>([]);

  const contextChatScope = getContextChatScope(active, memoryTab, editorialModelTab);
  const contextChatSuggestions = useMemo(
    () => createContextChatSuggestions(workspace, contextChatScope),
    [workspace, contextChatScope]
  );
  const visibleContextChatSuggestions = useMemo(
    () => contextChatSuggestions.filter((suggestion) => !dismissedContextSuggestionIds.includes(suggestion.id)),
    [contextChatSuggestions, dismissedContextSuggestionIds]
  );

  function openContextChat(tab: ContextChatTab = 'chat') {
    setContextChatTab(tab);
    setContextChatOpen(true);
  }

  function resetContextChat() {
    setContextChatOpen(false);
    setContextChatTab('chat');
    setContextChatMessages(createInitialContextChatMessages('memory'));
    setContextChatIntent(null);
    setDismissedContextSuggestionIds([]);
  }

  function sendContextChatMessage(text: string) {
    const createdAt = new Date().toISOString();
    const reply = createContextChatReply(workspace, contextChatScope, text);
    setContextChatMessages((messages) => [
      ...messages,
      { id: `ctx-author-free-${createdAt}`, role: 'author', text, createdAt },
      {
        id: `ctx-assistant-free-${createdAt}`,
        role: 'assistant',
        text: reply.text,
        createdAt,
        suggestion: reply.suggestion
      }
    ]);
  }

  function dismissContextChatSuggestion(suggestionId: string) {
    setDismissedContextSuggestionIds((ids) => (ids.includes(suggestionId) ? ids : [...ids, suggestionId]));
  }

  function acceptContextChatSuggestion(suggestion: ContextChatSuggestion) {
    const createdAt = new Date().toISOString();
    setContextChatMessages((messages) => [
      ...messages,
      {
        id: `ctx-author-${suggestion.id}-${createdAt}`,
        role: 'author',
        text: `Принять: ${suggestion.title}`,
        createdAt,
        suggestionId: suggestion.id
      }
    ]);

    if (suggestion.actionType === 'runValidation') {
      setWorkspace((current) => {
        const checkedAt = new Date().toISOString();
        return {
          ...current,
          activeSection: 'editorialModel',
          editorialValidationRun: createEditorialValidationRun(current, checkedAt),
          updatedAt: checkedAt
        };
      });
      setToast('Редакционная модель проверена');
      return;
    }

    if (suggestion.actionType === 'addEditorialRule' && suggestion.payload) {
      setWorkspace((current) => ({ ...current, activeSection: 'editorialModel' }));
      setEditorialModelTab('publisher');
      setContextChatIntent({
        id: `${suggestion.id}-${createdAt}`,
        actionType: 'addEditorialRule',
        payload: suggestion.payload as AddEditorialRulePayload
      });
      return;
    }

    if (suggestion.actionType === 'addTopic' && suggestion.payload) {
      setWorkspace((current) => ({ ...current, activeSection: 'editorialModel' }));
      setEditorialModelTab('topics');
      setContextChatIntent({
        id: `${suggestion.id}-${createdAt}`,
        actionType: 'addTopic',
        payload: suggestion.payload as AddTopicPayload
      });
      return;
    }

    if (suggestion.actionType === 'addFabula' && suggestion.payload) {
      setWorkspace((current) => ({ ...current, activeSection: 'editorialModel' }));
      setEditorialModelTab('fabulas');
      setContextChatIntent({
        id: `${suggestion.id}-${createdAt}`,
        actionType: 'addFabula',
        payload: suggestion.payload as AddFabulaPayload
      });
      return;
    }

    setContextChatMessages((messages) => [
      ...messages,
      {
        id: `ctx-assistant-${suggestion.id}-${createdAt}`,
        role: 'assistant',
        text: 'Эта подсказка пока только для чтения. В следующих слайсах я смогу переводить больше рекомендаций в структурные изменения.',
        createdAt,
        suggestionId: suggestion.id
      }
    ]);
  }

  return {
    acceptContextChatSuggestion,
    contextChatIntent,
    contextChatMessages,
    contextChatOpen,
    contextChatScope,
    contextChatTab,
    dismissContextChatSuggestion,
    openContextChat,
    resetContextChat,
    sendContextChatMessage,
    setContextChatIntent,
    setContextChatOpen,
    setContextChatTab,
    visibleContextChatSuggestions
  };
}
