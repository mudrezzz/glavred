import { useState } from 'react';
import { act, renderHook, waitFor } from '@testing-library/react';
import { afterEach, describe, expect, it, vi } from 'vitest';
import { createDemoPortfolio } from '../fixtures/demoPortfolio';
import { useBackendPortfolioBridge } from './useBackendPortfolioBridge';

function jsonResponse(payload: unknown, status = 200): Response {
  return {
    ok: status >= 200 && status < 300,
    status,
    json: async () => payload
  } as Response;
}

function deferredResponse() {
  let reject!: (reason?: unknown) => void;
  const promise = new Promise<Response>((_resolve, rejectPromise) => {
    reject = rejectPromise;
  });
  return { promise, reject };
}

function useBridgeHarness() {
  const [portfolio, setPortfolio] = useState(createDemoPortfolio());
  const [toast, setToast] = useState('');
  const bridge = useBackendPortfolioBridge({ portfolio, setPortfolio, setToast });
  return { ...bridge, toast };
}

describe('useBackendPortfolioBridge logout', () => {
  afterEach(() => {
    vi.unstubAllGlobals();
  });

  it('keeps the login screen active when an older autosave fails after logout', async () => {
    const staleSave = deferredResponse();
    const fetcher = vi.fn((input: RequestInfo | URL, init?: RequestInit) => {
      const url = String(input);
      if (url.endsWith('/api/users/me')) {
        return Promise.resolve(jsonResponse({
          user: {
            id: 'user-founder-editor',
            displayName: 'Founder',
            email: 'founder@example.test',
            status: 'active',
            createdAt: '2026-06-30T00:00:00Z'
          }
        }));
      }
      if (url.includes('/api/projects?')) {
        return Promise.resolve(jsonResponse({ projects: [] }));
      }
      if (url.endsWith('/api/auth/logout')) {
        return Promise.resolve(jsonResponse({ status: 'ok' }));
      }
      if (init?.method === 'PUT') return staleSave.promise;
      return Promise.resolve(jsonResponse({}));
    });
    vi.stubGlobal('fetch', fetcher);

    const { result } = renderHook(() => useBridgeHarness());

    await waitFor(() => expect(result.current.backendStatus).toBe('authenticated'));
    await waitFor(() => expect(fetcher.mock.calls.some(([, init]) => init?.method === 'PUT')).toBe(true));

    await act(async () => {
      await result.current.logout();
    });
    expect(result.current.backendStatus).toBe('loginRequired');

    staleSave.reject(new TypeError('late autosave failure'));
    await act(async () => {
      await Promise.resolve();
    });

    expect(result.current.backendStatus).toBe('loginRequired');
    expect(result.current.toast).toBe('Вы вышли из аккаунта');
  });
});
