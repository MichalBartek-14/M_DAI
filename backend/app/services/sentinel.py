"""
Sentinel Hub Process API wrapper.

Handles:
  - Scene search (STAC)
  - Band download (Process API evalscript)
  - Cloud masking (SCL layer)
  - Index computation + PNG tile generation
"""

import io
import logging
from datetime import date
from typing import Any, Dict, List, Optional, Tuple

import httpx
import numpy as np
from PIL import Image

from app.core.auth import get_sentinelhub_token, build_auth_headers
from app.core.config import settings
from app.core.schemas import AOI, IndexType
from app.services.indices import compute_index, INDEX_META, array_stats
from app.services.colormap import index_to_png

logger = logging.getLogger(__name__)

PROCESS_API_URL = "https://sh.dataspace.copernicus.eu/api/v1/process"
STAC_SEARCH_URL = "https://catalogue.dataspace.copernicus.eu/stac/search"

# ── Evalscripts ───────────────────────────────────────────────────────────────
# These JavaScript snippets run server-side on Sentinel Hub.

def build_evalscript(index_name: str) -> str:
    """
    Return a Sentinel Hub evalscript that outputs the required bands
    as raw float values (no visual rendering — we do that ourselves).
    """
    index = index_name.upper()
    band_map = {
        "NDVI":  (["B04", "B08"],         "return [B04, B08];"),
        "NDWI":  (["B03", "B08"],         "return [B03, B08];"),
        "EVI":   (["B02", "B04", "B08"],  "return [B02, B04, B08];"),
        "SAVI":  (["B04", "B08"],         "return [B04, B08];"),
        "NDMI":  (["B8A", "B11"],         "return [B8A, B11];"),
    }
    if index not in band_map:
        raise ValueError(f"Unknown index: {index}")

    bands, return_stmt = band_map[index]
    bands_input = ", ".join(f'"{b}"' for b in bands)
    n_bands = len(bands)

    return f"""
//VERSION=3
function setup() {{
  return {{
    input: [{{
      bands: [{bands_input}, "SCL"],
      units: "REFLECTANCE"
    }}],
    output: {{
      bands: {n_bands},
      sampleType: "FLOAT32"
    }}
  }};
}}
function evaluatePixel(sample) {{
  // Cloud masking: SCL classes 3(shadow),8(cloud medium),9(cloud high),10(thin cirrus)
  if ([3,8,9,10].includes(sample.SCL)) {{
    return new Array({n_bands}).fill(NaN);
  }}
  var {{B02, B03, B04, B08, B8A, B11}} = sample;
  {return_stmt}
}}
"""


# ── STAC scene search ──────────────────────────────────────────────────────────

async def search_scenes(
    aoi: AOI,
    start_date: date,
    end_date: date,
    cloud_cover_max: int = 30,
    max_items: int = 20,
) -> List[Dict[str, Any]]:
    """Search the Copernicus STAC catalogue for Sentinel-2 L2A scenes."""

    bbox = _aoi_to_bbox(aoi)

    params = {
        "collections": ["SENTINEL-2"],
        "bbox": bbox,
        "datetime": f"{start_date.isoformat()}T00:00:00Z/{end_date.isoformat()}T23:59:59Z",
        "limit": max_items,
        "filter": f"eo:cloud_cover <= {cloud_cover_max}",
        "filter-lang": "cql2-text",
        "sortby": "+datetime",
    }

    async with httpx.AsyncClient(timeout=20) as client:
        resp = await client.post(STAC_SEARCH_URL, json=params)
        if resp.status_code != 200:
            logger.warning(f"STAC search returned {resp.status_code}: {resp.text[:200]}")
            return _demo_scenes(start_date, end_date)
        data = resp.json()

    features = data.get("features", [])
    scenes = []
    for f in features:
        props = f.get("properties", {})
        scenes.append({
            "scene_id":    f.get("id", ""),
            "date":        props.get("datetime", "")[:10],
            "cloud_cover": props.get("eo:cloud_cover", 0),
            "tile_id":     props.get("s2:mgrs_tile", ""),
            "preview_url": (f.get("links") or [{}])[0].get("href"),
        })
    return scenes


def _demo_scenes(start_date: date, end_date: date) -> List[Dict]:
    """Return mock scene list when API is unavailable (demo mode)."""
    from datetime import timedelta
    scenes = []
    current = start_date
    while current <= end_date:
        scenes.append({
            "scene_id":    f"S2A_MSIL2A_{current.strftime('%Y%m%d')}T100000_DEMO",
            "date":        current.isoformat(),
            "cloud_cover": 5.0,
            "tile_id":     "32UMD",
            "preview_url": None,
        })
        current += timedelta(days=16)
    return scenes


# ── Band data fetch ───────────────────────────────────────────────────────────

async def fetch_band_data(
    aoi: AOI,
    evalscript: str,
    start_date: date,
    end_date: date,
    resolution: int = 10,
    width: int = 512,
    height: int = 512,
) -> Optional[np.ndarray]:
    """
    Call the Sentinel Hub Process API and return a float32 NumPy array
    of shape (n_bands, height, width).

    Returns None in demo mode (no valid credentials).
    """
    token = await get_sentinelhub_token(use_cdse=True)
    if not token:
        return None

    bbox = _aoi_to_bbox(aoi)
    payload = {
        "input": {
            "bounds": {
                "bbox": bbox,
                "properties": {"crs": "http://www.opengis.net/def/crs/EPSG/0/4326"},
            },
            "data": [{
                "type": "S2L2A",
                "dataFilter": {
                    "timeRange": {
                        "from": f"{start_date.isoformat()}T00:00:00Z",
                        "to": f"{end_date.isoformat()}T23:59:59Z",
                    },
                    "mosaickingOrder": "leastCC",
                    "maxCloudCoverage": 30,
                },
                "processing": {
                    "harmonizeValues": True,
                },
            }],
        },
        "evalscript": evalscript,
        "output": {
            "width": width,
            "height": height,
            "responses": [{
                "identifier": "default",
                "format": {"type": "image/tiff"},
            }],
        },
    }

    headers = {
        **build_auth_headers(token),
        "Content-Type": "application/json",
        "Accept": "image/tiff",
    }
    async with httpx.AsyncClient(timeout=60) as client:
        resp = await client.post(PROCESS_API_URL, json=payload, headers=headers)
        logger.info(f"Process API response status: {resp.status_code}")
        logger.info(f"Process API response body: {resp.text[:500]}")
        resp.raise_for_status()
        tiff_bytes = resp.content

    return _tiff_to_numpy(tiff_bytes)


# ── Demo / fallback data ──────────────────────────────────────────────────────

def generate_demo_index(index_name: str, width: int = 512, height: int = 512) -> np.ndarray:
    """
    Generate realistic-looking synthetic index data for UI demonstration
    when no API credentials are configured.
    """
    rng = np.random.default_rng(42)
    meta = INDEX_META[index_name.upper()]
    lo, hi = meta["range"]
    centre = (lo + hi) * 0.45

    # Smooth spatial noise (simulate vegetation patches)
    noise = np.zeros((height, width), dtype=np.float32)
    for scale in [8, 16, 32, 64]:
        small = rng.standard_normal((height // scale + 1, width // scale + 1)).astype(np.float32)
        zoomed = np.kron(small, np.ones((scale, scale)))[:height, :width]
        noise += zoomed / (scale ** 0.5)

    noise = (noise - noise.min()) / (noise.max() - noise.min() + 1e-6)
    arr = lo + noise * (hi - lo) * 0.8 + centre * 0.2

    # Add a realistic water body in the lower-left
    if index_name.upper() in ("NDVI", "EVI", "SAVI"):
        y, x = np.ogrid[:height, :width]
        water_mask = ((x - width * 0.15) ** 2 + (y - height * 0.75) ** 2) < (min(width, height) * 0.08) ** 2
        arr[water_mask] = lo + rng.random(water_mask.sum()).astype(np.float32) * 0.15

    return arr.clip(lo, hi).astype(np.float32)


# ── Tile rendering pipeline ───────────────────────────────────────────────────

async def render_index_tile(
    index_name: str,
    aoi: AOI,
    start_date: date,
    end_date: date,
    z: int,
    x: int,
    y: int,
    resolution: int = 10,
) -> bytes:
    """
    Fetch bands, compute index, apply colormap, return PNG tile bytes.
    Falls back to synthetic demo data if credentials are not set or API fails.
    """
    try:
        evalscript = build_evalscript(index_name)
        band_data = await fetch_band_data(
            aoi, evalscript, start_date, end_date,
            resolution=resolution, width=256, height=256,
        )
    except Exception as e:
        logger.error(f"BAND FETCH FAILED - using demo data. Error: {e}", exc_info=True)
        band_data = None

    try:
        if band_data is None:
            index_arr = generate_demo_index(index_name, 256, 256)
        else:
            bands = _unpack_bands(index_name, band_data)
            index_arr = compute_index(index_name, bands)
    except Exception as e:
        logger.warning(f"Index compute failed, using demo data: {e}")
        index_arr = generate_demo_index(index_name, 256, 256)

    try:
        meta = INDEX_META[index_name.upper()]
        return index_to_png(index_arr, meta["colormap"], meta["range"])
    except Exception as e:
        logger.error(f"PNG render failed: {e}")
        # Return a 1x1 transparent PNG as absolute fallback
        import base64
        transparent_png = base64.b64decode(
            "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg=="
        )
        return transparent_png

# ── Helpers ───────────────────────────────────────────────────────────────────

def _aoi_to_bbox(aoi: AOI) -> List[float]:
    """Return [min_lon, min_lat, max_lon, max_lat]."""
    if aoi.bbox:
        b = aoi.bbox
        return [b.min_lon, b.min_lat, b.max_lon, b.max_lat]
    # Derive bbox from GeoJSON geometry
    coords = _flatten_coords(aoi.geometry.coordinates)
    lons = [c[0] for c in coords]
    lats = [c[1] for c in coords]
    return [min(lons), min(lats), max(lons), max(lats)]


def _flatten_coords(obj):
    if isinstance(obj[0], (int, float)):
        return [obj]
    return [c for sub in obj for c in _flatten_coords(sub)]


def _tiff_to_numpy(tiff_bytes: bytes) -> np.ndarray:
    """Convert a multi-band GeoTIFF byte string to a NumPy array."""
    try:
        import rasterio
        from rasterio.io import MemoryFile
        with MemoryFile(tiff_bytes) as mf:
            with mf.open() as ds:
                return ds.read().astype(np.float32)
    except ImportError:
        # Rasterio not installed — fall back to PIL (single band only)
        img = Image.open(io.BytesIO(tiff_bytes))
        return np.array(img, dtype=np.float32)[np.newaxis, ...]


def _unpack_bands(index_name: str, data: np.ndarray) -> Dict[str, np.ndarray]:
    """Map ordered band array back to named bands for compute_index()."""
    band_order = {
        "NDVI":  ["B04", "B08"],
        "NDWI":  ["B03", "B08"],
        "EVI":   ["B02", "B04", "B08"],
        "SAVI":  ["B04", "B08"],
        "NDMI":  ["B8A", "B11"],
    }
    names = band_order[index_name.upper()]
    return {name: data[i] for i, name in enumerate(names)}
