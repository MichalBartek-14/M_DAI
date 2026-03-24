/**
 * ExportButtons — download index rasters as PNG or GeoTIFF.
 */

import React, { useState } from 'react'
import toast from 'react-hot-toast'
import { useStore }           from '../../store/useStore.js'
import { exportPng, exportGeotiff } from '../../services/api.js'
import { downloadBlob }       from '../../utils/mapUtils.js'
import styles from './ExportButtons.module.css'

export default function ExportButtons() {
  const { aoi, selectedIndex, startDate, endDate, tileUrl } = useStore()
  const [exporting, setExporting] = useState(null)

  const disabled = !aoi || !tileUrl

  async function handleExport(format) {
    if (disabled) { toast.error('Run analysis first'); return }
    setExporting(format)
    try {
      const blob = format === 'png'
        ? await exportPng({ aoi, index: selectedIndex, startDate, endDate })
        : await exportGeotiff({ aoi, index: selectedIndex, startDate, endDate })

      downloadBlob(blob, `${selectedIndex}_${startDate}_${endDate}.${format === 'geotiff' ? 'tif' : 'png'}`)
      toast.success(`Downloaded ${format.toUpperCase()}`)
    } catch (e) {
      toast.error(e.message)
    } finally {
      setExporting(null)
    }
  }

  return (
    <div className={styles.row}>
      <button
        className={styles.btn}
        onClick={() => handleExport('png')}
        disabled={disabled || exporting === 'png'}
        title="Download colourised PNG"
      >
        {exporting === 'png' ? '…' : '⬇'} PNG
      </button>
      <button
        className={styles.btn}
        onClick={() => handleExport('geotiff')}
        disabled={disabled || exporting === 'geotiff'}
        title="Download float32 GeoTIFF"
      >
        {exporting === 'geotiff' ? '…' : '⬇'} GeoTIFF
      </button>
    </div>
  )
}
