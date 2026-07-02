import { useMemo, useState } from 'react';
import type { ContentPlanItem, ContentPlanSettings } from '../../domain/editorialWorkspace';
import type { PublicationChannel } from '../../domain/publication-channels/types';
import {
  PUBLICATION_PLATFORM_LABELS,
  canDeletePublicationChannel,
  createPublicationChannel,
  publicationChannelLabel,
  validatePublicationChannels
} from '../../domain/publication-channels/transitions';
import { ValidationBadge } from './ValidationPanel';

type Draft = PublicationChannel;

const EMPTY_DRAFT: Draft = createPublicationChannel({
  id: 'new-publication-channel',
  projectId: 'local-project',
  platform: 'telegram',
  title: 'Telegram',
  language: 'ru',
  role: 'primary',
  publishingMode: 'manual',
  status: 'active'
});

export function PublicationChannelsTab({
  channels,
  planItems,
  settings,
  onChange
}: {
  channels: PublicationChannel[];
  planItems: ContentPlanItem[];
  settings: ContentPlanSettings;
  onChange: (channels: PublicationChannel[]) => void;
}) {
  const [expandedId, setExpandedId] = useState<string | null>(channels[0]?.id ?? null);
  const [editingId, setEditingId] = useState<string | null>(null);
  const [draft, setDraft] = useState<Draft | null>(null);
  const validation = useMemo(() => validatePublicationChannels(channels), [channels]);

  function startCreate() {
    if (editingId === 'new' && draft) {
      setExpandedId(draft.id);
      return;
    }
    const nextDraft = { ...EMPTY_DRAFT, id: `channel-${Date.now()}` };
    setExpandedId(nextDraft.id);
    setEditingId('new');
    setDraft(nextDraft);
  }

  function startEdit(channel: PublicationChannel) {
    setExpandedId(channel.id);
    setEditingId(channel.id);
    setDraft({ ...channel });
  }

  function saveDraft() {
    if (!draft) return;
    const normalized = createPublicationChannel(draft);
    const exists = channels.some((channel) => channel.id === normalized.id);
    onChange(exists ? channels.map((channel) => channel.id === normalized.id ? normalized : channel) : [normalized, ...channels]);
    setExpandedId(normalized.id);
    setEditingId(null);
    setDraft(null);
  }

  function cancelEdit() {
    setEditingId(null);
    setDraft(null);
  }

  function pauseChannel(channel: PublicationChannel) {
    onChange(channels.map((item) => item.id === channel.id ? { ...item, status: 'paused' } : item));
  }

  function activateChannel(channel: PublicationChannel) {
    onChange(channels.map((item) => item.id === channel.id ? { ...item, status: 'active' } : item));
  }

  function deleteChannel(channel: PublicationChannel) {
    if (!canDeletePublicationChannel(channel.id, planItems)) {
      pauseChannel(channel);
      return;
    }
    onChange(channels.filter((item) => item.id !== channel.id));
    if (expandedId === channel.id) setExpandedId(null);
  }

  return (
    <section className="publication-channels-tab">
      <div className="entity-list">
        <div className="entity-list-toolbar">
          <span className="mono-label">{channels.length} каналов</span>
          <button className="btn btn-sec btn-sm" type="button" onClick={startCreate}>
            + Канал
          </button>
        </div>
        {validation.messages.length > 0 ? (
          <div className={`validation-badge ${validation.status === 'critical' ? 'red' : 'yellow'}`}>
            {validation.messages.join(' ')}
          </div>
        ) : null}
        {editingId === 'new' && draft ? (
          <article className="card entity-row publication-channel-row">
            <ChannelRowHeader channel={draft} isPlaceholder />
            <ChannelEditor draft={draft} settings={settings} onPatch={setDraft} onSave={saveDraft} onCancel={cancelEdit} />
          </article>
        ) : null}
        {channels.map((channel) => {
          const isExpanded = expandedId === channel.id;
          const isEditing = editingId === channel.id && draft;
          return (
            <article className="card entity-row publication-channel-row" key={channel.id}>
              <ChannelRowHeader
                channel={channel}
                onToggle={() => setExpandedId(isExpanded ? null : channel.id)}
              />
              {isExpanded ? (
                isEditing ? (
                  <ChannelEditor draft={draft} settings={settings} onPatch={setDraft} onSave={saveDraft} onCancel={cancelEdit} />
                ) : (
                  <ChannelDetails
                    channel={channel}
                    settings={settings}
                    planItems={planItems}
                    onActivate={() => activateChannel(channel)}
                    onDelete={() => deleteChannel(channel)}
                    onEdit={() => startEdit(channel)}
                    onPause={() => pauseChannel(channel)}
                  />
                )
              ) : null}
            </article>
          );
        })}
      </div>
    </section>
  );
}

function ChannelRowHeader({
  channel,
  isPlaceholder = false,
  onToggle
}: {
  channel: PublicationChannel;
  isPlaceholder?: boolean;
  onToggle?: () => void;
}) {
  const status = channel.status === 'active' ? 'активно' : 'пауза';
  const validationStatus = channel.title.trim() && channel.language.trim() ? 'green' : 'yellow';

  return (
    <div className="entity-row-main">
      {onToggle ? (
        <button className="entity-title-button" type="button" onClick={onToggle}>
          {channel.title}
        </button>
      ) : (
        <span className="entity-title-placeholder">{channel.title.trim() || 'Новый канал'}</span>
      )}
      <div className="entity-row-meta">
        <span className="entity-meta-chip">{PUBLICATION_PLATFORM_LABELS[channel.platform]}</span>
        <span className={`status-chip ${channel.status}`}>{status}</span>
        <span className="entity-meta-chip">{channel.role}</span>
        <span className="entity-meta-chip">{channel.language}</span>
        <span className="entity-meta-chip">{channel.defaultPublicationSizeProfileId ?? 'профиль'}</span>
      </div>
      <ValidationBadge status={isPlaceholder ? 'yellow' : validationStatus} />
    </div>
  );
}

function ChannelDetails({
  channel,
  settings,
  planItems,
  onActivate,
  onDelete,
  onEdit,
  onPause
}: {
  channel: PublicationChannel;
  settings: ContentPlanSettings;
  planItems: ContentPlanItem[];
  onActivate: () => void;
  onDelete: () => void;
  onEdit: () => void;
  onPause: () => void;
}) {
  const canDelete = canDeletePublicationChannel(channel.id, planItems);

  return (
    <div className="entity-details">
      <div className="entity-details-scroll">
        <dl className="entity-detail-list">
          <dt>Платформа</dt>
          <dd>{PUBLICATION_PLATFORM_LABELS[channel.platform]}</dd>
          <dt>Роль</dt>
          <dd>{channel.role}</dd>
          <dt>Режим</dt>
          <dd>{channel.publishingMode}</dd>
          <dt>Язык</dt>
          <dd>{channel.language}</dd>
          <dt>Профиль размера</dt>
          <dd>{channel.defaultPublicationSizeProfileId ?? settings.defaultPublicationSizeProfileId}</dd>
          <dt>Адрес</dt>
          <dd>{channel.handleOrUrl || 'Не задан'}</dd>
        </dl>
      </div>
      <div className="inline-actions">
        <button className="btn btn-sec btn-sm" type="button" onClick={onEdit}>
          Редактировать
        </button>
        {channel.status === 'active' ? (
          <button className="btn btn-sec btn-sm" type="button" onClick={onPause}>
            Пауза
          </button>
        ) : (
          <button className="btn btn-sec btn-sm" type="button" onClick={onActivate}>
            Активировать
          </button>
        )}
        <button className="btn btn-sec btn-sm danger-text" type="button" onClick={onDelete}>
          {canDelete ? 'Удалить' : 'Пауза вместо удаления'}
        </button>
      </div>
    </div>
  );
}

function ChannelEditor({
  draft,
  settings,
  onPatch,
  onSave,
  onCancel
}: {
  draft: Draft;
  settings: ContentPlanSettings;
  onPatch: (draft: Draft) => void;
  onSave: () => void;
  onCancel: () => void;
}) {
  function patch(value: Partial<Draft>) {
    onPatch({ ...draft, ...value });
  }

  return (
    <div className="entity-edit-form publication-channel-editor">
      <div className="entity-edit-scroll">
        <label>Название
          <input value={draft.title} onChange={(event) => patch({ title: event.target.value })} />
        </label>
        <label>Платформа
          <select value={draft.platform} onChange={(event) => patch({ platform: event.target.value as Draft['platform'] })}>
            {Object.entries(PUBLICATION_PLATFORM_LABELS).map(([id, label]) => <option value={id} key={id}>{label}</option>)}
          </select>
        </label>
        <label>Язык
          <input value={draft.language} onChange={(event) => patch({ language: event.target.value })} />
        </label>
        <label>Handle или URL
          <input value={draft.handleOrUrl} onChange={(event) => patch({ handleOrUrl: event.target.value })} />
        </label>
        <label>Роль
          <select value={draft.role} onChange={(event) => patch({ role: event.target.value as Draft['role'] })}>
            <option value="primary">primary</option>
            <option value="repurpose">repurpose</option>
            <option value="experiment">experiment</option>
            <option value="archive">archive</option>
          </select>
        </label>
        <label>Режим
          <select value={draft.publishingMode} onChange={(event) => patch({ publishingMode: event.target.value as Draft['publishingMode'] })}>
            <option value="manual">manual</option>
            <option value="adapterPlanned">adapterPlanned</option>
            <option value="connected">connected</option>
          </select>
        </label>
        <label>Профиль размера
          <select value={draft.defaultPublicationSizeProfileId ?? ''} onChange={(event) => patch({ defaultPublicationSizeProfileId: event.target.value || undefined })}>
            <option value="">По умолчанию: {settings.defaultPublicationSizeProfileId}</option>
            {settings.publicationSizeProfiles.map((profile) => <option value={profile.id} key={profile.id}>{profile.title}</option>)}
          </select>
        </label>
      </div>
      <div className="inline-actions">
        <button className="btn btn-sec btn-sm" type="button" onClick={onCancel}>
          Отменить
        </button>
        <button className="btn btn-pri btn-sm" type="button" onClick={onSave} disabled={!draft.title.trim() || !draft.language.trim()}>
          Сохранить
        </button>
      </div>
      <p className="muted">{publicationChannelLabel(draft)} сохраняет legacy platform label для старых экранов.</p>
    </div>
  );
}
