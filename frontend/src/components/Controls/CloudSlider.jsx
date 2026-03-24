/**
 * CloudSlider — max cloud cover filter (0–100 %).
 */

import React from 'react'
import { useStore } from '../../store/useStore.js'
import styles from './CloudSlider.module.css'

export function CloudSlider() {
  const { cloudCoverMax, setCloudCoverMax } = useStore()

  const color =
    cloudCoverMax <= 20 ? '#5deb9b' :
    cloudCoverMax <= 50 ? '#ffb938' : '#ff5c5c'

  return (
    <div className={styles.wrap}>
      <div className={styles.header}>
        <span className={styles.icon}>☁</span>
        <span className={styles.value} style={{ color }}>≤ {cloudCoverMax}%</span>
      </div>
      <input
        type="range"
        min={0}
        max={100}
        step={5}
        value={cloudCoverMax}
        onChange={(e) => setCloudCoverMax(Number(e.target.value))}
        className={styles.slider}
        style={{ '--fill': `${cloudCoverMax}%`, '--color': color }}
      />
      <div className={styles.ticks}>
        <span>0%</span><span>50%</span><span>100%</span>
      </div>
    </div>
  )
}

export default CloudSlider
