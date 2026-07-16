import { useEffect, useState, type Dispatch, type SetStateAction } from 'react';
import type { PortfolioState } from '../domain/portfolio/types';
import {
  BackendPortfolioAuthRequiredError,
  BackendPortfolioIntegrityError,
  BackendPortfolioStore,
  type BackendProjectCreateInput,
  type BackendProjectUpdateInput
} from '../infrastructure/backendPortfolioStore';
import { LocalPortfolioStore } from '../infrastructure/localPortfolioStore';

export type PortfolioBackendStatus = 'checking' | 'authenticated' | 'loginRequired' | 'localFallback' | 'integrityError';

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
  const [integrityError, setIntegrityError] = useState('');

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
        if (error instanceof BackendPortfolioIntegrityError) {
          setBackendStatus('integrityError');
          setIntegrityError(integrityMessage(error));
          return;
        }
        setBackendStatus(error instanceof BackendPortfolioAuthRequiredError ? 'loginRequired' : 'localFallback');
      });
    return () => {
      cancelled = true;
    };
  }, [setPortfolio]);

  useEffect(() => {
    if (backendStatus !== 'authenticated') return;
    backendStore.save(portfolio).catch((error) => {
      if (error instanceof BackendPortfolioIntegrityError) {
        setBackendStatus('integrityError');
        setIntegrityError(integrityMessage(error));
        return;
      }
      setBackendStatus('localFallback');
      setToast('Backend недоступен, изменения сохранены локально');
    });
  }, [backendStatus, portfolio, setToast]);

  async function login(email: string, password: string) {
    setAuthError('');
    try {
      setPortfolio(await backendStore.login(email, password));
      setBackendStatus('authenticated');
      setIntegrityError('');
      setToast('Вход выполнен');
    } catch (error) {
      if (error instanceof BackendPortfolioAuthRequiredError) {
        setBackendStatus('loginRequired');
        setAuthError('Неверный email или пароль');
        return;
      }
      if (error instanceof BackendPortfolioIntegrityError) {
        setBackendStatus('integrityError');
        setIntegrityError(integrityMessage(error));
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
    backendStore.load().then((loaded) => {
      setPortfolio(loaded);
      setIntegrityError('');
    }).catch((error) => {
      if (error instanceof BackendPortfolioIntegrityError) {
        setBackendStatus('integrityError');
        setIntegrityError(integrityMessage(error));
        return;
      }
      setBackendStatus('localFallback');
    });
    setToast('Backend-портфель перезагружен');
    return true;
  }

  async function createProject(input: BackendProjectCreateInput): Promise<boolean> {
    if (backendStatus !== 'authenticated') return false;
    try {
      await backendStore.createProject(input);
      setPortfolio(await backendStore.load());
      setToast('Проект создан');
      return true;
    } catch {
      setBackendStatus('localFallback');
      setToast('Backend недоступен, проект будет создан локально');
      return false;
    }
  }

  async function updateProject(projectId: string, patch: BackendProjectUpdateInput): Promise<boolean> {
    if (backendStatus !== 'authenticated') return false;
    try {
      await backendStore.updateProject(projectId, patch);
      setPortfolio(await backendStore.load());
      setToast(patch.status === 'archived' ? 'Проект отправлен в архив' : 'Проект обновлен');
      return true;
    } catch {
      setBackendStatus('localFallback');
      setToast('Backend недоступен, изменение сохранено локально');
      return false;
    }
  }

  return { authError, backendStatus, createProject, integrityError, login, logout, reloadBackendPortfolio, updateProject };
}

function integrityMessage(error: BackendPortfolioIntegrityError): string {
  const snapshot = error.diagnostic.snapshotId ? ` Снимок: ${error.diagnostic.snapshotId}.` : '';
  return `Проверка данных проекта обнаружила поврежденный текст. Автосохранение остановлено.${snapshot}`;
}
