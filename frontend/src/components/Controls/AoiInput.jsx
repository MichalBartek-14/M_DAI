/**
 * AoiInput — shows drawn AOI info and allows manual coordinate entry.
 */

import React, { useState } from 'react'
import { useStore }    from '../../store/useStore.js'
import { parseBboxString, formatBbox, bboxAreaKm2 } from '../../utils/mapUtils.js'
import styles from './AoiInput.module.css'

export default function AoiInput() {
  const { aoi, setAoi, clearAoi } = useStore()
  const [manualInput, setManualInput] = useState('')
  const [error, setError] = useState('')

  function handleManualApply() {
    setError('')
    const bbox = parseBboxString(manualInput)
    if (!bbox) {
      setError('Format: minLon,minLat,maxLon,maxLat')
      return
    }
    setAoi({ type: 'bbox', data: bbox })
    setManualInput('')
  }

  function handleKeyDown(e) {
    if (e.key === 'Enter') handleManualApply()
  }

  const bbox = aoi?.type === 'bbox' ? aoi.data : null
  const area = bbox ? bboxAreaKm2(bbox) : null

  return (
    <div className={styles.wrap}>
      {aoi ? (
        <div className={styles.aoiCard}>
          <div className={styles.aoiHeader}>
            <span className={styles.aoiType}>
              {aoi.type === 'bbox' ? '⬜ Bounding Box' : '⬡ Polygon'}
            </span>
            <button className={styles.clearBtn} onClick={clearAoi} title="Clear AOI">
              ✕
            </button>
          </div>
          {bbox && (
            <>
              <div className={styles.coords}>{formatBbox(bbox)}</div>
              <div className={styles.area}>≈ {area?.toLocaleString()} km²</div>
            </>
          )}
          {aoi.type === 'geojson' && (
            <div className={styles.coords}>Custom polygon</div>
          )}
        </div>
      ) : (
        <div className={styles.hint}>
          <DrawIcon />
          <span>Draw a polygon or rectangle on the map</span>
        </div>
      )}

      <div className={styles.divider}>
        <span>or enter coordinates</span>
      </div>

      <div className={styles.inputRow}>
        <input
          className={`${styles.input} ${error ? styles.inputError : ''}`}
          type="text"
          placeholder="minLon,minLat,maxLon,maxLat"
          value={manualInput}
          onChange={(e) => setManualInput(e.target.value)}
          onKeyDown={handleKeyDown}
        />
        <button className={styles.applyBtn} onClick={handleManualApply}>
          Set
        </button>
      </div>
      {error && <p className={styles.error}>{error}</p>}

      <div className={styles.examples}>
        <span className={styles.exLabel}>Examples:</span>
        {EXAMPLE_BBOXES.map((ex) => (
          <button
            key={ex.label}
            className={styles.exBtn}
            onClick={() => {
              setManualInput(ex.value)
              const bbox = parseBboxString(ex.value)
              if (bbox) setAoi({ type: 'bbox', data: bbox })
            }}
          >
            {ex.label}
          </button>
        ))}
      </div>
    </div>
  )
}

const EXAMPLE_BBOXES = [
  { label: 'Klenovec', value: '19.8,48.5,20.0,48.7' },
  { label: 'Bratislava', value: '17.0,48.2,17.2,48.0' },
  { label: 'Jasna', value: '48.8,19.5,49.0,19.7' },
]

const DrawIcon = () => (
  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5">
    <path d="M12 2L2 7l10 5 10-5-10-5zM2 17l10 5 10-5M2 12l10 5 10-5"/>
  </svg>
)
