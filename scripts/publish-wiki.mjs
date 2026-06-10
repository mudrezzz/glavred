import { execFileSync } from 'node:child_process';
import { existsSync } from 'node:fs';
import { cp, mkdir, readdir, rm } from 'node:fs/promises';
import os from 'node:os';
import path from 'node:path';

const rootDir = process.cwd();
const wikiSourceDir = path.join(rootDir, 'docs', 'wiki');
const publishDir = path.join(os.tmpdir(), 'glavred-wiki-publish');
const wikiRemote = process.env.GITHUB_WIKI_REMOTE ?? 'https://github.com/mudrezzz/glavred.wiki.git';

function git(args, options = {}) {
  return execFileSync('git', args, {
    cwd: options.cwd ?? rootDir,
    encoding: 'utf8',
    stdio: options.stdio ?? 'pipe'
  });
}

async function emptyDirectoryExceptGit(directory) {
  for (const entry of await readdir(directory, { withFileTypes: true })) {
    if (entry.name === '.git') {
      continue;
    }
    await rm(path.join(directory, entry.name), { recursive: true, force: true });
  }
}

async function main() {
  if (!existsSync(wikiSourceDir)) {
    throw new Error('docs/wiki does not exist. Run the wiki documentation slice first.');
  }

  await rm(publishDir, { recursive: true, force: true });
  await mkdir(publishDir, { recursive: true });

  try {
    git(['clone', wikiRemote, publishDir], { stdio: 'inherit' });
  } catch {
    await rm(publishDir, { recursive: true, force: true });
    await mkdir(publishDir, { recursive: true });
    git(['init'], { cwd: publishDir, stdio: 'inherit' });
    git(['remote', 'add', 'origin', wikiRemote], { cwd: publishDir, stdio: 'inherit' });
  }

  await emptyDirectoryExceptGit(publishDir);
  await cp(wikiSourceDir, publishDir, { recursive: true });

  git(['add', '.'], { cwd: publishDir, stdio: 'inherit' });
  const status = git(['status', '--porcelain'], { cwd: publishDir });
  if (!status.trim()) {
    console.log('GitHub Wiki is already up to date.');
    return;
  }

  git(['commit', '-m', 'Update Glavred user wiki'], { cwd: publishDir, stdio: 'inherit' });
  git(['push', '-u', 'origin', 'master'], { cwd: publishDir, stdio: 'inherit' });
}

main().catch((error) => {
  console.error(error);
  process.exit(1);
});
