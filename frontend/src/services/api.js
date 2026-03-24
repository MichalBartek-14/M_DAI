/**
 * API service — all backend calls centralised here.
 * Base URL is configurable via VITE_API_URL env var.
 */

import axios from 'axios'

const BASE = import.meta.env.VITE_API_URL || ''

const api = axios.create({
  baseURL: BASE,
  timeout: 60_000,
  headers: { 'Content-Type': 'application/json' },
})

// ── Request / response interceptors ────────────────────────────────────────

api.interceptors.response.use(
  (res) => res,
  (err) => {
    const msg = err.response?.data?.detail || err.message || 'Unknown error'
    return Promise.reject(new Error(msg))
  }
)

// ── AOI helpers ─────────────────────────────────────────────────────────────

function buildAoi(aoi) {
  if (!aoi) return null
  if (aoi.type === 'bbox') {
    return { bbox: aoi.data }
  }
  return { geometry: aoi.data }
}

// ── Index metadata ──────────────────────────────────────────────────────────

export async function fetchIndexMeta() {
  const { data } = await api.get('/api/indices/meta')
  return data
}

// ── Compute index + get tile URL ────────────────────────────────────────────

export async function computeIndex({ aoi, startDate, endDate, index, cloudCoverMax = 30, resolution = 10 }) {
  const { data } = await api.post('/api/indices/compute', {
    aoi: buildAoi(aoi),
    start_date: startDate,
    end_date: endDate,
    index,
    cloud_cover_max: cloudCoverMax,
    resolution,
  })
  return data
}

// ── Time-series ─────────────────────────────────────────────────────────────

export async function fetchTimeseries({ aoi, startDate, endDate, indices = ['NDVI'], cloudCoverMax = 30 }) {
  const { data } = await api.post('/api/timeseries/', {
    aoi: buildAoi(aoi),
    start_date: startDate,
    end_date: endDate,
    indices,
    cloud_cover_max: cloudCoverMax,
    temporal_resolution: '16D',
  })
  return data
}

// ── Area statistics ──────────────────────────────────────────────────────────

export async function fetchAreaStats({ aoi, index, startDate, endDate }) {
  const { data } = await api.post('/api/stats/area', buildAoi(aoi), {
    params: { index, start_date: startDate, end_date: endDate },
  })
  return data
}

// ── Export ───────────────────────────────────────────────────────────────────

export async function exportPng({ aoi, index, startDate, endDate, width = 1024, height = 1024 }) {
  const resp = await api.post('/api/export/png', buildAoi(aoi), {
    params: { index, start_date: startDate, end_date: endDate, width, height },
    responseType: 'blob',
  })
  return resp.data
}

export async function exportGeotiff({ aoi, index, startDate, endDate }) {
  const resp = await api.post('/api/export/geotiff', buildAoi(aoi), {
    params: { index, start_date: startDate, end_date: endDate },
    responseType: 'blob',
  })
  return resp.data
}

// ── Health check ─────────────────────────────────────────────────────────────

export async function healthCheck() {
  const { data } = await api.get('/api/health')
  return data
}

export default api
