/**
 * Map utility helpers — coordinate transforms, AOI formatting, etc.
 */

/**
 * Convert a Leaflet LatLngBounds to a BoundingBox object.
 */
export function leafletBoundsToBbox(bounds) {
  return {
    min_lon: bounds.getWest(),
    min_lat: bounds.getSouth(),
    max_lon: bounds.getEast(),
    max_lat: bounds.getNorth(),
  }
}

/**
 * Convert a Leaflet GeoJSON feature to an AOI geometry object.
 */
export function leafletFeatureToGeometry(feature) {
  return feature.geometry
}

/**
 * Format a bounding box as a human-readable string.
 */
export function formatBbox(bbox) {
  if (!bbox) return 'None'
  const fmt = (n) => n.toFixed(4)
  return `[${fmt(bbox.min_lon)}, ${fmt(bbox.min_lat)}, ${fmt(bbox.max_lon)}, ${fmt(bbox.max_lat)}]`
}

/**
 * Compute approximate area of a bbox in km².
 */
export function bboxAreaKm2(bbox) {
  const R = 6371
  const dLat = (bbox.max_lat - bbox.min_lat) * (Math.PI / 180)
  const dLon = (bbox.max_lon - bbox.min_lon) * (Math.PI / 180)
  const midLat = ((bbox.min_lat + bbox.max_lat) / 2) * (Math.PI / 180)
  return Math.round(R * R * dLat * Math.cos(midLat) * dLon)
}

/**
 * Parse a comma-separated bbox string "minLon,minLat,maxLon,maxLat".
 */
export function parseBboxString(str) {
  const parts = str.split(',').map((p) => parseFloat(p.trim()))
  if (parts.length !== 4 || parts.some(isNaN)) return null
  return {
    min_lon: parts[0],
    min_lat: parts[1],
    max_lon: parts[2],
    max_lat: parts[3],
  }
}

/**
 * Build a Leaflet bounds array from a bbox object.
 */
export function bboxToLeafletBounds(bbox) {
  return [
    [bbox.min_lat, bbox.min_lon],
    [bbox.max_lat, bbox.max_lon],
  ]
}

/**
 * Center point of a bbox.
 */
export function bboxCenter(bbox) {
  return [
    (bbox.min_lat + bbox.max_lat) / 2,
    (bbox.min_lon + bbox.max_lon) / 2,
  ]
}

/**
 * Download a Blob as a file.
 */
export function downloadBlob(blob, filename) {
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = filename
  document.body.appendChild(a)
  a.click()
  document.body.removeChild(a)
  URL.revokeObjectURL(url)
}

/**
 * Format index value for display.
 */
export function formatIndexValue(value, decimals = 3) {
  if (value == null || isNaN(value)) return 'N/A'
  return Number(value).toFixed(decimals)
}
