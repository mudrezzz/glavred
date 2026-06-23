import { useState } from 'react';
import type { PostBrief, PostBriefEditPatch } from '../../domain/editorialWorkspace';
import { BriefSourceIntentEditor } from './BriefSourceIntentEditor';

export function EditorialBriefEditForm({
  brief,
  onCancel,
  onSave
}: {
  brief: PostBrief;
  onCancel: () => void;
  onSave: (patch: PostBriefEditPatch) => void;
}) {
  const [draft, setDraft] = useState({
    title: brief.title,
    thesis: brief.thesis,
    conflict: brief.conflict,
    authorPosition: brief.authorPosition,
    audience: brief.audience,
    evidence: toText(brief.evidence),
    examples: toText(brief.examples),
    structure: toText(brief.structure),
    cta: brief.cta,
    risks: toText(brief.risks),
    sources: toText(brief.sources)
  });

  function update(field: keyof typeof draft, value: string) {
    setDraft((current) => ({ ...current, [field]: value }));
  }

  return (
    <div className="brief-edit-form" data-testid="editorial-brief-edit-form">
      <div className="brief-edit-grid">
        <label>
          Заголовок
          <input value={draft.title} onChange={(event) => update('title', event.target.value)} />
        </label>
        <label>
          Аудитория
          <textarea value={draft.audience} onChange={(event) => update('audience', event.target.value)} />
        </label>
        <label className="brief-edit-wide">
          Тезис
          <textarea value={draft.thesis} onChange={(event) => update('thesis', event.target.value)} />
        </label>
        <label className="brief-edit-wide">
          Конфликт
          <textarea value={draft.conflict} onChange={(event) => update('conflict', event.target.value)} />
        </label>
        <label className="brief-edit-wide">
          Позиция / ценность
          <textarea value={draft.authorPosition} onChange={(event) => update('authorPosition', event.target.value)} />
        </label>
        <label className="brief-edit-wide">
          Доказательства
          <textarea value={draft.evidence} onChange={(event) => update('evidence', event.target.value)} />
        </label>
        <label className="brief-edit-wide">
          Примеры
          <textarea value={draft.examples} onChange={(event) => update('examples', event.target.value)} />
        </label>
        <label className="brief-edit-wide">
          Структура
          <textarea value={draft.structure} onChange={(event) => update('structure', event.target.value)} />
        </label>
        <label className="brief-edit-wide">
          CTA
          <textarea value={draft.cta} onChange={(event) => update('cta', event.target.value)} />
        </label>
        <label className="brief-edit-wide">
          Риски
          <textarea value={draft.risks} onChange={(event) => update('risks', event.target.value)} />
        </label>
        <BriefSourceIntentEditor value={draft.sources} onChange={(value) => update('sources', value)} />
      </div>
      <div className="inline-actions brief-edit-actions">
        <button className="btn btn-pri" type="button" onClick={() => onSave(toPatch(draft))}>
          Сохранить
        </button>
        <button className="btn btn-sec" type="button" onClick={onCancel}>
          Отменить
        </button>
      </div>
    </div>
  );
}

function toText(items: string[]): string {
  return items.join('\n');
}

function toLines(value: string): string[] {
  return value.split(/\r?\n/).map((line) => line.trim()).filter(Boolean);
}

function toPatch(draft: {
  title: string;
  thesis: string;
  conflict: string;
  authorPosition: string;
  audience: string;
  evidence: string;
  examples: string;
  structure: string;
  cta: string;
  risks: string;
  sources: string;
}): PostBriefEditPatch {
  return {
    title: draft.title.trim(),
    thesis: draft.thesis.trim(),
    conflict: draft.conflict.trim(),
    authorPosition: draft.authorPosition.trim(),
    audience: draft.audience.trim(),
    evidence: toLines(draft.evidence),
    examples: toLines(draft.examples),
    structure: toLines(draft.structure),
    cta: draft.cta.trim(),
    risks: toLines(draft.risks),
    sources: toLines(draft.sources)
  };
}
