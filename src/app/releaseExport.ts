import {
  markReleaseExported,
  type ReleasePackage
} from '../domain/editorialWorkspace';

export function markManualExportDone(releasePackage: ReleasePackage): ReleasePackage {
  return {
    ...releasePackage,
    checklist: releasePackage.checklist.map((item) =>
      item.id === 'manual-exported' ? { ...item, done: true } : item
    )
  };
}

export async function copyToClipboard(value: string): Promise<void> {
  if (navigator.clipboard?.writeText) {
    try {
      await navigator.clipboard.writeText(value);
    } catch {
      // Markdown preview stays visible for manual copy when clipboard access is unavailable.
    }
  }
}

export function downloadMarkdown(releasePackage: ReleasePackage): void {
  if (!window.URL?.createObjectURL) return;

  const blob = new Blob([releasePackage.markdown], { type: 'text/markdown;charset=utf-8' });
  const url = window.URL.createObjectURL(blob);
  const link = document.createElement('a');
  link.href = url;
  link.download = `${releasePackage.id}.md`;
  link.click();
  window.URL.revokeObjectURL(url);
}

export function markReleaseManuallyExported(releasePackage: ReleasePackage): ReleasePackage {
  return markReleaseExported(markManualExportDone(releasePackage));
}
