import type { AuthorNoteType } from '../../domain/editorialWorkspace';

export type MemoryInternalTab = 'feed' | 'sources' | 'queue' | 'archive';
export type MemoryTypeFilter = AuthorNoteType | 'all';
export type CorrectionTarget = {
  type: 'assertion' | 'evidence';
  id: string;
  title: string;
};
export type PendingCorrectionConflict = {
  noteId: string;
  targetTitle: string;
};
export type ImportViewMode = 'list' | 'groups';
export type PendingBulkAction = {
  action: 'archive' | 'reject';
  candidateIds: string[];
  destination: string;
};
export type LinkPreview = {
  isValid: boolean;
  domain: string;
  normalizedUrl: string;
  title: string;
};
export type SpeechRecognitionEventLike = {
  results: {
    [index: number]: {
      [index: number]: {
        transcript: string;
      };
    };
  };
};
export type SpeechRecognitionLike = {
  lang: string;
  interimResults: boolean;
  onresult: ((event: SpeechRecognitionEventLike) => void) | null;
  start: () => void;
};
export type SpeechRecognitionWindow = Window &
  typeof globalThis & {
    SpeechRecognition?: new () => SpeechRecognitionLike;
    webkitSpeechRecognition?: new () => SpeechRecognitionLike;
  };
