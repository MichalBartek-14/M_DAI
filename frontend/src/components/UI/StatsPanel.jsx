/**
 * StatsPanel — displays area statistics for the current AOI.
 */

import React from 'react'
import { useStore }         from '../../store/useStore.js'
import { INDEX_META }       from '../../utils/indexMeta.js'
import { formatIndexValue } from '../../utils/mapUtils.js'
import styles from './StatsPanel.module.css'

export default function StatsPanel() {
  const { areaStats, selectedIndex, scenes, setStatsOpen } = useStore()
  const meta = INDEX_META[selectedIndex]

  return (
    <div className={styles.panel}>
      <div className={styles.header}>
        <span className={styles.title}>
          <span className={styles.dot} style={{ background: meta?.color }} />
          {selectedIndex} Statistics
        </span>
        <button className={styles.close} onClick={() => setStatsOpen(false)}>✕</button>
      </div>

      {areaStats ? (
        <div className={styles.grid}>
          <Stat label="Mean"   value={formatIndexValue(areaStats.mean)} />
          <Stat label="Median" value={formatIndexValue(areaStats.median)} />
          <Stat label="Std"    value={formatIndexValue(areaStats.std)} />
          <Stat label="Min"    value={formatIndexValue(areaStats.min)} />
          <Stat label="Max"    value={formatIndexValue(areaStats.max)} />
          <Stat label="Valid"  value={`${formatIndexValue(areaStats.valid_pct, 1)}%`} />
        </div>
      ) : (
        <p className={styles.empty}>Run analysis to compute statistics.</p>
      )}

      {scenes?.length > 0 && (
        <div className={styles.scenes}>
          <div className={styles.scenesTitle}>Scenes ({scenes.length})</div>
          <div className={styles.sceneList}>
            {scenes.slice(0, 6).map((s) => (
              <div key={s.scene_id} className={styles.scene}>
                <span className={styles.sceneDate}>{s.date}</span>
                <span className={styles.sceneCloud}>☁ {s.cloud_cover?.toFixed(0)}%</span>
              </div>
            ))}
            {scenes.length > 6 && (
              <div className={styles.moreScenes}>+{scenes.length - 6} more</div>
            )}
          </div>
        </div>
      )}
    </div>
  )
}

function Stat({ label, value }) {
  return (
    <div className={styles.stat}>
      <span className={styles.statLabel}>{label}</span>
      <span className={styles.statValue}>{value}</span>
    </div>
  )
}
