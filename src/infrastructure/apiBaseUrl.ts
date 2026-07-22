export function resolveApiBaseUrl(configuredUrl: string, browserHost = globalThis.location?.hostname): string {
  if (!browserHost || !isLoopbackHost(browserHost)) return configuredUrl.replace(/\/$/u, '');
  try {
    const apiUrl = new URL(configuredUrl);
    if (!isLoopbackHost(apiUrl.hostname)) return configuredUrl.replace(/\/$/u, '');
    apiUrl.hostname = browserHost;
    return apiUrl.toString().replace(/\/$/u, '');
  } catch {
    return configuredUrl.replace(/\/$/u, '');
  }
}

function isLoopbackHost(hostname: string): boolean {
  return hostname === 'localhost' || hostname === '127.0.0.1';
}
