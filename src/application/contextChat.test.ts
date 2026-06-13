import { describe, expect, it } from 'vitest';
import { createContextChatReply, createContextChatSuggestions } from './contextChat';
import { createDemoWorkspace } from '../fixtures/demoWorkspace';
import { createEditorialValidationRun } from '../domain/editorialWorkspace';

describe('context chat suggestions', () => {
  it('creates deterministic editorial setup suggestions from validator context', () => {
    const workspace = createDemoWorkspace();
    const validationRun = createEditorialValidationRun(workspace, '2026-06-12T10:00:00.000Z');
    const suggestions = createContextChatSuggestions({ ...workspace, editorialValidationRun: validationRun }, 'editorialPublisher');

    expect(suggestions.some((suggestion) => suggestion.actionType === 'addEditorialRule')).toBe(true);
    expect(suggestions[0].body).toContain('Последняя проверка');
  });

  it('creates safe draft actions for topics and fabulas', () => {
    const workspace = createDemoWorkspace();

    const topicSuggestions = createContextChatSuggestions(workspace, 'topics');
    const fabulaSuggestions = createContextChatSuggestions(workspace, 'fabulas');

    expect(topicSuggestions[0]).toMatchObject({
      actionType: 'addTopic',
      payload: expect.objectContaining({ title: 'AI trust onboarding' })
    });
    expect(fabulaSuggestions[0]).toMatchObject({
      actionType: 'addFabula',
      payload: expect.objectContaining({ title: 'Postmortem внедрения' })
    });
  });

  it('turns chat generation requests into safe draft actions', () => {
    const workspace = createDemoWorkspace();

    const reply = createContextChatReply(workspace, 'editorialPublisher', 'Сгенерируй темы по настройкам');

    expect(reply.text).toContain('черновик');
    expect(reply.suggestion).toMatchObject({
      actionType: 'addTopic',
      payload: expect.objectContaining({ title: 'AI rollout risk' })
    });
  });
});
