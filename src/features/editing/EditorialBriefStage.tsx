import { useState } from 'react';
import type { PostBrief, PostBriefEditPatch, WorkspaceState } from '../../domain/editorialWorkspace';
import { Icon } from '../../shared/ui/Icon';
import { EditorialBriefContextPanel } from './EditorialBriefContextPanel';
import { EditorialBriefEditForm } from './EditorialBriefEditForm';
import { getEditorialWorkItemContext } from './editorialWorkItemContext';

export function EditorialBriefStage({
  brief,
  workspace,
  onApproveBrief,
  onEditBrief,
  onGoPlan,
  onOpenDraft
}: {
  brief: PostBrief;
  workspace: WorkspaceState;
  onApproveBrief: () => void;
  onEditBrief: (patch: PostBriefEditPatch) => void;
  onGoPlan: () => void;
  onOpenDraft: () => void;
}) {
  const [isEditing, setIsEditing] = useState(false);
  const selectedWorkItem = workspace.editorialWorkItems.find((item) => item.id === workspace.selectedEditorialWorkItemId) ?? null;
  const context = getEditorialWorkItemContext(workspace, selectedWorkItem);

  function approveBrief() {
    onApproveBrief();
    onOpenDraft();
  }

  function saveBrief(patch: PostBriefEditPatch) {
    onEditBrief(patch);
    setIsEditing(false);
  }

  return (
    <section className="doc editorial-brief-stage" data-testid="editorial-brief-stage">
      <EditorialBriefContextPanel context={context} />
      {isEditing ? (
        <EditorialBriefEditForm brief={brief} onCancel={() => setIsEditing(false)} onSave={saveBrief} />
      ) : (
        <>
          <BriefSnapshot brief={brief} />
          <div className="inline-actions editorial-brief-actions">
            <button
              className="btn btn-pri"
              type="button"
              disabled={brief.approvalStatus === 'approved'}
              onClick={approveBrief}
            >
              <Icon name="check" size={16} />
              {brief.approvalStatus === 'approved' ? 'Фабула утверждена' : 'Утвердить фабулу'}
            </button>
            <button className="btn btn-sec" type="button" onClick={() => setIsEditing(true)}>
              Редактировать
            </button>
            <button className="btn btn-sec" type="button" onClick={onGoPlan}>
              Вернуться в план
            </button>
          </div>
        </>
      )}
    </section>
  );
}

function BriefSnapshot({ brief }: { brief: PostBrief }) {
  return (
    <div className="brief-snapshot" data-testid="editorial-brief-snapshot">
      <span className="rub">{brief.rubric}</span>
      <h2>{brief.title}</h2>
      <p className="lead">{brief.thesis}</p>
      <div className="snapshot-grid">
        <InfoBlock title="Конфликт" items={[brief.conflict]} />
        <InfoBlock title="Позиция" items={[brief.authorPosition]} />
        <InfoBlock title="Аудитория" items={[brief.audience]} />
        <InfoBlock title="CTA" items={[brief.cta]} />
        <InfoBlock title="Доказательства" items={brief.evidence} wide />
        <InfoBlock title="Примеры" items={brief.examples} wide />
        <InfoBlock title="Структура" items={brief.structure} wide />
        <InfoBlock title="Риски" items={brief.risks} wide />
        <InfoBlock title="Источники" items={brief.sources} wide />
      </div>
    </div>
  );
}

function InfoBlock({ title, items, wide = false }: { title: string; items: string[]; wide?: boolean }) {
  return (
    <div className={`info-block${wide ? ' wide' : ''}`}>
      <h4>{title}</h4>
      <ul className="bullets">
        {items.map((item) => (
          <li key={item}>{item}</li>
        ))}
      </ul>
    </div>
  );
}
