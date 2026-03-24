/**
 * Legend — floating colormap legend overlay on the map.
 */

import React from 'react'
import { useStore }   from '../../store/useStore.js'
import { INDEX_META } from '../../utils/indexMeta.js'
import styles from './Legend.module.css'

// Colormap CSS gradients keyed to index
const GRADIENTS = {
  NDVI:  'linear-gradient(to right, #d73027, #fdae61, #fee090, #a6d96a, #1a9850)',
  NDWI:  'linear-gradient(to right, #f7fbff, #c6dbef, #6baed6, #2171b5, #084594)',
  EVI:   'linear-gradient(to right, #440154, #3b5288, #21918c, #5ec962, #fde725)',
  SAVI:  'linear-gradient(to right, #ffffe5, #c2e699, #31a354, #006837)',
  NDMI:  'linear-gradient(to right, #543005, #bf812d, #f6e8c3, #80cdc1, #01858f)',
}

export default function Legend() {
  const { tileUrl, selectedIndex } = useStore()
  if (!tileUrl) return null

  const meta = INDEX_META[selectedIndex]
  if (!meta) return null

  const [lo, hi] = meta.range
  const mid = ((lo + hi) / 2).toFixed(1)

  return (
    <div className={styles.legend}>
      <div className={styles.title}>
        <span className={styles.dot} style={{ background: meta.color }} />
        {meta.label}
      </div>
      <div
        className={styles.bar}
        style={{ background: GRADIENTS[selectedIndex] }}
      />
      <div className={styles.ticks}>
        <span>{lo.toFixed(1)}</span>
        <span>{mid}</span>
        <span>{hi.toFixed(1)}</span>
      </div>
      <div className={styles.desc}>{meta.description}</div>
    </div>
  )
}
