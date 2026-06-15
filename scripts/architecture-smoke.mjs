import fs from "node:fs";
import path from "node:path";

const ROOT = process.cwd();

const APP_TSX_LIMIT = 1700;
const APP_TEST_TSX_LIMIT = 850;
const LARGE_APP_DECLARATION_LIMIT = 10;

const ADR_PATH =
  "docs/adr/2026-06-15-react-ui-uses-feature-modules-not-app-god-file.md";
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

const requiredSourceFiles = [
  "src/app/AppShell.tsx",
  "src/app/Sidebar.tsx",
  "src/app/Topbar.tsx",
  "src/app/navigation.ts",
  "src/app/useWorkspaceController.ts",
  "src/app/contextChatScope.ts",
  "src/shared/ui/Icon.tsx",
  "src/features/author-memory/AuthorMemoryView.tsx",
  "src/features/editorial-model/EditorialModelView.tsx",
  "src/features/signals/SignalsView.tsx",
];

for (const requiredFile of requiredSourceFiles) {
  assert(fileExists(requiredFile), `Missing React architecture source file: ${requiredFile}`);
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
