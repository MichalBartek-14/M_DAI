/**
 * IndexSelector — pill buttons to switch between spectral indices.
 */

import React from 'react'
import { useStore }    from '../../store/useStore.js'
import { INDEX_META }  from '../../utils/indexMeta.js'
import styles from './IndexSelector.module.css'

export default function IndexSelector() {
  const { selectedIndex, setSelectedIndex } = useStore()

  return (
    <div className={styles.grid}>
      {Object.entries(INDEX_META).map(([key, meta]) => (
        <button
          key={key}
          className={`${styles.pill} ${selectedIndex === key ? styles.active : ''}`}
          style={{ '--index-color': meta.color }}
          onClick={() => setSelectedIndex(key)}
          title={meta.fullName}
        >
          <span className={styles.dot} />
          <span className={styles.label}>{meta.label}</span>
        </button>
      ))}
    </div>
  )
}
