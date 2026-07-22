import { Icon } from '../../shared/ui/Icon';

export function PortfolioIntegrityPanel({ message }: { message: string }) {
  return (
    <main className="integrity-page" data-testid="portfolio-integrity-error">
      <section className="panel integrity-panel" role="alert">
        <span className="sig">Целостность данных</span>
        <Icon name="warning" size={24} />
        <h1>Проект временно недоступен</h1>
        <p>{message}</p>
        <p>Поврежденные данные не были показаны и не будут сохранены повторно.</p>
      </section>
    </main>
  );
}
