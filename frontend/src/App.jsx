/**
 * Root App component — lays out the dashboard shell.
 *
 * Layout:
 *   ┌─────────────────────────────────────────────────────┐
 *   │  TopBar                                             │
 *   ├───────────┬─────────────────────────────────────────┤
 *   │  Sidebar  │  Map (full height)                      │
 *   │           ├─────────────────────────────────────────┤
 *   │           │  Chart panel (collapsible)              │
 *   └───────────┴─────────────────────────────────────────┘
 */

import React, { useEffect } from 'react'
import { Toaster } from 'react-hot-toast'

import TopBar       from './components/UI/TopBar.jsx'
import Sidebar      from './components/Controls/Sidebar.jsx'
import MapContainer from './components/Map/MapContainer.jsx'
import ChartPanel   from './components/Charts/ChartPanel.jsx'
import StatsPanel   from './components/UI/StatsPanel.jsx'
import Legend       from './components/UI/Legend.jsx'

import { useStore }      from './store/useStore.js'
import { fetchIndexMeta } from './services/api.js'

import styles from './App.module.css'

export default function App() {
  const { setIndexMeta, sidebarOpen, chartOpen, statsOpen } = useStore()

  // Load index metadata on mount
  useEffect(() => {
    fetchIndexMeta()
      .then(setIndexMeta)
      .catch(() => {}) // Non-fatal — frontend has its own copy
  }, [setIndexMeta])

  return (
    <div className={styles.shell}>
      <Toaster
        position="top-right"
        toastOptions={{
          style: {
            background: 'var(--bg-elevated)',
            color: 'var(--text-primary)',
            border: '1px solid var(--border)',
            fontFamily: 'var(--font-body)',
            fontSize: '13px',
          },
        }}
      />

      <TopBar />

      <div className={styles.body}>
        {sidebarOpen && (
          <aside className={styles.sidebar}>
            <Sidebar />
          </aside>
        )}

        <main className={styles.main}>
          <div className={styles.mapArea}>
            <MapContainer />
            <Legend />
            {statsOpen && <StatsPanel />}
          </div>

          {chartOpen && (
            <div className={styles.chartArea}>
              <ChartPanel />
            </div>
          )}
        </main>
      </div>
    </div>
  )
}
