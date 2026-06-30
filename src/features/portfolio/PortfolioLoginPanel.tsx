import { useState } from 'react';

export function PortfolioLoginPanel({
  error,
  loading,
  onLogin
}: {
  error: string;
  loading: boolean;
  onLogin: (email: string, password: string) => Promise<void>;
}) {
  const [email, setEmail] = useState('founder@example.test');
  const [password, setPassword] = useState('glavred-demo');

  return (
    <main className="portfolio-login-screen">
      <form
        className="portfolio-login-panel"
        onSubmit={(event) => {
          event.preventDefault();
          void onLogin(email, password);
        }}
      >
        <span className="eyebrow">Backend portfolio</span>
        <h1>Вход в рабочий портфель</h1>
        <p>Используется dev-password сессия. Если backend выключен, приложение откроет локальный демо-портфель.</p>
        <label>
          <span>Email</span>
          <input value={email} type="email" onChange={(event) => setEmail(event.target.value)} />
        </label>
        <label>
          <span>Пароль</span>
          <input value={password} type="password" onChange={(event) => setPassword(event.target.value)} />
        </label>
        {error ? <div className="portfolio-login-error">{error}</div> : null}
        <button className="primary" type="submit" disabled={loading}>
          {loading ? 'Проверяем...' : 'Войти'}
        </button>
        <div className="portfolio-login-hint">
          Демо: founder@example.test или glavred-editor@example.test, пароль по умолчанию glavred-demo.
        </div>
      </form>
    </main>
  );
}
