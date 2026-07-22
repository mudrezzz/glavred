import { describe, expect, it } from 'vitest';
import { resolveApiBaseUrl } from './apiBaseUrl';

describe('resolveApiBaseUrl', () => {
  it('aligns loopback API requests with the authenticated browser host', () => {
    expect(resolveApiBaseUrl('http://localhost:8000', '127.0.0.1')).toBe('http://127.0.0.1:8000');
    expect(resolveApiBaseUrl('http://127.0.0.1:8000', 'localhost')).toBe('http://localhost:8000');
  });

  it('does not rewrite non-loopback API hosts', () => {
    expect(resolveApiBaseUrl('https://api.example.test/', '127.0.0.1')).toBe('https://api.example.test');
  });
});
