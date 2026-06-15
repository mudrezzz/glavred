import type {
  ContentPlanItem,
  FinalText,
  ReleasePackage,
  ReleaseTarget
} from '../domain/editorialWorkspace';

export function createReleasePackage(
  finalText: FinalText,
  contentPlanItem: ContentPlanItem | null
): ReleasePackage {
  if (finalText.approvalStatus !== 'approved') {
    throw new Error('Release package can be created only from approved final text.');
  }

  const targets = resolveReleaseTargets(contentPlanItem?.platform ?? '');
  const platformLabel = contentPlanItem?.platform ?? targets.join(' + ');
  const markdown = [
    `# ${finalText.title}`,
    '',
    finalText.body,
    '',
    '---',
    '',
    '## Метаданные выпуска',
    '',
    `- Площадки: ${platformLabel}`,
    `- Формат: ${contentPlanItem?.format ?? 'Ручной выпуск'}`,
    `- Дата плана: ${contentPlanItem?.date ?? 'не задана'}`,
    '- Статус: ручной экспорт подготовлен',
    `- Утверждено: ${finalText.approvedAt}`
  ].join('\n');

  return {
    id: `release-${finalText.id}`,
    finalTextId: finalText.id,
    targets,
    markdown,
    checklist: [
      { id: 'final-approved', label: 'Финальный текст утвержден', done: true },
      { id: 'warnings-reviewed', label: 'Фактические warnings просмотрены', done: false },
      { id: 'target-selected', label: 'Площадка выбрана', done: targets.length > 0 },
      { id: 'cta-reviewed', label: 'CTA проверен', done: false },
      { id: 'manual-exported', label: 'Текст скопирован или Markdown скачан', done: false }
    ],
    status: 'draft',
    updatedAt: new Date().toISOString()
  };
}

function resolveReleaseTargets(platform: string): ReleaseTarget[] {
  const normalized = platform.toLowerCase();
  const targets: ReleaseTarget[] = [];

  if (normalized.includes('telegram')) {
    targets.push('telegram');
  }

  if (normalized.includes('linkedin')) {
    targets.push('linkedin');
  }

  return targets.length > 0 ? targets : ['telegram'];
}
