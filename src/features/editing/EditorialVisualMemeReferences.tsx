import type { PostVisualMemeReference } from '../../domain/editorialWorkspace';
import { Icon } from '../../shared/ui/Icon';

export function EditorialVisualMemeReferences({
  references,
  selectedReferenceId,
  onSelect
}: {
  references: PostVisualMemeReference[];
  selectedReferenceId: string | null;
  onSelect: (referenceId: string) => void;
}) {
  return (
    <div className="visual-variants" data-testid="editorial-visual-meme-references">
      {references.map((reference) => {
        const selected = reference.id === selectedReferenceId;

        return (
          <article className={`visual-variant-card${selected ? ' selected' : ''}`} data-testid="editorial-visual-meme-reference" key={reference.id}>
            <div className="visual-variant-preview">{reference.previewLabel}</div>
            <div className="visual-variant-body">
              <span className="k">Мем-референс</span>
              <h3>{reference.title}</h3>
              <p>{reference.description}</p>
              <dl className="visual-variant-details">
                <div>
                  <dt>Почему подходит</dt>
                  <dd>{reference.rationale}</dd>
                </div>
                <div>
                  <dt>Риски</dt>
                  <dd>{reference.risks.join(' ')}</dd>
                </div>
              </dl>
              <div className="inline-actions">
                <button className={`btn ${selected ? 'btn-pri' : 'btn-sec'}`} type="button" onClick={() => onSelect(reference.id)}>
                  {selected ? <Icon name="check" size={16} /> : null}
                  {selected ? 'Мем выбран' : 'Выбрать мем'}
                </button>
              </div>
            </div>
          </article>
        );
      })}
    </div>
  );
}
