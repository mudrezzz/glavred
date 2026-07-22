import { chromium } from '@playwright/test';
import { spawn, spawnSync } from 'node:child_process';

const rootDir = process.cwd();
const port = process.env.DESIGN_SMOKE_PORT ?? '4182';
const baseUrl = `http://127.0.0.1:${port}`;

function runDevServer() {
  const npmCommand = process.platform === 'win32' ? 'npm.cmd' : 'npm';
  return spawn(npmCommand, ['run', 'dev', '--', '--host', '127.0.0.1', '--port', port, '--strictPort'], {
    cwd: rootDir,
    detached: process.platform !== 'win32',
    env: { ...process.env, BROWSER: 'none' },
    shell: process.platform === 'win32',
    stdio: ['ignore', 'pipe', 'pipe']
  });
}

function stopDevServer(server) {
  if (process.platform === 'win32' && server.pid) {
    spawnSync('taskkill', ['/pid', String(server.pid), '/T', '/F'], { stdio: 'ignore' });
    return;
  }
  if (!server.pid) return;
  try {
    process.kill(-server.pid, 'SIGTERM');
  } catch {
    server.kill();
  }
}

async function waitForServer() {
  const startedAt = Date.now();
  while (Date.now() - startedAt < 30000) {
    try {
      const response = await fetch(baseUrl);
      if (response.ok) return;
    } catch {
      // Vite is still starting.
    }
    await new Promise((resolve) => setTimeout(resolve, 500));
  }
  throw new Error(`Vite did not start at ${baseUrl}`);
}

function failIfAny(title, failures) {
  if (failures.length) {
    throw new Error(`${title} failed:\n- ${failures.join('\n- ')}`);
  }
}

function sharedDesignChecks() {
  function numberFromPx(value) {
    return Number.parseFloat(value || '0') || 0;
  }

  function minSameLineGap(elements) {
    const rects = Array.from(elements)
      .map((element) => element.getBoundingClientRect())
      .filter((rect) => rect.width > 0 && rect.height > 0)
      .sort((a, b) => a.top - b.top || a.left - b.left);
    const gaps = rects
      .slice(1)
      .map((rect, index) => ({ rect, prev: rects[index] }))
      .filter(({ rect, prev }) => Math.abs(rect.top - prev.top) < 8)
      .map(({ rect, prev }) => Math.round(rect.left - prev.right));
    return gaps.length ? Math.min(...gaps) : null;
  }

  function cardPaddingFailures() {
    const failures = [];
    const selectors = [
      '.project-profile-header',
      '.signals-section-header',
      '.panel',
      '.card:not(.signal-card):not(.radar-card):not(.broadcast-row):not(.editorial-work-row)'
    ];
    document.querySelectorAll(selectors.join(',')).forEach((element) => {
      const rect = element.getBoundingClientRect();
      if (rect.width < 80 || rect.height < 40) return;
      const style = window.getComputedStyle(element);
      const left = numberFromPx(style.paddingLeft);
      const right = numberFromPx(style.paddingRight);
      const top = numberFromPx(style.paddingTop);
      const bottom = numberFromPx(style.paddingBottom);
      if (Math.min(left, right, top, bottom) < 14) {
        failures.push(`${element.className || element.tagName}: padding is too small (${top}/${right}/${bottom}/${left}).`);
      }
    });
    return failures;
  }

  function columnGapFailures() {
    const failures = [];
    document.querySelectorAll('.memory-grid, .editorial-workspace, .signals-workspace-grid').forEach((grid) => {
      const children = Array.from(grid.children).filter((child) => {
        const rect = child.getBoundingClientRect();
        return rect.width > 0 && rect.height > 0;
      });
      if (children.length < 2) return;
      const [first, second] = children;
      const firstRect = first.getBoundingClientRect();
      const secondRect = second.getBoundingClientRect();
      const verticalOverlap = firstRect.bottom > secondRect.top && secondRect.bottom > firstRect.top;
      const sameRow = verticalOverlap || Math.abs(firstRect.top - secondRect.top) < 80;
      if (!sameRow) return;
      const gap = Math.round(secondRect.left - firstRect.right);
      const requiredGap = grid.classList.contains('signals-workspace-grid') ? 28 : 16;
      if (gap < requiredGap) {
        failures.push(`${grid.className}: main/side gap is too small (${gap}px).`);
      }
    });
    return failures;
  }

  function mainContentOverflowFailures() {
    const failures = [];
    document.querySelectorAll('.signals-workspace-grid').forEach((grid) => {
      const main = grid.querySelector('.memory-main');
      const side = grid.querySelector('.memory-side');
      if (!main || !side) return;
      const mainRect = main.getBoundingClientRect();
      const sideRect = side.getBoundingClientRect();
      const sameRow = mainRect.bottom > sideRect.top && sideRect.bottom > mainRect.top;
      const allowedRight = sameRow ? Math.min(mainRect.right, sideRect.left - 28) : mainRect.right;

      main.querySelectorAll(':scope > *').forEach((child) => {
        const rect = child.getBoundingClientRect();
        if (rect.width < 20 || rect.height < 20) return;
        if (rect.right > allowedRight + 1) {
          failures.push(
            `${child.className || child.tagName}: overflows Signals main column by ${Math.round(rect.right - allowedRight)}px.`
          );
        }
      });
    });
    return failures;
  }

  function actionGapFailures() {
    const failures = [];
    document
      .querySelectorAll('.row-actions, .inline-actions, .entity-actions, .composer-actions, .entity-actions-footer, .source-row-actions')
      .forEach((group) => {
        const buttons = group.querySelectorAll('button, .btn');
        if (buttons.length < 2) return;
        const minGap = minSameLineGap(buttons);
        if (minGap !== null && minGap < 8) {
          failures.push(`${group.className}: action gap is too small (${minGap}px).`);
        }
      });
    return failures;
  }

  function pageOverflowFailure() {
    const overflow = document.documentElement.scrollWidth - document.documentElement.clientWidth;
    return overflow > 2 ? [`page overflows horizontally by ${overflow}px.`] : [];
  }

  return [
    ...pageOverflowFailure(),
    ...cardPaddingFailures(),
    ...columnGapFailures(),
    ...mainContentOverflowFailures(),
    ...actionGapFailures()
  ];
}

function colorToRgb(value) {
  const match = value.match(/rgba?\((\d+),\s*(\d+),\s*(\d+)/);
  return match ? [Number(match[1]), Number(match[2]), Number(match[3])] : null;
}

function contrastRatio(foreground, background) {
  function luminance([red, green, blue]) {
    const channels = [red, green, blue].map((channel) => {
      const value = channel / 255;
      return value <= 0.03928 ? value / 12.92 : ((value + 0.055) / 1.055) ** 2.4;
    });
    return 0.2126 * channels[0] + 0.7152 * channels[1] + 0.0722 * channels[2];
  }

  const lighter = Math.max(luminance(foreground), luminance(background));
  const darker = Math.min(luminance(foreground), luminance(background));
  return (lighter + 0.05) / (darker + 0.05);
}

async function assertCommonDesign(page, label) {
  const failures = await page.evaluate(sharedDesignChecks);
  failIfAny(`${label} design contract`, failures);
}

async function assertSignalsDesign(page, viewportName) {
  await page.locator('[data-testid="signals-section-header"]').waitFor();
  const baseFailures = await page.evaluate(sharedDesignChecks);
  const specificFailures = await page.evaluate(() => {
    const failures = [];
    const header = document.querySelector('[data-testid="signals-section-header"]');
    const tabs = document.querySelector('.signal-tabs');
    const tabCount = tabs?.querySelector('.tab-count');
    const headerStats = header?.querySelector('.signals-header-stats');
    const radarToolbar = document.querySelector('[data-testid="signals-radar-toolbar"]');
    const radarEditor = document.querySelector('.radar-editor');
    const firstFormInput = radarEditor?.querySelector('.signal-edit-form input, .signal-edit-form textarea, .signal-edit-form select');
    const firstConfigSection = radarEditor?.querySelector('.radar-config-section');

    if (!header?.classList.contains('project-profile-header')) {
      failures.push('signals header does not reuse project-profile-header pattern.');
    }

    if (header && headerStats) {
      const headerRect = header.getBoundingClientRect();
      const statsRect = headerStats.getBoundingClientRect();
      const lastStat = Array.from(headerStats.children).at(-1);
      const rightGap = Math.round(headerRect.right - statsRect.right);
      if (rightGap < 12 || rightGap > 32) {
        failures.push(`signals header metrics are not aligned to the right edge (${rightGap}px).`);
      }
      if (lastStat) {
        const lastStatRect = lastStat.getBoundingClientRect();
        const lastStatGap = Math.round(headerRect.right - lastStatRect.right);
        if (lastStatGap < 12 || lastStatGap > 32) {
          failures.push(`signals header visible metric cards are not aligned to the right edge (${lastStatGap}px).`);
        }
      }
    }

    if (!tabCount) {
      failures.push('signals tab count badge is missing.');
    } else {
      const rect = tabCount.getBoundingClientRect();
      const style = window.getComputedStyle(tabCount);
      const marginLeft = Number.parseFloat(style.marginLeft || '0') || 0;
      if (rect.width < 22 || rect.height < 22 || marginLeft < 6) {
        failures.push(`signals tab count badge is malformed (${Math.round(rect.width)}x${Math.round(rect.height)}, margin ${marginLeft}px).`);
      }
    }

    if (radarToolbar) {
      const title = radarToolbar.querySelector('.entity-toolbar-copy h2');
      const description = radarToolbar.querySelector('.entity-toolbar-copy p');
      const action = radarToolbar.querySelector('[data-testid="add-radar-button"]');
      if (!title || !description) {
        failures.push('signals radar toolbar does not use canonical count + description copy.');
      }
      if (!action) {
        failures.push('signals radar toolbar add action is missing.');
      } else if (action.classList.contains('btn-pri')) {
        failures.push('ordinary + Radar action uses validation/primary button styling.');
      }
      if (action) {
        const toolbarRect = radarToolbar.getBoundingClientRect();
        const actionRect = action.getBoundingClientRect();
        const rightGap = Math.round(toolbarRect.right - actionRect.right);
        if (rightGap < -1 || rightGap > 4) {
          failures.push(`signals radar toolbar action is not aligned to the right edge (${rightGap}px).`);
        }
      }
    }

    document.querySelectorAll('.entity-list-toolbar button').forEach((button) => {
      const label = button.textContent?.trim() ?? '';
      if (label.startsWith('+') && button.classList.contains('btn-pri')) {
        failures.push(`ordinary create button "${label}" uses btn-pri.`);
      }
    });

    document.querySelectorAll('[data-testid="radar-row"] .radar-row-main').forEach((row) => {
      const rowRect = row.getBoundingClientRect();
      const meta = row.querySelector('.radar-row-meta');
      const status = row.querySelector('.radar-status');
      const date = row.querySelector('.radar-date');
      const title = row.querySelector('.radar-title');
      const description = row.querySelector('.radar-row-sub');
      if (!meta || !status || !date || !title || !description || meta.children.length < 3) {
        failures.push('radar row is missing title/description/status/count/date structure.');
        return;
      }
      const dateText = date.textContent?.trim() ?? '';
      if (dateText === 'last run' || dateText.length <= 'last run'.length) {
        failures.push('radar row date slot is empty instead of showing a fallback.');
      }
      const metaRect = meta.getBoundingClientRect();
      if (metaRect.right > rowRect.right + 1) {
        failures.push('radar row metadata overflows the row.');
      }
      const statusRect = status.getBoundingClientRect();
      const dateRect = date.getBoundingClientRect();
      if (statusRect.right > rowRect.right + 1 || dateRect.right > metaRect.right + 1) {
        failures.push('radar row status or date overflows its owner.');
      }
      const titleStyle = getComputedStyle(title);
      if (titleStyle.textOverflow === 'ellipsis' || titleStyle.whiteSpace === 'nowrap') {
        failures.push('radar title is truncated instead of wrapping to its full value.');
      }
    });

    if (radarEditor && firstFormInput && firstConfigSection) {
      const inputRect = firstFormInput.getBoundingClientRect();
      const sectionRect = firstConfigSection.getBoundingClientRect();
      if (Math.abs(inputRect.left - sectionRect.left) > 2 || Math.abs(inputRect.right - sectionRect.right) > 2) {
        failures.push('radar editor grouped sections are not aligned with base fields.');
      }
    }

    if (radarEditor) {
      const embeddedEditor = document.querySelector('[data-testid="radar-row"] .radar-editor');
      const topLevelEditor = radarEditor.closest('[data-testid="radar-row"]') ? null : radarEditor;
      if (topLevelEditor && !topLevelEditor.closest('[data-testid="radar-list"]')) {
        failures.push('radar editor is detached from the edited radar row.');
      }
      if (embeddedEditor) {
        const ruleTextareas = embeddedEditor.querySelectorAll('.radar-rule-edit textarea');
        if (ruleTextareas.length === 0) {
          failures.push('inline radar editor does not use textarea for radar search rules.');
        }
        embeddedEditor.querySelectorAll('.radar-source-edit').forEach((sourceEdit) => {
          if (!sourceEdit.querySelector('textarea')) {
            failures.push('inline radar editor does not use textarea for radar source values.');
          }
        });
      }

      const blocks = Array.from(radarEditor.querySelectorAll('.signal-edit-form > label, .signal-edit-form > .form-grid-3'))
        .map((element) => element.getBoundingClientRect())
        .filter((rect) => rect.width > 0 && rect.height > 0)
        .sort((a, b) => a.top - b.top);
      blocks.slice(1).forEach((rect, index) => {
        const prev = blocks[index];
        const gap = Math.round(rect.top - prev.bottom);
        if (gap < 12) {
          failures.push(`radar editor form rhythm is too tight between fields (${gap}px).`);
        }
      });

      radarEditor.querySelectorAll('.form-grid-3 label').forEach((label) => {
        const labelText = label.querySelector('span');
        const control = label.querySelector('input, select, textarea');
        if (!labelText || !control) return;
        const labelRect = labelText.getBoundingClientRect();
        const controlRect = control.getBoundingClientRect();
        const gap = Math.round(controlRect.top - labelRect.bottom);
        if (gap < 6) {
          failures.push(`radar editor field label touches control (${gap}px).`);
        }
      });
    }

    return failures;
  });

  failIfAny(`${viewportName} signals design`, [...baseFailures, ...specificFailures]);
}

async function assertPlanDesign(page) {
  await page.locator('[data-testid="broadcast-filter-toolbar"]').waitFor();
  const baseFailures = await page.evaluate(sharedDesignChecks);
  const planFailures = await page.evaluate(() => {
    const failures = [];
    function colorToRgb(value) {
      const match = value.match(/rgba?\((\d+),\s*(\d+),\s*(\d+)/);
      return match ? [Number(match[1]), Number(match[2]), Number(match[3])] : null;
    }
    function contrastRatio(foreground, background) {
      function luminance([red, green, blue]) {
        const channels = [red, green, blue].map((channel) => {
          const value = channel / 255;
          return value <= 0.03928 ? value / 12.92 : ((value + 0.055) / 1.055) ** 2.4;
        });
        return 0.2126 * channels[0] + 0.7152 * channels[1] + 0.0722 * channels[2];
      }
      const lighter = Math.max(luminance(foreground), luminance(background));
      const darker = Math.min(luminance(foreground), luminance(background));
      return (lighter + 0.05) / (darker + 0.05);
    }
    const header = document.querySelector('.gate');
    const tabs = document.querySelector('.plan-mode-tabs');
    const filterCard = document.querySelector('[data-testid="broadcast-filter-toolbar"]');
    const grid = document.querySelector('[data-testid="broadcast-grid"]');
    const main = document.querySelector('.broadcast-main');
    const side = document.querySelector('.broadcast-aside');

    if (!tabs?.classList.contains('tabs') || tabs.querySelectorAll('.tab').length < 2) {
      failures.push('plan mode switcher does not use canonical .tabs .tab structure.');
    }
    if (!filterCard?.querySelector('.compact-tabs .tab:nth-child(3)')) {
      failures.push('broadcast grid calendar view tab is missing from the filter toolbar.');
    }
    if (header && tabs && tabs.getBoundingClientRect().top <= header.getBoundingClientRect().bottom) {
      failures.push('plan mode tabs are not placed below the plan header.');
    }
    if (!filterCard || !grid) {
      failures.push('broadcast grid filter card or list is missing.');
    } else if (filterCard.getBoundingClientRect().top > grid.getBoundingClientRect().top) {
      failures.push('broadcast grid filter card is not before the list.');
    }
    if (main && side) {
      const mainRect = main.getBoundingClientRect();
      const sideRect = side.getBoundingClientRect();
      document.querySelectorAll('.broadcast-main > *').forEach((child) => {
        const rect = child.getBoundingClientRect();
        if (rect.width > 20 && rect.right > sideRect.left - 20) {
          failures.push(`${child.className || child.tagName}: overflows broadcast main column.`);
        }
      });
      if (mainRect.right > sideRect.left - 20) {
        failures.push('broadcast main and side columns are too close.');
      }
    }
    document.querySelectorAll('.broadcast-row-main').forEach((row) => {
      const rect = row.getBoundingClientRect();
      row.querySelectorAll(':scope > *').forEach((child) => {
        const childRect = child.getBoundingClientRect();
        if (childRect.right > rect.right + 1) {
          failures.push('broadcast row child overflows row bounds.');
        }
      });
    });
    document.querySelectorAll('.validation-warnings p').forEach((paragraph) => {
      const textColor = colorToRgb(window.getComputedStyle(paragraph).color);
      const backgroundColor = colorToRgb(window.getComputedStyle(paragraph.parentElement).backgroundColor);
      if (textColor && backgroundColor && contrastRatio(textColor, backgroundColor) < 4.5) {
        failures.push('validation warning text contrast is below 4.5.');
      }
    });
    return failures;
  });

  failIfAny('plan design contract', [...baseFailures, ...planFailures]);
}

async function assertEditingDesign(page) {
  await page.locator('[data-testid="editorial-section-header"]').waitFor();
  const baseFailures = await page.evaluate(sharedDesignChecks);
  const editingFailures = await page.evaluate(() => {
    const failures = [];
    const header = document.querySelector('[data-testid="editorial-section-header"]');
    const headerStats = header?.querySelector('.signals-header-stats');
    const asideSummary = document.querySelector('.editorial-side .editorial-summary-grid');
    const isWorkbenchMode = Boolean(document.querySelector('[data-testid="editorial-workbench-picker"]'));

    if (!header?.classList.contains('project-profile-header')) {
      failures.push('editing header does not reuse project-profile-header padding pattern.');
    }

    if (header) {
      const style = window.getComputedStyle(header);
      const paddingLeft = Number.parseFloat(style.paddingLeft || '0') || 0;
      const paddingTop = Number.parseFloat(style.paddingTop || '0') || 0;
      if (paddingLeft < 20 || paddingTop < 20) {
        failures.push(`editing header padding is too small (${paddingTop}/${paddingLeft}px).`);
      }
    }

    if (header && headerStats) {
      const headerRect = header.getBoundingClientRect();
      const statsRect = headerStats.getBoundingClientRect();
      const rightGap = Math.round(headerRect.right - statsRect.right);
      if (rightGap < 12 || rightGap > 32) {
        failures.push(`editing header metrics are not aligned to the right edge (${rightGap}px).`);
      }
      headerStats.querySelectorAll(':scope > div').forEach((card) => {
        const rect = card.getBoundingClientRect();
        const style = window.getComputedStyle(card);
        if (rect.width < 90 || rect.height < 50 || style.backgroundColor === 'rgba(0, 0, 0, 0)') {
          failures.push('editing header metric card does not use the compact metric-card pattern.');
        }
      });
    }

    if (!isWorkbenchMode && !asideSummary) {
      failures.push('editing side panel does not use the shared summary metric grid.');
    } else if (asideSummary) {
      asideSummary.querySelectorAll('.summary-item').forEach((item) => {
        const value = item.querySelector('b');
        const label = item.querySelector('span');
        if (!value || !label) {
          failures.push('editing side summary item does not use b/span metric structure.');
        }
      });
    }

    if (document.querySelector('.editorial-workbench-head')) {
      failures.push('editing workbench renders a redundant top post header.');
    }

    if (isWorkbenchMode) {
      const picker = document.querySelector('[data-testid="editorial-workbench-picker"]');
      if (!picker?.querySelector('select[aria-label="Выбор поста"]')) {
        failures.push('editing workbench picker must use a single select combobox.');
      }
      if (picker?.querySelector('input') || picker?.querySelector('.picker-results')) {
        failures.push('editing workbench picker must not render input plus separate result rows.');
      }
    }

    return failures;
  });

  failIfAny('editing design contract', [...baseFailures, ...editingFailures]);
}

async function captureSignalsLayout(page) {
  await page.evaluate(async () => {
    await document.fonts.ready;
  });
  return page.evaluate(() => {
    const selectors = {
      header: '[data-testid="signals-section-header"]',
      tabs: '.signal-tabs',
      grid: '.signals-workspace-grid',
      main: '.signals-workspace-grid .memory-main',
      side: '.signals-workspace-grid .memory-side',
      toolbar: '[data-testid="signals-radar-toolbar"]',
      firstRadar: '[data-testid="radar-row"]'
    };

    return Object.fromEntries(
      Object.entries(selectors).map(([key, selector]) => {
        const element = document.querySelector(selector);
        if (!element) return [key, null];
        const rect = element.getBoundingClientRect();
        return [
          key,
          {
            left: Math.round(rect.left),
            right: Math.round(rect.right),
            width: Math.round(rect.width),
            top: Math.round(rect.top)
          }
        ];
      })
    );
  });
}

function assertStableSignalsLayout(before, after, label) {
  const failures = [];
  ['header', 'tabs', 'grid', 'main', 'side', 'toolbar', 'firstRadar'].forEach((key) => {
    const beforeRect = before[key];
    const afterRect = after[key];
    if (!beforeRect || !afterRect) return;
    ['left', 'right', 'width'].forEach((axis) => {
      const delta = Math.abs(afterRect[axis] - beforeRect[axis]);
      if (delta > 1) {
        failures.push(`${key}.${axis} shifted by ${delta}px.`);
      }
    });
  });
  failIfAny(`${label} layout stability`, failures);
}

async function installAiRunTraceMocks(page) {
  const draftRun = {
    id: 'draft-run-smoke',
    status: 'succeeded',
    inputSummary: { title: 'Trace smoke' },
    steps: [
      step('context', { workItem: { title: 'Trace smoke post' } }),
      step('rulePack', { hardConstraints: [{ text: 'No hype' }] }),
      step('materialPlan', { materialPlan: { availableEvidence: ['signal'], missingEvidence: ['benchmark'] }, aiRunId: 'ai-material' }),
      step('strategy', { draftStrategy: { thesisAngle: 'workflow before model', openingMove: 'pilot gap' }, aiRunId: 'ai-strategy' }),
      step('draft', {
        progress: {
          status: 'succeeded',
          currentOperationId: null,
          operations: [{
            id: 'draft-candidate-research',
            kind: 'draftCandidate',
            label: 'Generate candidate: research',
            status: 'succeeded',
            startedAt: '2026-06-19T00:00:00+00:00',
            completedAt: '2026-06-19T00:00:01+00:00',
            aiRunId: 'ai-candidate',
            target: 'research'
          }]
        },
        candidates: [{ id: 'candidate-1', title: 'Candidate', body: 'Body', aiRunId: 'ai-candidate' }],
        selection: { selectedCandidateId: 'candidate-1', rationale: 'Best score' }
      }),
      step('validation', { status: 'placeholder-passed' }),
      step('complete', { status: 'succeeded' })
    ],
    finalDraft: { title: 'Selected draft', body: 'Selected body' },
    error: null,
    aiRunIds: ['ai-material', 'ai-strategy', 'ai-candidate'],
    createdAt: '2026-06-19T00:00:00+00:00',
    updatedAt: '2026-06-19T00:00:03+00:00'
  };
  const aiRuns = Object.fromEntries(draftRun.aiRunIds.map((id) => [id, aiRun(id)]));

  await page.route('**/api/draft-runs/**', (route) => route.fulfill({ status: 200, json: draftRun }));
  await page.route('**/api/ai-runs/**', (route) => {
    const id = route.request().url().split('/').pop();
    return route.fulfill({ status: aiRuns[id] ? 200 : 404, json: aiRuns[id] ?? { detail: 'not found' } });
  });

  function step(key, artifactPayload) {
    return {
      key,
      status: 'succeeded',
      title: key,
      artifactPayload,
      error: null,
      startedAt: '2026-06-19T00:00:00+00:00',
      completedAt: '2026-06-19T00:00:01+00:00'
    };
  }

  function aiRun(id) {
    const draftRunStep = id === 'ai-candidate' ? 'draftCandidate' : id.replace('ai-', '');
    return {
      id,
      capability: 'draftGeneration',
      status: 'succeeded',
      provider: 'openrouter',
      model: 'deepseek/deepseek-v3.2',
      requestPayload: {
        draftRunStep,
        providerRequest: {
          messages: [
            { role: 'system', content: 'Return JSON' },
            { role: 'user', content: JSON.stringify({ task: draftRunStep, input: 'trace smoke payload' }) }
          ]
        }
      },
      resultPayload: { draftRunStep, result: { thesisAngle: 'angle' } },
      error: null,
      fallbackUsed: false,
      createdAt: '2026-06-19T00:00:00+00:00',
      updatedAt: '2026-06-19T00:00:01+00:00'
    };
  }
}

async function assertAiRunTraceDesign(page) {
  await page.goto(`${baseUrl}/ai-runs?runId=draft-run-smoke`, { waitUntil: 'domcontentloaded' });
  await page.locator('[data-testid="ai-run-timeline"]').waitFor();
  const failures = await page.evaluate(() => {
    const result = [];
    const tabs = document.querySelector('.ai-run-main-tabs');
    const detailTabs = document.querySelector('.ai-run-detail-tabs');
    const detail = document.querySelector('[data-testid="ai-run-detail-panel"]');
    const timeline = document.querySelector('[data-testid="ai-run-timeline"]');
    const jsonTabs = document.querySelector('.ai-run-json-tabs');

    if (!tabs?.classList.contains('tabs') || tabs.querySelectorAll('.tab').length < 2) {
      result.push('AI run trace top tabs do not use canonical .tabs .tab.');
    }
    if (!detailTabs?.classList.contains('tabs') || detailTabs.querySelectorAll('.tab').length < 3) {
      result.push('AI run trace detail tabs do not use canonical .tabs .tab.');
    }
    if (jsonTabs) {
      result.push('AI run trace still renders custom JSON tabs.');
    }
    [detail, timeline].forEach((element) => {
      if (!element) return;
      const style = window.getComputedStyle(element);
      const minPadding = Math.min(
        Number.parseFloat(style.paddingTop || '0') || 0,
        Number.parseFloat(style.paddingRight || '0') || 0,
        Number.parseFloat(style.paddingBottom || '0') || 0,
        Number.parseFloat(style.paddingLeft || '0') || 0
      );
      if (minPadding < 18) {
        result.push(`${element.className}: AI run trace panel padding is too small (${minPadding}px).`);
      }
    });
    const overflow = document.documentElement.scrollWidth - document.documentElement.clientWidth;
    if (overflow > 2) result.push(`AI run trace page overflows horizontally by ${overflow}px.`);
    document.querySelectorAll('.ai-run-child-calls button').forEach((button) => {
      const rect = button.getBoundingClientRect();
      const parentRect = button.closest('.ai-run-timeline-step')?.getBoundingClientRect();
      if (rect.height > 120) {
        result.push(`AI run child call row is too tall (${Math.round(rect.height)}px).`);
      }
      if (parentRect && rect.right > parentRect.right + 1) {
        result.push('AI run child call overflows its timeline step.');
      }
      if (!button.querySelector('.ai-run-call-meta')) {
        result.push('AI run child call does not render compact metadata.');
      }
    });
    document.querySelectorAll('.ai-run-operation').forEach((operation) => {
      const rect = operation.getBoundingClientRect();
      const parentRect = operation.closest('.ai-run-timeline-step')?.getBoundingClientRect();
      if (parentRect && rect.right > parentRect.right + 1) {
        result.push('AI run operation overflows its timeline step.');
      }
    });
    return result;
  });
  failIfAny('AI run trace design contract', [...await page.evaluate(sharedDesignChecks), ...failures]);
}

async function openDefaultProjectCabinet(page) {
  const button = page.getByRole('button', { name: 'Открыть кабинет' }).first();
  if (await button.count()) {
    await button.click();
  }
  await page.locator('.app').waitFor({ timeout: 10000 });
}

async function main() {
  const server = runDevServer();
  let stderr = '';
  server.stderr.on('data', (chunk) => {
    stderr += chunk.toString();
  });

  try {
    await waitForServer();
    const browser = await chromium.launch();
    const page = await browser.newPage({ viewport: { width: 1440, height: 1024 } });
    await page.route(/https:\/\/fonts\.(?:googleapis|gstatic)\.com\/.*/, (route) => route.abort());
    await page.goto(baseUrl, { waitUntil: 'domcontentloaded' });
    await page.evaluate(() => window.localStorage.clear());
    await page.reload({ waitUntil: 'domcontentloaded' });
    await openDefaultProjectCabinet(page);

    await page.locator('.nav-item').nth(1).click();
    await page.locator('.project-profile-header').waitFor();
    await assertCommonDesign(page, 'editorial model');

    await page.locator('.nav-item').nth(2).click();
    await page.locator('[data-testid="radar-row"]').first().waitFor();
    await assertSignalsDesign(page, 'desktop');

    const expandedLayout = await captureSignalsLayout(page);
    await page.locator('[data-testid="radar-row"]').first().locator('.radar-row-main').click();
    const collapsedLayout = await captureSignalsLayout(page);
    assertStableSignalsLayout(expandedLayout, collapsedLayout, 'desktop radar collapse');
    await page.locator('[data-testid="radar-row"]').first().locator('.radar-row-main').click();
    const reexpandedLayout = await captureSignalsLayout(page);
    assertStableSignalsLayout(expandedLayout, reexpandedLayout, 'desktop radar expand');

    await page.locator('[data-testid="add-radar-button"]').click();
    await page.locator('.radar-editor input').first().fill('Тестовый радар без даты');
    await page.locator('.radar-editor .btn-pri').click();
    await page.getByText('Тестовый радар без даты').waitFor();
    await assertSignalsDesign(page, 'desktop added radar');

    const firstRadarRow = page.locator('[data-testid="radar-row"]').first();
    await firstRadarRow.locator('.radar-row-main').click();
    await firstRadarRow.locator('.radar-actions .btn').first().click();
    await firstRadarRow.locator('.radar-editor').waitFor();
    await assertSignalsDesign(page, 'desktop radar editor');

    await page.locator('.signal-tabs .tab').nth(1).click();
    await page.locator('[data-testid="source-signal-row"]').first().waitFor();
    await assertSignalsDesign(page, 'desktop found signals');

    await page.getByRole('button', { name: /План/ }).click();
    await assertPlanDesign(page);
    await page.locator('[data-testid="broadcast-filter-toolbar"] .compact-tabs .tab').nth(2).click();
    await page.locator('[data-testid="broadcast-calendar-view"]').waitFor();
    await assertCommonDesign(page, 'plan calendar view');

    await page.locator('.nav-item').nth(4).click();
    await assertEditingDesign(page);
    await page.getByRole('tab', { name: /Рабочий стол/ }).click();
    await assertEditingDesign(page);

    await installAiRunTraceMocks(page);
    await assertAiRunTraceDesign(page);
    await page.goto(baseUrl, { waitUntil: 'domcontentloaded' });
    await openDefaultProjectCabinet(page);

    await page.setViewportSize({ width: 2048, height: 1100 });
    await page.reload({ waitUntil: 'domcontentloaded' });
    await openDefaultProjectCabinet(page);
    await page.locator('.nav-item').nth(2).click();
    await page.locator('[data-testid="signals-section-header"]').waitFor();
    await assertSignalsDesign(page, 'wide desktop');

    await page.setViewportSize({ width: 1180, height: 820 });
    await page.reload({ waitUntil: 'domcontentloaded' });
    await openDefaultProjectCabinet(page);
    await page.locator('.nav-item').nth(2).click();
    await page.locator('[data-testid="radar-row"]').first().waitFor();
    await assertSignalsDesign(page, 'laptop');

    await browser.close();
  } catch (error) {
    console.error(stderr);
    throw error;
  } finally {
    stopDevServer(server);
  }
}

main().catch((error) => {
  console.error(error);
  process.exit(1);
});
