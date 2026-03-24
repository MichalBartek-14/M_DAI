/**
 * PresetButtons — quick-configure for common use cases.
 */

import React from 'react'
import { useStore }        from '../../store/useStore.js'
import { PRESET_CONFIGS }  from '../../utils/indexMeta.js'
import styles from './PresetButtons.module.css'

export default function PresetButtons() {
  const {
    activePreset, setActivePreset,
    setSelectedIndex, setCloudCoverMax, setTimeseriesIndices,
  } = useStore()

  function applyPreset(key) {
    const p = PRESET_CONFIGS[key]
    setActivePreset(key === activePreset ? null : key)
    if (key !== activePreset) {
      setSelectedIndex(p.indices[0])
      setCloudCoverMax(p.cloudMax)
      setTimeseriesIndices(p.indices)
    }
  }

  return (
    <div className={styles.grid}>
      {Object.entries(PRESET_CONFIGS).map(([key, preset]) => (
        <button
          key={key}
          className={`${styles.btn} ${activePreset === key ? styles.active : ''}`}
          onClick={() => applyPreset(key)}
          title={preset.description}
        >
          <span className={styles.emoji}>{preset.label.split(' ')[0]}</span>
          <span className={styles.name}>{preset.label.split(' ').slice(1).join(' ')}</span>
        </button>
      ))}
    </div>
  )
}
