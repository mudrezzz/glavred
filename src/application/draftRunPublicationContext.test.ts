import { describe, expect, it } from 'vitest';
import { createDemoWorkspace } from '../fixtures/demoWorkspace';
import { buildPublicationSizeContext } from './draftRunPublicationContext';

describe('buildPublicationSizeContext', () => {
  it('uses slot profile before default settings profile', () => {
    const workspace = createDemoWorkspace();
    const planSlot = {
      ...workspace.contentPlanItems[0],
      publicationSizeProfileId: 'linkedin-article',
      platform: 'LinkedIn'
    };
    const context = buildPublicationSizeContext(workspace, null, planSlot, workspace.fabulas[0]);

    expect(context.slotProfileId).toBe('linkedin-article');
    expect((context.selectedProfile as { id: string }).id).toBe('linkedin-article');
  });

  it('sends fabula scale intent separately from platform profile', () => {
    const workspace = createDemoWorkspace();
    const context = buildPublicationSizeContext(workspace, null, workspace.contentPlanItems[0], {
      ...workspace.fabulas[0],
      sizeIntent: 'deep'
    });

    expect(context.fabulaSizeIntent).toBe('deep');
    expect(context.platform).toBe('Telegram');
  });
});
