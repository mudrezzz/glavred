import { chromium } from '@playwright/test';
import { readFile } from 'node:fs/promises';

const frontendUrl = process.env.AUTH_SMOKE_FRONTEND_URL ?? 'http://127.0.0.1:5176';
const backendUrl = process.env.AUTH_SMOKE_BACKEND_URL ?? 'http://127.0.0.1:8000';

async function main() {
  const password = process.env.GLAVRED_DEV_AUTH_PASSWORD
    ?? await secretFileValue(process.env.GLAVRED_DEV_AUTH_PASSWORD_FILE)
    ?? await envValue('GLAVRED_DEV_AUTH_PASSWORD')
    ?? 'glavred-demo';
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: 1440, height: 1000 } });
  page.on('requestfailed', (request) => {
    if (request.url().includes('/api/')) console.error(`Request failed: ${request.method()} ${request.url()} ${request.failure()?.errorText ?? ''}`);
  });
  page.on('pageerror', (error) => console.error(`Page error: ${error.message}`));

  try {
    await page.goto(frontendUrl, { waitUntil: 'domcontentloaded' });
    await login(page, 'founder@example.test', password);
    await page.getByRole('button', { name: 'Выйти' }).waitFor();

    await page.getByRole('button', { name: 'Открыть кабинет' }).first().click();
    const switcher = page.getByTestId('portfolio-switcher');
    await switcher.getByRole('button').click();
    await page.getByTestId('portfolio-switcher-panel').getByRole('button', { name: 'Выйти' }).click();
    await assertLoggedOut(page);

    await login(page, 'glavred-editor@example.test', password);
    await page.getByRole('button', { name: 'Выйти' }).click();
    await assertLoggedOut(page);

    console.log('Auth session smoke passed: cabinet logout, account switch, and dashboard logout.');
  } finally {
    await browser.close();
  }
}

async function secretFileValue(path) {
  if (!path) return null;
  const value = (await readFile(path, 'utf8')).trim();
  return value || null;
}

async function login(page, email, password) {
  const loginButton = page.getByRole('button', { name: 'Войти' });
  await loginButton.waitFor();
  await page.locator('input[type="email"]').fill(email);
  await page.locator('input[type="password"]').fill(password);
  const responsePromise = page.waitForResponse(
    (response) => response.url().endsWith('/api/auth/login') && response.request().method() === 'POST'
  );
  await loginButton.click();
  const response = await responsePromise;
  if (!response.ok()) throw new Error(`Login failed for ${email} with status ${response.status()}.`);
  await page.getByTestId('project-dashboard').waitFor();
  await page.getByText(email, { exact: true }).first().waitFor();
}

async function assertLoggedOut(page) {
  await page.getByRole('heading', { name: 'Вход в рабочий портфель' }).waitFor();
  const status = await page.evaluate(async (url) => {
    const response = await fetch(`${url}/api/users/me`, { credentials: 'include' });
    return response.status;
  }, backendUrl);
  if (status !== 401) throw new Error(`Expected /api/users/me=401 after logout, received ${status}.`);
}

async function envValue(name) {
  try {
    const source = await readFile('.env', 'utf8');
    const line = source.split(/\r?\n/).find((item) => item.trim().startsWith(`${name}=`));
    if (!line) return null;
    return line.slice(line.indexOf('=') + 1).trim().replace(/^['"]|['"]$/g, '');
  } catch {
    return null;
  }
}

await main();
