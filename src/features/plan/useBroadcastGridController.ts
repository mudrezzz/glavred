import { useMemo, useState } from 'react';
import type { ContentPlanItem, PlanWeightWarning } from '../../domain/editorialWorkspace';
import {
  DEFAULT_BROADCAST_GRID_FILTERS,
  filterBroadcastItems,
  groupBroadcastItems,
  type BroadcastGridFilters,
  type BroadcastGridGroupMode,
  type BroadcastGridViewMode
} from './broadcastGridFilters';

export function useBroadcastGridController(items: ContentPlanItem[], warnings: PlanWeightWarning[]) {
  const [filters, setFilters] = useState<BroadcastGridFilters>(DEFAULT_BROADCAST_GRID_FILTERS);
  const [viewMode, setViewMode] = useState<BroadcastGridViewMode>('list');
  const [groupMode, setGroupMode] = useState<BroadcastGridGroupMode>('date');
  const [selectedCalendarDate, setSelectedCalendarDate] = useState('');

  const filteredItems = useMemo(
    () => filterBroadcastItems(items, warnings, filters),
    [filters, items, warnings]
  );
  const groups = useMemo(
    () => groupBroadcastItems(filteredItems, warnings, groupMode),
    [filteredItems, groupMode, warnings]
  );

  return {
    filteredItems,
    filters,
    groupMode,
    groups,
    setFilters,
    selectedCalendarDate,
    setSelectedCalendarDate,
    setGroupMode,
    setViewMode,
    viewMode
  };
}
