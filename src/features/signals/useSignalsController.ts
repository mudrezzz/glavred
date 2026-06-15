import { useMemo, useState } from 'react';
import {
  createRadarDraft,
  isRadarSourceConfigurationValid,
  type ImportRiskLevel,
  type RadarDefinition,
  type RadarEditorialFilterRule,
  type RadarSearchRule,
  type RadarSearchSource,
  type SignalFilterStatus,
  type SignalReviewStatus,
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
  const [filterStatusFilter, setFilterStatusFilter] = useState<'all' | SignalFilterStatus>('all');
  const [riskFilter, setRiskFilter] = useState<'all' | ImportRiskLevel>('all');
  const [query, setQuery] = useState('');

  const signalCountsByRadar = useMemo(() => {
    return workspace.sourceSignals.reduce<Record<string, number>>((counts, signal) => {
      if (!signal.radarId) return counts;
      return { ...counts, [signal.radarId]: (counts[signal.radarId] ?? 0) + 1 };
    }, {});
  }, [workspace.sourceSignals]);

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
    if (filterStatusFilter !== 'all' && signal.filterStatus !== filterStatusFilter) return false;
    if (riskFilter !== 'all' && signal.duplicateRisk !== riskFilter) return false;
    if (query.trim() && !haystack.includes(query.trim().toLowerCase())) return false;
    return true;
  });

  const signalSummary = {
    total: workspace.sourceSignals.length,
    new: workspace.sourceSignals.filter((signal) => !signal.reviewStatus || signal.reviewStatus === 'new').length,
    approved: workspace.sourceSignals.filter((signal) => signal.reviewStatus === 'approved').length,
    archived: workspace.sourceSignals.filter((signal) => signal.reviewStatus === 'archived').length,
    highRisk: workspace.sourceSignals.filter((signal) => signal.duplicateRisk === 'high').length
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
      rawNote: editingSignal.rawNote,
      searchNote: editingSignal.searchNote,
      authorCorrection: editingSignal.authorCorrection
    });
    setEditingSignal(null);
  }

  return {
    tab, setTab, expandedRadarId, setExpandedRadarId, expandedSignalId, setExpandedSignalId,
    editingRadar, isNewRadar, editingSignal, setEditingSignal,
    radarFilter, setRadarFilter, statusFilter, setStatusFilter, filterStatusFilter,
    setFilterStatusFilter, riskFilter, setRiskFilter, query, setQuery,
    signalCountsByRadar, filteredSignals, signalSummary, openNewRadar, startRadarEdit,
    saveRadarDraft, cancelRadarDraft, patchRadarDraft, patchRadarRule, patchRadarFilter,
    addRadarRule, deleteRadarRule, patchRadarSource, addRadarSource, deleteRadarSource,
    startSignalEdit, patchSignalDraft, saveSignalDraft
  };
}

export type SignalsController = ReturnType<typeof useSignalsController>;
