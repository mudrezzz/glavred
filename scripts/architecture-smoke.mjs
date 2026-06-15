import fs from "node:fs";
import path from "node:path";

const ROOT = process.cwd();

const APP_TSX_LIMIT = 350;
const APP_TEST_TSX_LIMIT = 850;
const LARGE_APP_DECLARATION_LIMIT = 1;

const LARGE_SOURCE_BASELINES = [
  {
    path: "src/features/author-memory/AuthorMemoryView.tsx",
    limit: 320,
    next: "AuthorMemoryView must stay a feature composition root; put feed/import orchestration in feature-local hooks and views.",
  },
  {
    path: "src/features/author-memory/useMemoryFeedController.ts",
    limit: 280,
    next: "Memory feed state should stay in this hook or be split by composer/edit/correction role.",
  },
  {
    path: "src/features/author-memory/useImportReviewController.ts",
    limit: 300,
    next: "Import review state should stay in this hook or be split by queue/archive role.",
  },
  {
    path: "src/features/author-memory/MemoryFeedTab.tsx",
    limit: 260,
    next: "MemoryFeedTab should stay focused on composer, toolbar, and feed rendering.",
  },
  {
    path: "src/features/author-memory/MemorySidePanel.tsx",
    limit: 140,
    next: "MemorySidePanel should stay summary/assertion-only.",
  },
  {
    path: "src/features/author-memory/MemoryDialogs.tsx",
    limit: 120,
    next: "MemoryDialogs should stay limited to author-memory modal/confirmation surfaces.",
  },
  {
    path: "src/domain/editorialWorkspace.ts",
    limit: 170,
    next: "editorialWorkspace.ts must remain a thin compatibility barrel.",
  },
  {
    path: "src/features/editorial-model/EditorialModelView.tsx",
    limit: 220,
    next: "Editorial model internals must keep moving into feature-local tab/panel modules.",
  },
  {
    path: "src/fixtures/demoWorkspace.ts",
    limit: 120,
    next: "demoWorkspace.ts must remain the public demo factory, not the fixture owner.",
  },
  {
    path: "src/features/signals/SignalsView.tsx",
    limit: 180,
    next: "SignalsView must stay a composition root; keep radar/signal state and tab UI in feature-local modules.",
  },
  {
    path: "src/features/signals/useSignalsController.ts",
    limit: 280,
    next: "Signals tab/filter/edit state should stay in this hook or be split by radar/signal role.",
  },
  {
    path: "src/features/signals/RadarsTab.tsx",
    limit: 220,
    next: "RadarsTab should stay focused on toolbar, new radar editor, and radar list composition.",
  },
  {
    path: "src/features/signals/RadarCard.tsx",
    limit: 240,
    next: "RadarCard should stay focused on one radar row/detail/edit surface.",
  },
  {
    path: "src/features/signals/FoundSignalsTab.tsx",
    limit: 220,
    next: "FoundSignalsTab should stay focused on filter toolbar and signal list composition.",
  },
  {
    path: "src/features/signals/SourceSignalCard.tsx",
    limit: 260,
    next: "SourceSignalCard should stay focused on one found signal row/detail/edit surface.",
  },
  {
    path: "src/features/signals/SignalsHeader.tsx",
    limit: 100,
    next: "SignalsHeader should stay focused on section title and header metrics.",
  },
  {
    path: "src/features/signals/SignalsTabs.tsx",
    limit: 80,
    next: "SignalsTabs should stay focused on tab switching only.",
  },
  {
    path: "src/features/signals/PostCandidatesPreviewTab.tsx",
    limit: 120,
    next: "PostCandidatesPreviewTab should stay a read-only Slice 1.6 placeholder.",
  },
  {
    path: "src/application/editorialServices.ts",
    limit: 20,
    next: "editorialServices.ts must remain a compatibility barrel.",
  },
  {
    path: "src/domain/editorial-model/transitions.ts",
    limit: 20,
    next: "If editorial-model transitions grow, split them by rules, topics, fabulas, matrix, and validators.",
  },
  {
    path: "src/domain/editorial-model/rules.ts",
    limit: 50,
    next: "Editorial rule transitions should stay small and role-owned.",
  },
  {
    path: "src/domain/editorial-model/validation.ts",
    limit: 460,
    next: "If editorial validation grows, split individual validators into dedicated modules.",
  },
  {
    path: "src/domain/editorial-model/catalog.ts",
    limit: 190,
    next: "Topic/fabula/matrix transitions should stay catalog-owned.",
  },
  {
    path: "src/features/author-memory/ImportViews.tsx",
    limit: 20,
    next: "ImportViews.tsx must remain a feature-local compatibility barrel.",
  },
  {
    path: "src/features/author-memory/ExternalSourcesView.tsx",
    limit: 190,
    next: "External source UI should stay separate from memory feed and import queue logic.",
  },
  {
    path: "src/features/author-memory/ImportQueueView.tsx",
    limit: 340,
    next: "If import queue grows, split filters, bulk toolbar, and selection state helpers.",
  },
  {
    path: "src/features/author-memory/CandidateCard.tsx",
    limit: 170,
    next: "CandidateCard should stay focused on one imported candidate.",
  },
  {
    path: "src/features/author-memory/ArchiveView.tsx",
    limit: 150,
    next: "Archive UI should stay separate from import queue review logic.",
  },
  {
    path: "src/features/author-memory/BulkActionDialog.tsx",
    limit: 130,
    next: "Bulk action confirmation should stay a small dialog component.",
  },
  {
    path: "src/features/editorial-model/EditorialModelParts.tsx",
    limit: 20,
    next: "EditorialModelParts.tsx must remain a feature-local compatibility barrel.",
  },
  {
    path: "src/features/editorial-model/ProjectProfileHeader.tsx",
    limit: 160,
    next: "Project profile header must stay separate from rules, topics, and matrix UI.",
  },
  {
    path: "src/features/editorial-model/PublisherRulesView.tsx",
    limit: 260,
    next: "Publisher rules UI should stay focused on rules and rule editing.",
  },
  {
    path: "src/features/editorial-model/TopicsTab.tsx",
    limit: 310,
    next: "Topics tab should be split again if topic editor/list behavior grows.",
  },
  {
    path: "src/features/editorial-model/FabulasTab.tsx",
    limit: 310,
    next: "Fabulas tab should be split again if fabula editor/list behavior grows.",
  },
  {
    path: "src/features/editorial-model/MatrixTab.tsx",
    limit: 140,
    next: "Matrix UI should stay focused on compatibility editing.",
  },
  {
    path: "src/features/signals/RadarEditor.tsx",
    limit: 270,
    next: "Radar editor should stay separate from signals list and side panel UI.",
  },
  {
    path: "src/features/signals/SignalsSidePanel.tsx",
    limit: 100,
    next: "Signals side panel should stay compact and summary-focused.",
  },
  {
    path: "src/fixtures/demoImports.ts",
    limit: 410,
    next: "If import demo data grows, split it by sources, candidates, archive, and bulk examples.",
  },
];

const ADR_PATH =
  "docs/adr/2026-06-15-react-ui-uses-feature-modules-not-app-god-file.md";
const MODULE_GUARDRAILS_ADR_PATH =
  "docs/adr/2026-06-15-domain-feature-modules-have-size-boundary-guardrails.md";
const FEATURE_INTERNALS_ADR_PATH =
  "docs/adr/2026-06-15-feature-entrypoints-stay-thin-and-domain-transitions-are-role-owned.md";
const SAO_PATH = "docs/architecture/SYSTEM_ARCHITECTURE_OVERVIEW.md";

function readText(relativePath) {
  return fs.readFileSync(path.join(ROOT, relativePath), "utf8");
}

function lineCount(text) {
  return text.split(/\r?\n/).length;
}

function fileExists(relativePath) {
  return fs.existsSync(path.join(ROOT, relativePath));
}

function listFiles(dir, extensions) {
  const absoluteDir = path.join(ROOT, dir);
  if (!fs.existsSync(absoluteDir)) {
    return [];
  }

  const entries = fs.readdirSync(absoluteDir, { withFileTypes: true });
  return entries.flatMap((entry) => {
    const fullPath = path.join(absoluteDir, entry.name);
    const relativePath = path.relative(ROOT, fullPath).replaceAll(path.sep, "/");

    if (entry.isDirectory()) {
      return listFiles(relativePath, extensions);
    }

    return extensions.some((extension) => entry.name.endsWith(extension)) ? [relativePath] : [];
  });
}

const failures = [];

function assert(condition, message) {
  if (!condition) {
    failures.push(message);
  }
}

const appSource = readText("src/App.tsx");
const appTestSource = readText("src/App.test.tsx");
const appLines = lineCount(appSource);
const appTestLines = lineCount(appTestSource);

assert(
  appLines <= APP_TSX_LIMIT,
  `src/App.tsx has ${appLines} lines; temporary limit is ${APP_TSX_LIMIT}. Extract UI before adding more.`
);

assert(
  appTestLines <= APP_TEST_TSX_LIMIT,
  `src/App.test.tsx has ${appTestLines} lines; temporary limit is ${APP_TEST_TSX_LIMIT}. Split tests before adding more.`
);

const largeDeclarationPattern =
  /^(?:export\s+)?function\s+([A-Z][A-Za-z0-9]*(?:View|Editor|Panel|Overlay|Card|Header|Sidebar|Topbar))\b/gm;
const largeDeclarations = [...appSource.matchAll(largeDeclarationPattern)].map(
  (match) => match[1]
);

assert(
  largeDeclarations.length <= LARGE_APP_DECLARATION_LIMIT,
  [
    `src/App.tsx has ${largeDeclarations.length} large UI declarations; temporary limit is ${LARGE_APP_DECLARATION_LIMIT}.`,
    `New declarations: ${largeDeclarations.join(", ")}`,
  ].join("\n")
);

assert(fileExists(ADR_PATH), `Missing ADR: ${ADR_PATH}`);
assert(
  fileExists(MODULE_GUARDRAILS_ADR_PATH),
  `Missing ADR: ${MODULE_GUARDRAILS_ADR_PATH}`
);
assert(
  fileExists(FEATURE_INTERNALS_ADR_PATH),
  `Missing ADR: ${FEATURE_INTERNALS_ADR_PATH}`
);

const requiredSourceFiles = [
  "src/app/AppShell.tsx",
  "src/app/Sidebar.tsx",
  "src/app/Topbar.tsx",
  "src/app/navigation.ts",
  "src/app/useWorkspaceController.ts",
  "src/app/contextChatScope.ts",
  "src/shared/ui/Icon.tsx",
  "src/features/author-memory/AuthorMemoryView.tsx",
  "src/features/author-memory/useMemoryFeedController.ts",
  "src/features/author-memory/useImportReviewController.ts",
  "src/features/author-memory/MemoryFeedTab.tsx",
  "src/features/author-memory/MemorySidePanel.tsx",
  "src/features/author-memory/MemoryDialogs.tsx",
  "src/features/author-memory/ImportViews.tsx",
  "src/features/author-memory/ExternalSourcesView.tsx",
  "src/features/author-memory/ImportQueueView.tsx",
  "src/features/author-memory/CandidateCard.tsx",
  "src/features/author-memory/ArchiveView.tsx",
  "src/features/author-memory/BulkActionDialog.tsx",
  "src/features/author-memory/components.tsx",
  "src/features/author-memory/helpers.ts",
  "src/features/editorial-model/EditorialModelView.tsx",
  "src/features/editorial-model/EditorialModelParts.tsx",
  "src/features/editorial-model/ProjectProfileHeader.tsx",
  "src/features/editorial-model/PublisherRulesView.tsx",
  "src/features/editorial-model/TopicsTab.tsx",
  "src/features/editorial-model/FabulasTab.tsx",
  "src/features/editorial-model/MatrixTab.tsx",
  "src/features/editorial-model/ValidationPanel.tsx",
  "src/features/editorial-model/helpers.ts",
  "src/features/signals/SignalsView.tsx",
  "src/features/signals/useSignalsController.ts",
  "src/features/signals/SignalsHeader.tsx",
  "src/features/signals/SignalsTabs.tsx",
  "src/features/signals/RadarsTab.tsx",
  "src/features/signals/RadarCard.tsx",
  "src/features/signals/FoundSignalsTab.tsx",
  "src/features/signals/SourceSignalCard.tsx",
  "src/features/signals/PostCandidatesPreviewTab.tsx",
  "src/features/signals/RadarEditor.tsx",
  "src/features/signals/SignalsSidePanel.tsx",
  "src/features/signals/helpers.tsx",
  "src/features/plan/PlanView.tsx",
  "src/features/briefing/BriefView.tsx",
  "src/features/editing/EditView.tsx",
  "src/features/release/ReleaseView.tsx",
  "src/features/analytics/AnalyticsView.tsx",
];

for (const requiredFile of requiredSourceFiles) {
  assert(fileExists(requiredFile), `Missing React architecture source file: ${requiredFile}`);
}

const largeSourceStats = [];

for (const baseline of LARGE_SOURCE_BASELINES) {
  assert(fileExists(baseline.path), `Missing large-file baseline target: ${baseline.path}`);

  if (fileExists(baseline.path)) {
    const lines = lineCount(readText(baseline.path));
    largeSourceStats.push({ ...baseline, lines });
    assert(
      lines <= baseline.limit,
      [
        `${baseline.path} has ${lines} lines; temporary limit is ${baseline.limit}.`,
        baseline.next,
      ].join("\n")
    );
  }
}

assert(
  !appSource.includes("LocalWorkspaceStore"),
  "src/App.tsx must not import or instantiate LocalWorkspaceStore; use src/app/useWorkspaceController.ts."
);

const forbiddenAppSignalsSymbols = [
  "function SignalsViewV2",
  "function RadarEditor",
  "function SignalsSidePanel",
  "function RadarView",
  "createRadarDraft",
  "isRadarSourceConfigurationValid",
  "radarSourceTypeLabel",
  "signalReviewStatusLabel",
];

for (const symbol of forbiddenAppSignalsSymbols) {
  assert(
    !appSource.includes(symbol),
    `src/App.tsx must not contain signals feature internals: ${symbol}. Use src/features/signals.`
  );
}

const signalsViewSource = readText("src/features/signals/SignalsView.tsx");
const forbiddenSignalsViewSymbols = [
  "function openNewRadar",
  "function saveRadarDraft",
  "filteredSignals",
  "function startSignalEdit",
  "function patchRadarRule",
  "function patchRadarSource",
];

for (const symbol of forbiddenSignalsViewSymbols) {
  assert(
    !signalsViewSource.includes(symbol),
    `src/features/signals/SignalsView.tsx must not contain signals internals: ${symbol}. Use useSignalsController or feature-local tab/entity modules.`
  );
}

const forbiddenAppEditorialModelSymbols = [
  "function EditorialModelView",
  "function TopicEditor",
  "function FabulaEditor",
  "function TopicFabulaMatrixView",
  "function EditorialValidationPanel",
  "createEditorialRule",
  "createTopicDraft",
  "createFabulaDraft",
];

for (const symbol of forbiddenAppEditorialModelSymbols) {
  assert(
    !appSource.includes(symbol),
    `src/App.tsx must not contain editorial-model feature internals: ${symbol}. Use src/features/editorial-model.`
  );
}

const forbiddenAppAuthorMemorySymbols = [
  "function AuthorMemoryView",
  "function AuthorNoteCard",
  "function AssertionCard",
  "function ExternalSourcesView",
  "function ImportQueueView",
  "function ArchiveView",
  "function BulkActionDialog",
  "createAuthorMemoryEvent",
  "filterAuthorNotes",
  "getImportSummary",
  "sourceTypeLabel",
  "reviewStatusLabel",
];

for (const symbol of forbiddenAppAuthorMemorySymbols) {
  assert(
    !appSource.includes(symbol),
    `src/App.tsx must not contain author-memory feature internals: ${symbol}. Use src/features/author-memory.`
  );
}

const authorMemoryViewSource = readText("src/features/author-memory/AuthorMemoryView.tsx");
const forbiddenAuthorMemoryEntrypointSymbols = [
  "function submitNote",
  "function saveEdit",
  "function performBulkAction",
  "function acceptArchiveRecordToMemory",
  "function restoreArchiveRecordToQueue",
  "function deleteArchiveRecord",
];

for (const symbol of forbiddenAuthorMemoryEntrypointSymbols) {
  assert(
    !authorMemoryViewSource.includes(symbol),
    `AuthorMemoryView.tsx must not contain author-memory orchestration internals: ${symbol}. Use feature-local hooks.`
  );
}

const forbiddenAppProductionSymbols = [
  "function PlanView",
  "function BriefView",
  "function EditView",
  "function ReleaseView",
  "function AnalyticsView",
  "function HitlGate",
  "function FieldInput",
  "function CheckCard",
  "function FinalTextView",
];

for (const symbol of forbiddenAppProductionSymbols) {
  assert(
    !appSource.includes(symbol),
    `src/App.tsx must not contain production-flow feature internals: ${symbol}. Use src/features/* and src/shared/* modules.`
  );
}

const featureFiles = listFiles("src/features", [".ts", ".tsx"]);
const importPattern = /from\s+["']([^"']+)["']/g;

for (const featureFile of featureFiles) {
  const [, featureName] = featureFile.match(/^src\/features\/([^/]+)\//) ?? [];
  if (!featureName) {
    continue;
  }

  const source = readText(featureFile);
  for (const match of source.matchAll(importPattern)) {
    const importPath = match[1];
    let resolvedImport = importPath;

    if (importPath.startsWith(".")) {
      resolvedImport = path
        .relative(ROOT, path.resolve(ROOT, path.dirname(featureFile), importPath))
        .replaceAll(path.sep, "/");
    }

    const [, importedFeature] =
      resolvedImport.match(/^src\/features\/([^/]+)/) ??
      importPath.match(/^src\/features\/([^/]+)/) ??
      [];

    if (!importedFeature) {
      continue;
    }

    assert(
      importedFeature === featureName,
      `${featureFile} imports another feature (${importedFeature}); feature -> feature imports are forbidden.`
    );
  }
}

const saoSource = readText(SAO_PATH);
const requiredSaoFragments = [
  "## React UI Architecture",
  "src/app/",
  "src/features/author-memory",
  "src/features/editorial-model",
  "src/features/signals",
  "src/features/plan",
  "src/features/briefing",
  "src/features/editing",
  "src/features/release",
  "src/features/analytics",
  "src/features/context-chat",
  "src/shared/ui",
  "src/shared/format",
  "features -> shared/application/domain",
  "no feature -> feature",
  "Large-file guardrails",
  "Feature entrypoints stay thin",
  "Domain transitions are role-owned",
  "domain/application/fixtures/feature files must shrink through the 1.5.x refactoring chain",
];

for (const fragment of requiredSaoFragments) {
  assert(
    saoSource.includes(fragment),
    `SAO is missing required React architecture fragment: ${fragment}`
  );
}

if (failures.length > 0) {
  console.error("Architecture smoke failed:");
  for (const failure of failures) {
    console.error(`- ${failure}`);
  }
  process.exit(1);
}

console.log("Architecture smoke passed.");
console.log(`- src/App.tsx: ${appLines}/${APP_TSX_LIMIT} lines`);
console.log(`- src/App.test.tsx: ${appTestLines}/${APP_TEST_TSX_LIMIT} lines`);
console.log(
  `- Large App.tsx UI declarations: ${largeDeclarations.length}/${LARGE_APP_DECLARATION_LIMIT}`
);
for (const stat of largeSourceStats) {
  console.log(`- ${stat.path}: ${stat.lines}/${stat.limit} lines`);
}
