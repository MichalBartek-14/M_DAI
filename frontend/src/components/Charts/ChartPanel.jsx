/**
 * ChartPanel — time-series line chart for selected vegetation indices.
 * Uses Recharts with a custom dark theme.
 */

import React, { useState } from 'react'
import {
  ResponsiveContainer, LineChart, Line,
  XAxis, YAxis, CartesianGrid, Tooltip, Legend as RechartLegend,
  ReferenceLine, Brush,
} from 'recharts'
import { format, parseISO } from 'date-fns'
import { useStore }    from '../../store/useStore.js'
import { INDEX_META, ALL_INDICES } from '../../utils/indexMeta.js'
import styles from './ChartPanel.module.css'

const CustomTooltip = ({ active, payload, label }) => {
  if (!active || !payload?.length) return null
  return (
    <div className={styles.tooltip}>
      <div className={styles.tooltipDate}>{label}</div>
      {payload.map((p) => (
        <div key={p.dataKey} className={styles.tooltipRow} style={{ color: p.color }}>
          <span>{p.dataKey}</span>
          <span className={styles.tooltipVal}>
            {p.value != null ? p.value.toFixed(3) : 'N/A'}
          </span>
        </div>
      ))}
    </div>
  )
}

export default function ChartPanel() {
  const {
    timeseries, selectedIndex, timeseriesIndices, setTimeseriesIndices,
    setChartOpen,
  } = useStore()

  const [hoveredIndex, setHoveredIndex] = useState(null)

  // Merge all index timeseries into chart-friendly row format
  function buildChartData() {
    if (!timeseries) return []
    const allDates = new Set()
    Object.values(timeseries).forEach((ts) =>
      ts.data.forEach((p) => allDates.add(p.date))
    )
    return Array.from(allDates).sort().map((date) => {
      const row = { date: format(parseISO(date), 'dd MMM yy') }
      Object.entries(timeseries).forEach(([name, ts]) => {
        const pt = ts.data.find((p) => p.date === date)
        row[name] = pt?.value ?? null
      })
      return row
    })
  }

  const chartData    = buildChartData()
  const activeKeys   = timeseries ? Object.keys(timeseries) : []
  const hasData      = chartData.length > 0

  function toggleIndex(name) {
    setTimeseriesIndices(
      timeseriesIndices.includes(name)
        ? timeseriesIndices.filter((i) => i !== name)
        : [...timeseriesIndices, name]
    )
  }

  return (
    <div className={styles.panel}>
      <div className={styles.header}>
        <span className={styles.title}>Time-series</span>

        <div className={styles.indexToggles}>
          {ALL_INDICES.map((name) => (
            <button
              key={name}
              className={`${styles.toggle} ${timeseriesIndices.includes(name) ? styles.toggleOn : ''}`}
              style={{ '--idx-color': INDEX_META[name].color }}
              onClick={() => toggleIndex(name)}
              onMouseEnter={() => setHoveredIndex(name)}
              onMouseLeave={() => setHoveredIndex(null)}
            >
              {name}
            </button>
          ))}
        </div>

        <button className={styles.closeBtn} onClick={() => setChartOpen(false)}>
          Collapse ↓
        </button>
      </div>

      <div className={styles.chartWrap}>
        {!hasData ? (
          <div className={styles.empty}>
            <WaveIcon />
            <span>Run an analysis to see the time-series</span>
          </div>
        ) : (
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={chartData} margin={{ top: 8, right: 20, bottom: 4, left: -10 }}>
              <CartesianGrid
                strokeDasharray="3 3"
                stroke="var(--border)"
                vertical={false}
              />
              <XAxis
                dataKey="date"
                tick={{ fill: 'var(--text-muted)', fontSize: 10, fontFamily: 'var(--font-display)' }}
                tickLine={false}
                axisLine={{ stroke: 'var(--border)' }}
              />
              <YAxis
                tick={{ fill: 'var(--text-muted)', fontSize: 10, fontFamily: 'var(--font-display)' }}
                tickLine={false}
                axisLine={false}
                domain={[-1, 1]}
              />
              <Tooltip content={<CustomTooltip />} />
              <ReferenceLine y={0} stroke="var(--border-bright)" strokeDasharray="4 4" />

              {activeKeys.map((name) => (
                <Line
                  key={name}
                  type="monotone"
                  dataKey={name}
                  stroke={INDEX_META[name]?.color ?? '#fff'}
                  strokeWidth={hoveredIndex === name ? 3 : (hoveredIndex ? 1 : 2)}
                  dot={false}
                  activeDot={{ r: 4, strokeWidth: 0 }}
                  connectNulls
                  opacity={hoveredIndex && hoveredIndex !== name ? 0.3 : 1}
                />
              ))}

              {chartData.length > 12 && (
                <Brush
                  dataKey="date"
                  height={16}
                  stroke="var(--border-bright)"
                  fill="var(--bg-panel)"
                  travellerWidth={6}
                />
              )}
            </LineChart>
          </ResponsiveContainer>
        )}
      </div>
    </div>
  )
}

const WaveIcon = () => (
  <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5">
    <polyline points="22,12 18,12 15,21 9,3 6,12 2,12"/>
  </svg>
)
