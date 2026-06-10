import { chromium } from '@playwright/test';
import { spawn } from 'node:child_process';
import { existsSync } from 'node:fs';
import { mkdir, rm } from 'node:fs/promises';
import path from 'node:path';

const rootDir = process.cwd();
const screenshotsDir = path.join(rootDir, 'docs', 'wiki', 'assets', 'screenshots');
const port = process.env.DOCS_SCREENSHOT_PORT ?? '4177';
const baseUrl = `http://127.0.0.1:${port}`;

function runDevServer() {
  const npmCommand = process.platform === 'win32' ? 'npm.cmd' : 'npm';
  return spawn(
    npmCommand,
    ['run', 'dev', '--', '--host', '127.0.0.1', '--port', port, '--strictPort'],
    {
      cwd: rootDir,
      env: { ...process.env, BROWSER: 'none' },
      shell: process.platform === 'win32',
      stdio: ['ignore', 'pipe', 'pipe']
    }
  );
}

async function waitForServer() {
  const startedAt = Date.now();
  while (Date.now() - startedAt < 30000) {
    try {
      const response = await fetch(baseUrl);
      if (response.ok) {
        return;
      }
    } catch {
      // Vite is still starting.
    }
    await new Promise((resolve) => setTimeout(resolve, 500));
  }
  throw new Error(`Vite did not start at ${baseUrl}`);
}

async function screenshot(page, name) {
  await page.locator('.scroll').evaluate((node) => {
    node.scrollTop = 0;
  });
  await page.screenshot({
    path: path.join(screenshotsDir, `${name}.png`),
    fullPage: false
  });
}

async function clickButton(page, name) {
  await page.getByRole('button', { name }).click();
}

async function completeProductionFlow(page) {
  await clickButton(page, /Радар/i);
  await clickButton(page, /Собрать инсайт/i);
  await clickButton(page, /В план/i);
  await clickButton(page, /Утвердить план/i);
  await clickButton(page, /Подготовить фабулу/i);
  await clickButton(page, /Утвердить фабулу/i);
}

async function completeReleaseFlow(page) {
  await clickButton(page, /Редактура/i);
  await clickButton(page, /Написать драфт/i);
  await clickButton(page, /Утвердить текст/i);
  await clickButton(page, /Финал/i);
  await screenshot(page, '06-editorial-review-final-text');

  await clickButton(page, /Выпуск/i);
  await clickButton(page, /Подготовить выпуск/i);
  for (const checkbox of await page.locator('.release-checklist input[type="checkbox"]').all()) {
    await checkbox.check();
  }
  await clickButton(page, /Готово к выпуску/i);
  const downloadPromise = page.waitForEvent('download');
  await clickButton(page, /Скачать Markdown/i);
  await downloadPromise;
  await screenshot(page, '07-release-manual-export');
}

async function main() {
  await rm(screenshotsDir, { recursive: true, force: true });
  await mkdir(screenshotsDir, { recursive: true });

  const server = runDevServer();
  let stderr = '';
  server.stderr.on('data', (chunk) => {
    stderr += chunk.toString();
  });

  try {
    await waitForServer();
    const browser = await chromium.launch();
    const page = await browser.newPage({
      viewport: { width: 1440, height: 1024 },
      locale: 'ru-RU',
      acceptDownloads: true
    });

    await page.goto(baseUrl, { waitUntil: 'networkidle' });
    await page.evaluate(() => window.localStorage.clear());
    await page.reload({ waitUntil: 'networkidle' });
    await page.getByText('Авторская память').first().waitFor();
    await screenshot(page, '01-author-memory-home');

    await clickButton(page, /Заголовок/i);
    await clickButton(page, /Файл/i);
    await screenshot(page, '02-author-memory-composer-title-file');

    await page.getByLabel('Тип записи').selectOption('linkReaction');
    await page.getByLabel('Ссылка').fill('https://example.com/ai-b2b-workflow-risk');
    await page.getByLabel('Заметка автора').fill('Ссылка полезна как пример: провал возникает не в модели, а в workflow adoption.');
    await screenshot(page, '03-author-memory-link-preview');

    await page.locator('summary', { hasText: 'Evidence' }).first().click();
    await page.getByRole('button', { name: /Корректировать evidence/i }).first().click();
    await screenshot(page, '04-author-memory-correction-evidence');

    await completeProductionFlow(page);
    await screenshot(page, '05-approved-post-brief');

    await completeReleaseFlow(page);

    await clickButton(page, /Аналитика/i);
    await clickButton(page, /Подготовить аналитику/i);
    await page.getByLabel('Что сработало').fill('Лучше сработали конкретные workflow-риски, а не общий рассказ про AI.');
    await clickButton(page, /Зафиксировать выводы/i);
    await screenshot(page, '08-analytics-learning-note');

    await browser.close();
  } catch (error) {
    console.error(stderr);
    throw error;
  } finally {
    server.kill();
  }

  if (!existsSync(path.join(screenshotsDir, '01-author-memory-home.png'))) {
    throw new Error('Screenshots were not created.');
  }
}

main().catch((error) => {
  console.error(error);
  process.exit(1);
});
