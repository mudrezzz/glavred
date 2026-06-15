import type { ImportCandidateGroup } from '../../domain/editorialWorkspace';

export function ImportCandidateGroupList({
  groups
}: {
  groups: ImportCandidateGroup[];
}) {
  return (
    <div className="import-groups">
      {groups.map((group) => (
        <article className="card import-group" key={group.id}>
          <div>
            <span className={`risk-dot ${group.riskLevel}`} />
            <b>{group.title}</b>
          </div>
          <span>{group.summary}</span>
          <small>{group.candidateIds.join(', ')}</small>
        </article>
      ))}
    </div>
  );
}
