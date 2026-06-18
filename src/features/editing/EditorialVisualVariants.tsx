import type { PostVisualVariant } from '../../domain/editorialWorkspace';
import { Icon } from '../../shared/ui/Icon';

export function EditorialVisualVariants({
  selectedVariantId,
  variants,
  onSelect
}: {
  selectedVariantId: string | null;
  variants: PostVisualVariant[];
  onSelect: (variantId: string) => void;
}) {
  return (
    <div className="visual-variants" data-testid="editorial-visual-variants">
      {variants.map((variant) => {
        const selected = variant.id === selectedVariantId;

        return (
          <article className={`visual-variant-card${selected ? ' selected' : ''}`} data-testid="editorial-visual-variant" key={variant.id}>
            <div className="visual-variant-preview">{variant.previewLabel}</div>
            <div className="visual-variant-body">
              <span className="k">Вариант визуала</span>
              <h3>{variant.title}</h3>
              <p>{variant.description}</p>
              <dl className="visual-variant-details">
                <div>
                  <dt>Почему подходит</dt>
                  <dd>{variant.rationale}</dd>
                </div>
                <div>
                  <dt>Риски</dt>
                  <dd>{variant.risks.join(' ')}</dd>
                </div>
              </dl>
              <div className="inline-actions">
                <button className={`btn ${selected ? 'btn-pri' : 'btn-sec'}`} type="button" onClick={() => onSelect(variant.id)}>
                  {selected ? <Icon name="check" size={16} /> : null}
                  {selected ? 'Выбран' : 'Выбрать'}
                </button>
              </div>
            </div>
          </article>
        );
      })}
    </div>
  );
}
