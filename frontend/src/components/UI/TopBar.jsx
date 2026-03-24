/**
 * TopBar — application header with title, status, and toolbar buttons.
 */

import React from 'react'
import { useStore } from '../../store/useStore.js'
import styles from './TopBar.module.css'

const SatelliteIcon = () => (
  <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5">
    <path d="M13 2L3 14h9l-1 8 10-12h-9l1-8z"/>
  </svg>
)

export default function TopBar() {
  const {
    sidebarOpen, setSidebarOpen,
    chartOpen, setChartOpen,
    statsOpen, setStatsOpen,
    loading,
  } = useStore()

  return (
    <header className={styles.bar}>
      <div className={styles.left}>
        <button
          className={styles.menuBtn}
          onClick={() => setSidebarOpen(!sidebarOpen)}
          aria-label="Toggle sidebar"
        >
          <span className={styles.hamburger} data-open={sidebarOpen}>
            <span/><span/><span/>
          </span>
        </button>

        <div className={styles.brand}>
          <span className={styles.brandIcon}><SatelliteIcon /></span>
          <span className={styles.brandName}>Sentinel<span className={styles.brandAccent}>·2</span></span>
          <span className={styles.brandSub}>Vegetation Dashboard</span>
        </div>

        {loading && (
          <div className={styles.loadingBadge}>
            <span className={`${styles.loadingDot} animate-pulse`} />
            <span>Loading imagery…</span>
          </div>
        )}
      </div>

      <div className={styles.right}>
        <button
          className={`${styles.toolBtn} ${statsOpen ? styles.active : ''}`}
          onClick={() => setStatsOpen(!statsOpen)}
          title="Area statistics"
        >
          <StatsIcon /> Stats
        </button>

        <button
          className={`${styles.toolBtn} ${chartOpen ? styles.active : ''}`}
          onClick={() => setChartOpen(!chartOpen)}
          title="Time-series chart"
        >
          <ChartIcon /> Chart
        </button>

        <a
          className={styles.docsBtn}
          href="https://documentation.dataspace.copernicus.eu/APIs/SentinelHub.html"
          target="_blank"
          rel="noopener noreferrer"
        >
          API Docs
        </a>
      </div>
    </header>
  )
}

const StatsIcon = () => (
  <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
    <path d="M18 20V10M12 20V4M6 20v-6"/>
  </svg>
)

const ChartIcon = () => (
  <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
    <polyline points="22,12 18,12 15,21 9,3 6,12 2,12"/>
  </svg>
)
