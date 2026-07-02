import type { ContentPlanItem, ContentPlanSettings } from '../planning/types';
import type {
  PublicationChannel,
  PublicationChannelPublishingMode,
  PublicationChannelRole,
  PublicationChannelStatus,
  PublicationChannelValidationResult,
  PublicationPlatform
} from './types';

const VALID_PLATFORMS: PublicationPlatform[] = ['telegram', 'linkedin', 'dzen', 'site', 'other'];
const VALID_ROLES: PublicationChannelRole[] = ['primary', 'repurpose', 'experiment', 'archive'];
const VALID_MODES: PublicationChannelPublishingMode[] = ['manual', 'adapterPlanned', 'connected'];
const VALID_STATUSES: PublicationChannelStatus[] = ['active', 'paused'];

export const PUBLICATION_PLATFORM_LABELS: Record<PublicationPlatform, string> = {
  telegram: 'Telegram',
  linkedin: 'LinkedIn',
  dzen: 'Дзен',
  site: 'Сайт',
  other: 'Другое'
};

export function createPublicationChannel(input: Partial<PublicationChannel> & { title: string }): PublicationChannel {
  const platform = normalizePublicationPlatform(input.platform ?? input.title);
  const audience = normalizeText(input.audience, '');
  return {
    id: input.id ?? `channel-${slugify(input.title || PUBLICATION_PLATFORM_LABELS[platform])}`,
    projectId: input.projectId ?? 'local-project',
    platform,
    title: normalizeText(input.title, PUBLICATION_PLATFORM_LABELS[platform]),
    handleOrUrl: normalizeText(input.handleOrUrl, ''),
    language: normalizeText(input.language, 'ru'),
    ...(audience ? { audience } : {}),
    role: VALID_ROLES.includes(input.role as PublicationChannelRole) ? input.role as PublicationChannelRole : 'primary',
    publishingMode: VALID_MODES.includes(input.publishingMode as PublicationChannelPublishingMode)
      ? input.publishingMode as PublicationChannelPublishingMode
      : 'manual',
    status: VALID_STATUSES.includes(input.status as PublicationChannelStatus)
      ? input.status as PublicationChannelStatus
      : 'active',
    defaultPublicationSizeProfileId: input.defaultPublicationSizeProfileId || undefined
  };
}

export function normalizePublicationChannels(
  saved: PublicationChannel[] | null | undefined,
  fallbackPlatform: string,
  fallbackLanguage = 'ru',
  fallbackSizeProfileId?: string
): PublicationChannel[] {
  const normalized = (saved ?? [])
    .map((channel) => createPublicationChannel(channel))
    .filter((channel, index, channels) => channels.findIndex((item) => item.id === channel.id) === index);

  if (normalized.length > 0) return normalized;

  const platform = normalizeText(fallbackPlatform, 'Telegram');
  return [
    createPublicationChannel({
      id: `channel-${slugify(platform)}`,
      title: platform,
      platform: normalizePublicationPlatform(platform),
      language: fallbackLanguage,
      defaultPublicationSizeProfileId: fallbackSizeProfileId
    })
  ];
}

export function validatePublicationChannels(channels: PublicationChannel[]): PublicationChannelValidationResult {
  const messages: string[] = [];
  channels.forEach((channel) => {
    if (!channel.title.trim()) messages.push(`Канал ${channel.id}: нужен заголовок.`);
    if (!VALID_PLATFORMS.includes(channel.platform)) messages.push(`Канал ${channel.title}: неизвестная платформа.`);
    if (!channel.language.trim()) messages.push(`Канал ${channel.title}: нужен язык.`);
  });
  if (!channels.some((channel) => channel.status === 'active')) {
    messages.push('Рекомендуется иметь хотя бы один активный канал публикации.');
  }

  return {
    status: messages.some((message) => message.includes('нужен') || message.includes('неизвестная')) ? 'critical' : messages.length > 0 ? 'warning' : 'ok',
    messages
  };
}

export function resolveDefaultPublicationChannel(
  settings: ContentPlanSettings,
  channels: PublicationChannel[]
): PublicationChannel | null {
  const byId = settings.defaultChannelId ? channels.find((channel) => channel.id === settings.defaultChannelId) : null;
  if (byId) return byId;
  const byPlatformLabel = channels.find((channel) => channel.title === settings.defaultPlatform) ??
    channels.find((channel) => PUBLICATION_PLATFORM_LABELS[channel.platform] === settings.defaultPlatform);
  if (byPlatformLabel) return byPlatformLabel;
  return channels.find((channel) => channel.status === 'active') ?? channels[0] ?? null;
}

export function applyPublicationChannelToSettings(
  settings: ContentPlanSettings,
  channel: PublicationChannel | null
): ContentPlanSettings {
  if (!channel) return settings;
  return {
    ...settings,
    defaultChannelId: channel.id,
    defaultPlatform: channel.title,
    defaultPublicationSizeProfileId: channel.defaultPublicationSizeProfileId ?? settings.defaultPublicationSizeProfileId
  };
}

export function resolvePlanItemPublicationChannel(
  item: Pick<ContentPlanItem, 'channelId' | 'platform'>,
  channels: PublicationChannel[]
): PublicationChannel | null {
  if (item.channelId) {
    const byId = channels.find((channel) => channel.id === item.channelId);
    if (byId) return byId;
  }
  const platform = normalizeText(item.platform, '');
  if (!platform) return null;
  return channels.find((channel) => channel.title === platform) ??
    channels.find((channel) => PUBLICATION_PLATFORM_LABELS[channel.platform] === platform) ??
    null;
}

export function applyPublicationChannelToPlanItem(
  item: ContentPlanItem,
  channel: PublicationChannel
): ContentPlanItem {
  return {
    ...item,
    channelId: channel.id,
    platform: channel.title,
    publicationSizeProfileId: channel.defaultPublicationSizeProfileId ?? item.publicationSizeProfileId
  };
}

export function canDeletePublicationChannel(channelId: string, items: ContentPlanItem[]): boolean {
  return !items.some((item) => item.channelId === channelId);
}

export function publicationChannelLabel(channel: PublicationChannel): string {
  return `${channel.title} · ${PUBLICATION_PLATFORM_LABELS[channel.platform]}`;
}

export function normalizePublicationPlatform(value: string | undefined): PublicationPlatform {
  const normalized = (value ?? '').toLowerCase();
  if (normalized.includes('telegram') || normalized.includes('tg')) return 'telegram';
  if (normalized.includes('linkedin')) return 'linkedin';
  if (normalized.includes('dzen') || normalized.includes('дзен')) return 'dzen';
  if (normalized.includes('site') || normalized.includes('сайт') || normalized.includes('blog')) return 'site';
  return VALID_PLATFORMS.includes(normalized as PublicationPlatform) ? normalized as PublicationPlatform : 'other';
}

function normalizeText(value: string | undefined, fallback: string): string {
  return typeof value === 'string' && value.trim() ? value.trim() : fallback;
}

function slugify(value: string): string {
  const ascii = value
    .toLowerCase()
    .replace(/[^a-z0-9а-яё]+/gi, '-')
    .replace(/^-+|-+$/g, '');
  return ascii || 'publication';
}
