import { useState, type FormEvent } from 'react';
import type { ContextChatActionType, ContextChatMessage, ContextChatScope, ContextChatSuggestion } from '../application/contextChat';
import { Icon } from '../shared/ui/Icon';
import { contextChatActionLabel, contextChatRoleLabel, contextChatScopeLabel, type ContextChatTab } from './contextChatScope';

export function ContextChatOverlay({
  activeTab,
  messages,
  open,
  scope,
  suggestions,
  onAcceptSuggestion,
  onClose,
  onDismissSuggestion,
  onSendMessage,
  onSwitchTab
}: {
  activeTab: ContextChatTab;
  messages: ContextChatMessage[];
  open: boolean;
  scope: ContextChatScope;
  suggestions: ContextChatSuggestion[];
  onAcceptSuggestion: (suggestion: ContextChatSuggestion) => void;
  onClose: () => void;
  onDismissSuggestion: (suggestionId: string) => void;
  onSendMessage: (message: string) => void;
  onSwitchTab: (tab: ContextChatTab) => void;
}) {
  const [draft, setDraft] = useState('');

  if (!open) return null;

  function submitMessage(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const text = draft.trim();
    if (!text) return;
    onSendMessage(text);
    setDraft('');
  }

  return (
    <aside
      className={`context-chat-drawer scope-${scope}`}
      data-testid="context-chat-drawer"
      aria-label="Контекстный помощник"
    >
      <div className="context-chat-head">
        <div>
          <span className="mono-label">Context chat</span>
          <h3>Помощник раздела</h3>
          <p>{contextChatScopeLabel(scope)}</p>
        </div>
        <div className="context-chat-head-actions">
          <button className="icon-btn" type="button" aria-label="Закрыть помощника" onClick={onClose}>
            <Icon name="close" size={16} />
          </button>
        </div>
      </div>
      <div className="context-chat-tabs tabs" role="tablist" aria-label="Режим помощника">
        <button
          className={`tab${activeTab === 'chat' ? ' active' : ''}`}
          role="tab"
          type="button"
          aria-selected={activeTab === 'chat'}
          onClick={() => onSwitchTab('chat')}
        >
          Чат
        </button>
        <button
          className={`tab${activeTab === 'suggestions' ? ' active' : ''}`}
          role="tab"
          type="button"
          aria-selected={activeTab === 'suggestions'}
          onClick={() => onSwitchTab('suggestions')}
        >
          Подсказки
          <span className="assistant-count">{suggestions.length}</span>
        </button>
      </div>
      {activeTab === 'chat' ? (
        <div className="context-chat-mode">
          <div className="context-chat-thread">
            {messages.map((message) => (
              <article className={`context-message ${message.role}`} key={message.id}>
                <span>{contextChatRoleLabel(message.role)}</span>
                <p>{message.text}</p>
                {message.suggestion && message.suggestion.actionType !== 'readOnly' ? (
                  <button
                    className="btn btn-pri btn-sm"
                    type="button"
                    onClick={() => onAcceptSuggestion(message.suggestion as ContextChatSuggestion)}
                  >
                    {contextChatActionLabel(message.suggestion.actionType)}
                  </button>
                ) : null}
              </article>
            ))}
          </div>
          <form className="context-chat-input" onSubmit={submitMessage}>
            <textarea
              aria-label="Сообщение помощнику"
              value={draft}
              onChange={(event) => setDraft(event.target.value)}
              placeholder="Спросите по текущему разделу или попросите сгенерировать тему..."
              rows={3}
            />
            <button className="btn btn-pri btn-sm" type="submit" disabled={!draft.trim()}>
              Отправить
            </button>
          </form>
        </div>
      ) : (
        <div className="context-chat-suggestions">
          {suggestions.length === 0 ? (
            <p className="context-empty">Новых подсказок нет. Можно вернуться в чат и задать вопрос по разделу.</p>
          ) : null}
          {suggestions.map((suggestion) => (
            <article className="context-suggestion" key={suggestion.id}>
              <button
                className="context-suggestion-dismiss"
                type="button"
                aria-label={`Скрыть подсказку: ${suggestion.title}`}
                onClick={() => onDismissSuggestion(suggestion.id)}
              >
                <Icon name="close" size={14} />
              </button>
              <div>
                <h4>{suggestion.title}</h4>
                <p>{suggestion.body}</p>
              </div>
              {suggestion.actionType !== 'readOnly' ? (
                <button className="btn btn-pri btn-sm" type="button" onClick={() => onAcceptSuggestion(suggestion)}>
                  {contextChatActionLabel(suggestion.actionType)}
                </button>
              ) : null}
            </article>
          ))}
        </div>
      )}
    </aside>
  );
}

