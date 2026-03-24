/**
 * DateRangePicker — start/end date selection with quick-range presets.
 */

import React from 'react'
import DatePicker from 'react-datepicker'
import { parseISO, format, subMonths, subYears, startOfYear } from 'date-fns'
import 'react-datepicker/dist/react-datepicker.css'
import { useStore } from '../../store/useStore.js'
import styles from './DateRangePicker.module.css'

const QUICK_RANGES = [
  { label: '1 M',  months: 1 },
  { label: '3 M',  months: 3 },
  { label: '6 M',  months: 6 },
  { label: '1 Y',  months: 12 },
  { label: 'YTD',  ytd: true },
]

const fmt = (d) => format(d, 'yyyy-MM-dd')

export default function DateRangePicker() {
  const { startDate, endDate, setStartDate, setEndDate } = useStore()

  const start = parseISO(startDate)
  const end   = parseISO(endDate)

  function applyQuick(range) {
    const today = new Date()
    if (range.ytd) {
      setStartDate(fmt(startOfYear(today)))
      setEndDate(fmt(today))
    } else {
      setStartDate(fmt(subMonths(today, range.months)))
      setEndDate(fmt(today))
    }
  }

  return (
    <div className={styles.wrap}>
      <div className={styles.quickRow}>
        {QUICK_RANGES.map((r) => (
          <button key={r.label} className={styles.quickBtn} onClick={() => applyQuick(r)}>
            {r.label}
          </button>
        ))}
      </div>

      <div className={styles.row}>
        <div className={styles.field}>
          <label className={styles.label}>From</label>
          <DatePicker
            selected={start}
            onChange={(d) => d && setStartDate(fmt(d))}
            selectsStart
            startDate={start}
            endDate={end}
            maxDate={end}
            dateFormat="dd MMM yyyy"
            customInput={<DateInput />}
          />
        </div>
        <span className={styles.arrow}>→</span>
        <div className={styles.field}>
          <label className={styles.label}>To</label>
          <DatePicker
            selected={end}
            onChange={(d) => d && setEndDate(fmt(d))}
            selectsEnd
            startDate={start}
            endDate={end}
            minDate={start}
            maxDate={new Date()}
            dateFormat="dd MMM yyyy"
            customInput={<DateInput />}
          />
        </div>
      </div>
    </div>
  )
}

// Styled input forwarded from DatePicker
const DateInput = React.forwardRef(({ value, onClick }, ref) => (
  <button className={styles.dateBtn} onClick={onClick} ref={ref}>
    <CalendarIcon />
    {value}
  </button>
))
DateInput.displayName = 'DateInput'

const CalendarIcon = () => (
  <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
    <rect x="3" y="4" width="18" height="18" rx="2"/>
    <path d="M16 2v4M8 2v4M3 10h18"/>
  </svg>
)
