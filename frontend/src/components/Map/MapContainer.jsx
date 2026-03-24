/**
 * MapContainer — Leaflet map with:
 *   - Draw controls (polygon, rectangle)
 *   - Index raster tile overlay
 *   - Opacity slider
 *   - Compare mode (side-by-side slider)
 */

import React, { useEffect, useRef, useCallback } from 'react'
import L from 'leaflet'
import 'leaflet/dist/leaflet.css'
import 'leaflet-draw/dist/leaflet.draw.css'

import { useStore }    from '../../store/useStore.js'
import { leafletBoundsToBbox, bboxToLeafletBounds, bboxCenter } from '../../utils/mapUtils.js'
import OpacitySlider   from './OpacitySlider.jsx'
import styles from './MapContainer.module.css'

// Fix Leaflet default icon paths broken by Vite bundling
delete L.Icon.Default.prototype._getIconUrl
L.Icon.Default.mergeOptions({
  iconRetinaUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon-2x.png',
  iconUrl:       'https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon.png',
  shadowUrl:     'https://unpkg.com/leaflet@1.9.4/dist/images/marker-shadow.png',
})

const BASEMAP_URL = 'https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png'
const BASEMAP_ATTR = '&copy; <a href="https://carto.com/">CARTO</a> &copy; <a href="https://www.openstreetmap.org/copyright">OSM</a>'

export default function MapContainer() {
  const mapRef        = useRef(null)
  const tileLayerRef  = useRef(null)
  const drawLayerRef  = useRef(null)
  const containerRef  = useRef(null)

  const {
    tileUrl, opacity, aoi, setAoi,
    mapCenter, mapZoom, setMapView,
  } = useStore()

  // ── Initialise Leaflet map ────────────────────────────────────────────────
  useEffect(() => {
    if (mapRef.current) return   // Already initialised

    const map = L.map(containerRef.current, {
      center: mapCenter,
      zoom:   mapZoom,
      zoomControl: false,
      preferCanvas: true,
    })

    L.tileLayer(BASEMAP_URL, {
      attribution: BASEMAP_ATTR,
      subdomains:  'abcd',
      maxZoom:     19,
    }).addTo(map)

    L.control.zoom({ position: 'bottomright' }).addTo(map)

    // ── Draw layer ──────────────────────────────────────────────────────
    const drawnItems = new L.FeatureGroup()
    map.addLayer(drawnItems)
    drawLayerRef.current = drawnItems

    // ── Load leaflet-draw dynamically ───────────────────────────────────
    import('leaflet-draw').then(() => {
      const drawControl = new L.Control.Draw({
        position: 'topleft',
        draw: {
          polygon:   { shapeOptions: { color: '#5deb9b', weight: 2, fillOpacity: 0.1 } },
          rectangle: { shapeOptions: { color: '#5deb9b', weight: 2, fillOpacity: 0.1 } },
          circle:    false,
          circlemarker: false,
          marker:    false,
          polyline:  false,
        },
        edit: { featureGroup: drawnItems },
      })
      map.addControl(drawControl)

      map.on(L.Draw.Event.CREATED, (e) => {
        drawnItems.clearLayers()
        drawnItems.addLayer(e.layer)

        if (e.layerType === 'rectangle') {
          const bounds = e.layer.getBounds()
          setAoi({ type: 'bbox', data: leafletBoundsToBbox(bounds) })
        } else if (e.layerType === 'polygon') {
          const geo = e.layer.toGeoJSON()
          setAoi({ type: 'geojson', data: geo.geometry })
        }
      })

      map.on(L.Draw.Event.DELETED, () => {
        useStore.getState().clearAoi()
      })
    })

    map.on('moveend', () => {
      setMapView(
        [map.getCenter().lat, map.getCenter().lng],
        map.getZoom(),
      )
    })

    mapRef.current = map
  }, []) // eslint-disable-line react-hooks/exhaustive-deps

  // ── Update tile layer when tileUrl changes ────────────────────────────────
  useEffect(() => {
    const map = mapRef.current
    if (!map) return

    if (tileLayerRef.current) {
      map.removeLayer(tileLayerRef.current)
      tileLayerRef.current = null
    }

    if (tileUrl) {
      // Replace {z}/{x}/{y} template tokens with Leaflet tokens
      const leafletUrl = tileUrl
        .replace('{z}', '{z}')
        .replace('{x}', '{x}')
        .replace('{y}', '{y}')

      const layer = L.tileLayer(leafletUrl, {
        opacity,
        maxZoom: 18,
        tileSize: 256,
      })
      layer.addTo(map)
      tileLayerRef.current = layer
    }
  }, [tileUrl]) // eslint-disable-line react-hooks/exhaustive-deps

  // ── Update opacity ────────────────────────────────────────────────────────
  useEffect(() => {
    if (tileLayerRef.current) {
      tileLayerRef.current.setOpacity(opacity)
    }
  }, [opacity])

  // ── Fly to AOI when set via coordinate input ──────────────────────────────
  useEffect(() => {
    const map = mapRef.current
    if (!map || !aoi) return

    if (aoi.type === 'bbox') {
      const bounds = bboxToLeafletBounds(aoi.data)
      map.fitBounds(bounds, { padding: [40, 40] })

      // Reflect on map as a rectangle layer
      drawLayerRef.current?.clearLayers()
      const rect = L.rectangle(bounds, {
        color: '#5deb9b', weight: 2, fillOpacity: 0.05,
      })
      drawLayerRef.current?.addLayer(rect)
    }
  }, [aoi])

  return (
    <div className={styles.outer}>
      <div ref={containerRef} className={styles.map} />
      <OpacitySlider />
    </div>
  )
}
