import type { ContentPlanSettings } from '../../domain/editorialWorkspace';
import type { PublicationKind, PublicationSizeProfile } from '../../domain/planning/publicationSize';

const KIND_LABELS: Record<PublicationKind, string> = {
  shortPost: 'Короткий пост',
  longPost: 'Длинный пост',
  article: 'Статья'
};

export function PublicationSizeSettings({
  settings,
  onChange
}: {
  settings: ContentPlanSettings;
  onChange: (settings: ContentPlanSettings) => void;
}) {
  const selectedProfile =
    settings.publicationSizeProfiles.find((profile) => profile.id === settings.defaultPublicationSizeProfileId) ??
    settings.publicationSizeProfiles[0];

  function updateDefaultProfileId(defaultPublicationSizeProfileId: string) {
    onChange({ ...settings, defaultPublicationSizeProfileId });
  }

  function updateSelectedProfile(patch: Partial<PublicationSizeProfile>) {
    if (!selectedProfile) return;
    onChange({
      ...settings,
      publicationSizeProfiles: settings.publicationSizeProfiles.map((profile) =>
        profile.id === selectedProfile.id ? { ...profile, ...patch } : profile
      )
    });
  }

  if (!selectedProfile) return null;

  return (
    <section className="publication-size-settings">
      <div className="publication-size-header">
        <span className="mono-label">Размер публикации</span>
        <p>Профиль задает диапазон длины для плановых слотов. Фабула добавляет только масштаб.</p>
      </div>
      <div className="publication-size-grid">
        <label>
          Профиль по умолчанию
          <select value={selectedProfile.id} onChange={(event) => updateDefaultProfileId(event.target.value)}>
            {settings.publicationSizeProfiles.map((profile) => (
              <option key={profile.id} value={profile.id}>
                {profile.title}
              </option>
            ))}
          </select>
        </label>
      <label>
        Платформа профиля
          <input value={selectedProfile.platform} onChange={(event) => updateSelectedProfile({ platform: event.target.value })} />
        </label>
        <label>
          Тип
          <select
            value={selectedProfile.publicationKind}
            onChange={(event) => updateSelectedProfile({ publicationKind: event.target.value as PublicationKind })}
          >
            {Object.entries(KIND_LABELS).map(([value, label]) => (
              <option key={value} value={value}>
                {label}
              </option>
            ))}
          </select>
        </label>
        <label>
          Минимум
          <input type="number" min={100} value={selectedProfile.minChars} onChange={(event) => updateSelectedProfile({ minChars: Number(event.target.value) })} />
        </label>
        <label>
          Цель
          <input type="number" min={100} value={selectedProfile.targetChars} onChange={(event) => updateSelectedProfile({ targetChars: Number(event.target.value) })} />
        </label>
        <label>
          Максимум
          <input type="number" min={100} value={selectedProfile.maxChars} onChange={(event) => updateSelectedProfile({ maxChars: Number(event.target.value) })} />
        </label>
      </div>
    </section>
  );
}
