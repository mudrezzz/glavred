import type { PostVisual, PostVisualEditPatch, VisualMode } from '../../domain/editorialWorkspace';

export type VisualDraft = {
  mode: VisualMode;
  brief: string;
};

export const modeLabels: Record<VisualMode, string> = {
  generate: 'Сгенерировать',
  memeSearch: 'Найти мем',
  memeRemix: 'Мем + генерация',
  noVisual: 'Без визуала'
};

export function EditorialVisualFields({
  draft,
  onChange
}: {
  draft: VisualDraft;
  onChange: (draft: VisualDraft) => void;
}) {
  if (draft.mode === 'noVisual') {
    return null;
  }

  return (
    <div className="visual-form" data-testid="editorial-visual-form">
      <VisualTextarea label="Бриф" value={draft.brief} onChange={(brief) => onChange({ ...draft, brief })} />
    </div>
  );
}

export function toVisualDraft(visual: PostVisual | null): VisualDraft {
  const legacyBrief =
    visual?.brief ||
    visual?.prompt ||
    visual?.memeSearchQuery ||
    visual?.transformationInstructions ||
    visual?.notes ||
    '';

  return {
    mode: visual?.mode ?? 'generate',
    brief: visual?.mode === 'noVisual' ? '' : legacyBrief
  };
}

export function toVisualPatch(draft: VisualDraft): PostVisualEditPatch {
  return {
    mode: draft.mode,
    brief: draft.mode === 'noVisual' ? '' : draft.brief,
    prompt: '',
    memeSearchQuery: '',
    memeReferenceTitle: '',
    memeReferenceUrl: '',
    transformationInstructions: '',
    assetPlaceholder: '',
    notes: ''
  };
}

function VisualTextarea({ label, value, onChange }: { label: string; value: string; onChange: (value: string) => void }) {
  return (
    <label className="visual-field wide">
      <span className="k">{label}</span>
      <textarea value={value} onChange={(event) => onChange(event.target.value)} />
    </label>
  );
}
