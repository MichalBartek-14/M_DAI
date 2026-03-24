/**
 * Sidebar — the main control panel.
 * Sections: Index selector, Date range, AOI input, Cloud cover, Presets, Run.
 */

import React, { useState } from 'react'
import toast from 'react-hot-toast'

import { useStore }         from '../../store/useStore.js'
import { computeIndex, fetchTimeseries } from '../../services/api.js'
import { INDEX_META, PRESET_CONFIGS }    from '../../utils/indexMeta.js'

import IndexSelector  from './IndexSelector.jsx'
import DateRangePicker from './DateRangePicker.jsx'
import AoiInput       from './AoiInput.jsx'
import CloudSlider    from './CloudSlider.jsx'
import PresetButtons  from './PresetButtons.jsx'
import ExportButtons  from './ExportButtons.jsx'

import styles from './Sidebar.module.css'

export default function Sidebar() {
  const {
    selectedIndex, startDate, endDate, aoi,
    cloudCoverMax, timeseriesIndices,
    setLoading, setError,
    setTileUrl, setScenes, setTimeseries, setAreaStats,
  } = useStore()

  const [running, setRunning] = useState(false)

  async function handleRun() {
    if (!aoi) {
      toast.error('Draw an area of interest on the map first')
      return
    }

    setRunning(true)
    setLoading(true, 'Querying Sentinel-2 scenes…')

    try {
      // 1. Compute index + get tile URL
      const result = await computeIndex({
        aoi,
        startDate,
        endDate,
        index: selectedIndex,
        cloudCoverMax,
      })

      setTileUrl(result.tile_url)
      setScenes(result.scenes)
      setAreaStats(result.stats)

      toast.success(`Found ${result.scene_count} scene${result.scene_count !== 1 ? 's' : ''}`)

      // 2. Fetch time-series in parallel
      setLoading(true, 'Computing time-series…')
      const ts = await fetchTimeseries({
        aoi,
        startDate,
        endDate,
        indices: timeseriesIndices.includes(selectedIndex)
          ? timeseriesIndices
          : [...timeseriesIndices, selectedIndex],
        cloudCoverMax,
      })
      setTimeseries(ts)

    } catch (err) {
      toast.error(err.message)
      setError(err.message)
    } finally {
      setRunning(false)
      setLoading(false)
    }
  }

  return (
    <div className={styles.sidebar}>
      <div className={styles.scroll}>

        {/* ── Presets ─────────────────────────────────────────────────── */}
        <section className={styles.section}>
          <h3 className={styles.sectionTitle}>Quick Presets</h3>
          <PresetButtons />
        </section>

        <div className={styles.divider} />

        {/* ── Index ───────────────────────────────────────────────────── */}
        <section className={styles.section}>
          <h3 className={styles.sectionTitle}>Spectral Index</h3>
          <IndexSelector />
        </section>

        <div className={styles.divider} />

        {/* ── Date range ──────────────────────────────────────────────── */}
        <section className={styles.section}>
          <h3 className={styles.sectionTitle}>Date Range</h3>
          <DateRangePicker />
        </section>

        <div className={styles.divider} />

        {/* ── AOI ─────────────────────────────────────────────────────── */}
        <section className={styles.section}>
          <h3 className={styles.sectionTitle}>Area of Interest</h3>
          <AoiInput />
        </section>

        <div className={styles.divider} />

        {/* ── Cloud cover ─────────────────────────────────────────────── */}
        <section className={styles.section}>
          <h3 className={styles.sectionTitle}>Cloud Cover Filter</h3>
          <CloudSlider />
        </section>

        <div className={styles.divider} />

        {/* ── Export ──────────────────────────────────────────────────── */}
        <section className={styles.section}>
          <h3 className={styles.sectionTitle}>Export</h3>
          <ExportButtons />
        </section>

      </div>

      {/* ── Run button (sticky footer) ───────────────────────────────── */}
      <div className={styles.footer}>
        <button
          className={`${styles.runBtn} ${running ? styles.running : ''}`}
          onClick={handleRun}
          disabled={running}
        >
          {running ? (
            <>
              <span className={`${styles.spinner} animate-spin`} />
              Analyzing…
            </>
          ) : (
            <>
              <RunIcon />
              Run Analysis
            </>
          )}
        </button>
      </div>
    </div>
  )
}

const RunIcon = () => (
  <svg width="15" height="15" viewBox="0 0 24 24" fill="currentColor">
    <path d="M8 5v14l11-7z"/>
  </svg>
)
