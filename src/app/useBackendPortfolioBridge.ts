import { useEffect, useState, type Dispatch, type SetStateAction } from 'react';
import type { PortfolioState } from '../domain/portfolio/types';
import {
  BackendPortfolioAuthRequiredError,
  BackendPortfolioStore,
  BackendPortfolioUnavailableError
} from '../infrastructure/backendPortfolioStore';
import { LocalPortfolioStore } from '../infrastructure/localPortfolioStore';

export type PortfolioBackendStatus = 'checking' | 'authenticated' | 'loginRequired' | 'localFallback';

const backendStore = new BackendPortfolioStore();

export function useBackendPortfolioBridge({
  localStore,
  portfolio,
  setPortfolio,
  setToast
}: {
  localStore: LocalPortfolioStore;
  portfolio: PortfolioState;
  setPortfolio: Dispatch<SetStateAction<PortfolioState>>;
  setToast: (message: string) => void;
}) {
  const [backendStatus, setBackendStatus] = useState<PortfolioBackendStatus>('checking');
  const [authError, setAuthError] = useState('');

  useEffect(() => {
    let cancelled = false;
    backendStore
      .load()
      .then((loadedPortfolio) => {
        if (cancelled) return;
        setPortfolio(loadedPortfolio);
        setBackendStatus('authenticated');
        setAuthError('');
      })
      .catch((error) => {
        if (cancelled) return;
        setBackendStatus(error instanceof BackendPortfolioAuthRequiredError ? 'loginRequired' : 'localFallback');
      });
    return () => {
      cancelled = true;
    };
  }, [setPortfolio]);

  useEffect(() => {
    if (backendStatus !== 'authenticated') return;
    backendStore.save(portfolio).catch(() => {
      setBackendStatus('localFallback');
      setToast('Backend недоступен, изменения сохранены локально');
    });
  }, [backendStatus, portfolio, setToast]);

  async function login(email: string, password: string) {
    setAuthError('');
    try {
      setPortfolio(await backendStore.login(email, password));
      setBackendStatus('authenticated');
      setToast('Вход выполнен');
    } catch (error) {
      if (error instanceof BackendPortfolioAuthRequiredError) {
        setBackendStatus('loginRequired');
        setAuthError('Неверный email или пароль');
        return;
      }
      setBackendStatus('localFallback');
      setToast('Backend недоступен, открыт локальный демо-портфель');
    }
  }

  async function logout() {
    await backendStore.logout().catch(() => undefined);
    setPortfolio(localStore.load());
    setBackendStatus('loginRequired');
    setToast('Вы вышли из backend-сессии');
  }

  function reloadBackendPortfolio(): boolean {
    if (backendStatus !== 'authenticated') return false;
    backendStore.load().then(setPortfolio).catch(() => setBackendStatus('localFallback'));
    setToast('Backend-портфель перезагружен');
    return true;
  }

  return { authError, backendStatus, login, logout, reloadBackendPortfolio };
}
