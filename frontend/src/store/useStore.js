/**
 * Global application state — Zustand store.
 *
 * Manages: selected index, date range, AOI geometry,
 * map layers, time-series data, and UI panels.
 */

import { create } from 'zustand'
import { subMonths, format } from 'date-fns'

const today = new Date()
const sixMonthsAgo = subMonths(today, 6)

const fmt = (d) => format(d, 'yyyy-MM-dd')

export const useStore = create((set, get) => ({
  // ── Selected index ──────────────────────────────────────────────────────
  selectedIndex: 'NDVI',
  setSelectedIndex: (index) => set({ selectedIndex: index, tileUrl: null }),

  // ── Date range ──────────────────────────────────────────────────────────
  startDate: fmt(sixMonthsAgo),
  endDate:   fmt(today),
  setStartDate: (d) => set({ startDate: d }),
  setEndDate:   (d) => set({ endDate: d }),

  // ── AOI (drawn polygon or bbox input) ───────────────────────────────────
  aoi: null,           // { type: 'bbox'|'geojson', data: {...} }
  setAoi: (aoi) => set({ aoi, tileUrl: null, timeseries: null }),
  clearAoi: () => set({ aoi: null, tileUrl: null, timeseries: null }),

  // ── Map state ───────────────────────────────────────────────────────────
  tileUrl: null,       // XYZ tile URL template string
  setTileUrl: (url) => set({ tileUrl: url }),

  mapCenter: [20, 0],
  mapZoom:   3,
  setMapView: (center, zoom) => set({ mapCenter: center, mapZoom: zoom }),

  opacity: 0.8,
  setOpacity: (v) => set({ opacity: v }),

  compareMode: false,
  compareDate: null,
  setCompareMode: (v) => set({ compareMode: v }),
  setCompareDate: (d) => set({ compareDate: d }),

  // ── Index metadata ──────────────────────────────────────────────────────
  indexMeta: {},
  setIndexMeta: (meta) => set({ indexMeta: meta }),

  // ── Scene list ──────────────────────────────────────────────────────────
  scenes: [],
  setScenes: (scenes) => set({ scenes }),

  // ── Statistics ──────────────────────────────────────────────────────────
  areaStats: null,
  setAreaStats: (stats) => set({ areaStats: stats }),

  // ── Time-series ─────────────────────────────────────────────────────────
  timeseries: null,    // { NDVI: [...], NDWI: [...], ... }
  setTimeseries: (ts) => set({ timeseries: ts }),
  timeseriesIndices: ['NDVI'],
  setTimeseriesIndices: (indices) => set({ timeseriesIndices: indices }),

  // ── Loading / error state ───────────────────────────────────────────────
  loading: false,
  loadingMsg: '',
  setLoading: (loading, msg = '') => set({ loading, loadingMsg: msg }),

  error: null,
  setError: (error) => set({ error }),

  // ── UI panel visibility ─────────────────────────────────────────────────
  sidebarOpen: true,
  setSidebarOpen: (v) => set({ sidebarOpen: v }),

  chartOpen: true,
  setChartOpen: (v) => set({ chartOpen: v }),

  statsOpen: false,
  setStatsOpen: (v) => set({ statsOpen: v }),

  activePreset: null,
  setActivePreset: (p) => set({ activePreset: p }),

  // ── Cloud cover filter ──────────────────────────────────────────────────
  cloudCoverMax: 30,
  setCloudCoverMax: (v) => set({ cloudCoverMax: v }),
}))
