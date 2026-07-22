import { useMemo, useState } from 'react';
import {
  createRadarDraft,
  isRadarSourceConfigurationValid,
  summarizeRadarRun,
  type FoundMaterial,
  type RadarDefinition,
  type RadarRun,
  type RadarEditorialFilterRule,
  type RadarSearchRule,
  type RadarSearchSource,
  type SignalUtilityRecommendation,
  type SignalReviewStatus,
  type SourceHandle,
  type SourceSignal,
  type WorkspaceState
} from '../../domain/editorialWorkspace';
import type { SignalsTab } from './helpers';

export function useSignalsController({
  workspace,
  onSaveRadar,
  onCorrectSignal
}: {
  workspace: WorkspaceState;
  onSaveRadar: (radar: RadarDefinition, isNew: boolean) => void;
  onCorrectSignal: (signal: SourceSignal, patch: Partial<SourceSignal>) => void;
}) {
  const [tab, setTab] = useState<SignalsTab>('radars');
  const [expandedRadarId, setExpandedRadarId] = useState(workspace.radars[0]?.id ?? '');
  const [expandedSignalId, setExpandedSignalId] = useState(workspace.sourceSignals[0]?.id ?? '');
  const [editingRadar, setEditingRadar] = useState<RadarDefinition | null>(null);
  const [isNewRadar, setIsNewRadar] = useState(false);
  const [editingSignal, setEditingSignal] = useState<SourceSignal | null>(null);
  const [radarFilter, setRadarFilter] = useState('all');
  const [statusFilter, setStatusFilter] = useState<'all' | SignalReviewStatus>('all');
  const [filterStatusFilter, setFilterStatusFilter] = useState<'all' | SignalUtilityRecommendation | 'unscored' | 'legacy'>('all');
  const [query, setQuery] = useState('');

  const signalCountsByRadar = useMemo(() => {
    return workspace.sourceSignals.reduce<Record<string, number>>((counts, signal) => {
      if (!signal.radarId) return counts;
      return { ...counts, [signal.radarId]: (counts[signal.radarId] ?? 0) + 1 };
    }, {});
  }, [workspace.sourceSignals]);

  const latestRunsByRadar = useMemo(() => {
    return workspace.radarRuns.reduce<Record<string, RadarRun>>((runs, run) => {
      const current = runs[run.radarId];
      if (!current || run.startedAt > current.startedAt) return { ...runs, [run.radarId]: run };
      return runs;
    }, {});
  }, [workspace.radarRuns]);

  const sourceHandlesByRadar = useMemo(() => {
    const byId = new Map(workspace.sourceRegistry.handles.map((handle) => [handle.id, handle]));
    return workspace.radars.reduce<Record<string, SourceHandle[]>>((handles, radar) => {
      const radarHandles = (radar.sourceHandleIds ?? [])
        .map((id) => byId.get(id))
        .filter((handle): handle is SourceHandle => Boolean(handle));
      return { ...handles, [radar.id]: radarHandles };
    }, {});
  }, [workspace.radars, workspace.sourceRegistry.handles]);

  const foundMaterialsByRun = useMemo(() => {
    return workspace.foundMaterials.reduce<Record<string, FoundMaterial[]>>((materials, material) => ({
      ...materials,
      [material.radarRunId]: [...(materials[material.radarRunId] ?? []), material]
    }), {});
  }, [workspace.foundMaterials]);

  const radarRunSummaries = useMemo(() => {
    return workspace.radars.reduce<Record<string, ReturnType<typeof summarizeRadarRun>>>((summaries, radar) => ({
      ...summaries,
      [radar.id]: summarizeRadarRun(latestRunsByRadar[radar.id])
    }), {});
  }, [latestRunsByRadar, workspace.radars]);

  const filteredSignals = workspace.sourceSignals.filter((signal) => {
    const haystack = [
      signal.title,
      signal.summary,
      signal.rawNote,
      signal.source,
      signal.searchNote ?? '',
      ...(signal.evidence ?? []).flatMap((item) => [item.sourceTitle, item.quote, item.summary])
    ]
      .join(' ')
      .toLowerCase();

    if (radarFilter !== 'all' && signal.radarId !== radarFilter) return false;
    if (statusFilter !== 'all' && signal.reviewStatus !== statusFilter) return false;
    const utilityState = signal.legacyIntegrityStatus === 'needsReExtraction'
      ? 'legacy'
      : signal.utilityReport?.recommendation ?? 'unscored';
    if (filterStatusFilter !== 'all' && utilityState !== filterStatusFilter) return false;
    if (query.trim() && !haystack.includes(query.trim().toLowerCase())) return false;
    return true;
  });

  const signalSummary = {
    total: workspace.sourceSignals.length,
    new: workspace.sourceSignals.filter((signal) => !signal.reviewStatus || signal.reviewStatus === 'new' || signal.reviewStatus === 'candidate').length,
    approved: workspace.sourceSignals.filter((signal) => signal.reviewStatus === 'approved').length,
    archived: workspace.sourceSignals.filter((signal) => signal.reviewStatus === 'archived').length,
    relationshipGroups: new Set(
      workspace.sourceSignals
        .map((signal) => signal.relationshipReport ?? signal.utilityReport?.relationshipReport)
        .filter((report) => report?.status === 'checked')
        .map((report) => report?.canonicalSignalId)
        .filter(Boolean)
    ).size
  };

  function openNewRadar() {
    if (editingRadar && isNewRadar) return;
    setEditingRadar(createRadarDraft());
    setIsNewRadar(true);
    setExpandedRadarId('');
  }

  function startRadarEdit(radar: RadarDefinition) {
    setEditingRadar(structuredClone(radar));
    setIsNewRadar(false);
    setExpandedRadarId(radar.id);
  }

  function saveRadarDraft() {
    if (!editingRadar || !editingRadar.title.trim()) return;
    if (!isRadarSourceConfigurationValid(editingRadar)) return;
    onSaveRadar(editingRadar, isNewRadar);
    setExpandedRadarId(editingRadar.id);
    setEditingRadar(null);
    setIsNewRadar(false);
  }

  function cancelRadarDraft() {
    setEditingRadar(null);
    setIsNewRadar(false);
  }

  function patchRadarDraft(patch: Partial<RadarDefinition>) {
    setEditingRadar((current) => (current ? { ...current, ...patch } : current));
  }

  function patchRadarRule(ruleId: string, patch: Partial<RadarSearchRule>) {
    setEditingRadar((current) => current ? { ...current, rules: current.rules.map((rule) => (rule.id === ruleId ? { ...rule, ...patch } : rule)) } : current);
  }

  function patchRadarFilter(filterId: string, patch: Partial<RadarEditorialFilterRule>) {
    setEditingRadar((current) => current ? { ...current, filters: (current.filters ?? []).map((filter) => (filter.id === filterId ? { ...filter, ...patch } : filter)) } : current);
  }

  function addRadarRule() {
    setEditingRadar((current) => current ? { ...current, rules: [...current.rules, { id: `radar-rule-${Date.now()}`, operator: 'and', negate: false, statement: '', status: 'active' }] } : current);
  }

  function deleteRadarRule(ruleId: string) {
    setEditingRadar((current) => current ? { ...current, rules: current.rules.filter((rule) => rule.id !== ruleId) } : current);
  }

  function patchRadarSource(sourceId: string, patch: Partial<RadarSearchSource>) {
    setEditingRadar((current) => current ? { ...current, sources: current.sources.map((source) => (source.id === sourceId ? { ...source, ...patch } : source)) } : current);
  }

  function addRadarSource() {
    setEditingRadar((current) => current ? { ...current, sources: [...current.sources, { id: `radar-source-${Date.now()}`, type: 'openWeb', title: '', value: '', notes: '', status: 'active' }] } : current);
  }

  function deleteRadarSource(sourceId: string) {
    setEditingRadar((current) => current ? { ...current, sources: current.sources.filter((source) => source.id !== sourceId) } : current);
  }

  function startSignalEdit(signal: SourceSignal) {
    setEditingSignal({ ...signal });
    setExpandedSignalId(signal.id);
  }

  function patchSignalDraft(patch: Partial<SourceSignal>) {
    setEditingSignal((current) => (current ? { ...current, ...patch } : current));
  }

  function saveSignalDraft() {
    if (!editingSignal) return;
    onCorrectSignal(editingSignal, {
      title: editingSignal.title,
      summary: editingSignal.summary,
      authorCorrection: editingSignal.authorCorrection
    });
    setEditingSignal(null);
  }

  return {
    tab, setTab, expandedRadarId, setExpandedRadarId, expandedSignalId, setExpandedSignalId,
    editingRadar, isNewRadar, editingSignal, setEditingSignal,
    radarFilter, setRadarFilter, statusFilter, setStatusFilter, filterStatusFilter,
    setFilterStatusFilter, query, setQuery,
    signalCountsByRadar, filteredSignals, signalSummary, openNewRadar, startRadarEdit,
    latestRunsByRadar, sourceHandlesByRadar, foundMaterialsByRun, radarRunSummaries,
    saveRadarDraft, cancelRadarDraft, patchRadarDraft, patchRadarRule, patchRadarFilter,
    addRadarRule, deleteRadarRule, patchRadarSource, addRadarSource, deleteRadarSource,
    startSignalEdit, patchSignalDraft, saveSignalDraft
  };
}

export type SignalsController = ReturnType<typeof useSignalsController>;
