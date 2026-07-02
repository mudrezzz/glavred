import { describe, expect, it } from 'vitest';
import {
  createPublicationChannel,
  applyPublicationChannelToPlanItem,
  applyPublicationChannelToSettings,
  canDeletePublicationChannel,
  normalizePublicationChannels,
  resolveDefaultPublicationChannel,
  resolvePlanItemPublicationChannel
} from './transitions';
import { DEFAULT_CONTENT_PLAN_SETTINGS, type ContentPlanItem } from '../editorialWorkspace';

describe('publication channel transitions', () => {
  it('normalizes a legacy workspace into one active manual channel from default platform', () => {
    const channels = normalizePublicationChannels(undefined, 'LinkedIn', 'en', 'linkedin-article');

    expect(channels).toHaveLength(1);
    expect(channels[0]).toMatchObject({
      platform: 'linkedin',
      title: 'LinkedIn',
      language: 'en',
      publishingMode: 'manual',
      status: 'active',
      defaultPublicationSizeProfileId: 'linkedin-article'
    });
  });

  it('resolves default channel and preserves legacy defaultPlatform label', () => {
    const channels = normalizePublicationChannels(undefined, 'Telegram');
    const settings = applyPublicationChannelToSettings(DEFAULT_CONTENT_PLAN_SETTINGS, channels[0]);

    expect(resolveDefaultPublicationChannel(settings, channels)?.id).toBe(channels[0].id);
    expect(settings.defaultChannelId).toBe(channels[0].id);
    expect(settings.defaultPlatform).toBe('Telegram');
  });

  it('maps plan items by channel id or legacy platform label', () => {
    const channels = normalizePublicationChannels(undefined, 'Telegram');
    const item = planItem({ platform: 'Telegram' });
    const resolved = resolvePlanItemPublicationChannel(item, channels);

    expect(resolved?.id).toBe(channels[0].id);
    expect(applyPublicationChannelToPlanItem(item, channels[0])).toMatchObject({
      channelId: channels[0].id,
      platform: channels[0].title
    });
  });

  it('keeps legacy channel audience readable but omits it from new channels', () => {
    const legacy = createPublicationChannel({
      title: 'Telegram',
      audience: 'Legacy channel audience'
    });
    const current = normalizePublicationChannels(undefined, 'Telegram');

    expect(legacy.audience).toBe('Legacy channel audience');
    expect(current[0].audience).toBeUndefined();
  });

  it('does not delete referenced channels', () => {
    const channels = normalizePublicationChannels(undefined, 'Telegram');

    expect(canDeletePublicationChannel(channels[0].id, [planItem({ channelId: channels[0].id })])).toBe(false);
    expect(canDeletePublicationChannel(channels[0].id, [planItem({ channelId: 'other' })])).toBe(true);
  });
});

function planItem(patch: Partial<ContentPlanItem>): ContentPlanItem {
  return {
    id: 'slot-1',
    insightId: 'insight-1',
    title: 'Slot',
    platform: 'Telegram',
    date: '2026-07-01',
    time: '10:00',
    priority: 'normal',
    format: 'post',
    expectedEffect: 'effect',
    approvalStatus: 'draft',
    manualOverride: false,
    weightWarningIds: [],
    ...patch
  };
}
