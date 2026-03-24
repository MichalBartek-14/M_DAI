/**
 * OpacitySlider — floating control to adjust raster overlay transparency.
 */

import React from 'react'
import { useStore } from '../../store/useStore.js'
import styles from './OpacitySlider.module.css'

export default function OpacitySlider() {
  const { opacity, setOpacity, tileUrl } = useStore()
  if (!tileUrl) return null

  return (
    <div className={styles.wrap}>
      <span className={styles.label}>Opacity</span>
      <input
        type="range"
        min={0}
        max={1}
        step={0.05}
        value={opacity}
        onChange={(e) => setOpacity(Number(e.target.value))}
        className={styles.slider}
        style={{ '--fill': `${opacity * 100}%` }}
        aria-label="Layer opacity"
      />
      <span className={styles.value}>{Math.round(opacity * 100)}%</span>
    </div>
  )
}
