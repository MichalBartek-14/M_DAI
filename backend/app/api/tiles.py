"""
/api/tiles/{index}/{z}/{x}/{y}.png — XYZ tile server.

Tiles are cached to disk after first render.
"""

from datetime import date

from fastapi import APIRouter, Query, Path, HTTPException
from fastapi.responses import Response

from app.core.cache import tile_exists, tile_read, tile_write, cache_key
from app.core.schemas import AOI, BoundingBox
from app.services.sentinel import render_index_tile

router = APIRouter()


@router.get("/{index_name}/{z}/{x}/{y}.png")
async def get_tile(
    index_name: str  = Path(..., description="Index name, e.g. NDVI"),
    z: int           = Path(..., ge=0, le=18),
    x: int           = Path(...),
    y: int           = Path(...),
    start:  str      = Query(..., description="Start date YYYY-MM-DD"),
    end:    str      = Query(..., description="End date YYYY-MM-DD"),
    bbox:   str      = Query("auto", description="min_lon,min_lat,max_lon,max_lat"),
    cloud:  int      = Query(30, ge=0, le=100),
    res:    int      = Query(10, ge=10, le=60),
):
    """
    Render and return a 256×256 PNG tile for the requested index/zoom/tile.
    Results are cached on disk for 24 h.
    """
    index_name = index_name.upper()
    layer_key  = f"{index_name}_{start}_{end}_{bbox}_{cloud}"

    # ── Cache hit ──────────────────────────────────────────────────────────
    if tile_exists(layer_key, z, x, y):
        data = tile_read(layer_key, z, x, y)
        if data:
            return Response(content=data, media_type="image/png",
                            headers={"Cache-Control": "public, max-age=86400"})

    # ── Parse AOI from bbox param ──────────────────────────────────────────
    aoi = _bbox_to_aoi(bbox, z, x, y)

    try:
        start_date = date.fromisoformat(start)
        end_date   = date.fromisoformat(end)
    except ValueError:
        raise HTTPException(400, "Invalid date format — use YYYY-MM-DD")

    # ── Render tile ────────────────────────────────────────────────────────
    png_bytes = await render_index_tile(
        index_name=index_name,
        aoi=aoi,
        start_date=start_date,
        end_date=end_date,
        z=z, x=x, y=y,
        resolution=res,
    )

    # ── Cache and return ───────────────────────────────────────────────────
    tile_write(layer_key, z, x, y, png_bytes)
    return Response(content=png_bytes, media_type="image/png",
                    headers={"Cache-Control": "public, max-age=86400"})


def _bbox_to_aoi(bbox_str: str, z: int, x: int, y: int) -> AOI:
    """Parse bbox query param; fall back to tile bbox if 'auto'."""
    if bbox_str == "auto":
        # Derive geographic bbox from Web Mercator tile coordinates
        lon_min, lat_min, lon_max, lat_max = _tile_to_bbox(z, x, y)
    else:
        parts = [float(p) for p in bbox_str.split(",")]
        lon_min, lat_min, lon_max, lat_max = parts

    return AOI(bbox=BoundingBox(
        min_lon=lon_min, min_lat=lat_min,
        max_lon=lon_max, max_lat=lat_max,
    ))


def _tile_to_bbox(z: int, x: int, y: int):
    """Convert XYZ tile indices to WGS-84 bounding box."""
    import math
    n = 2 ** z
    lon_min = x / n * 360.0 - 180.0
    lon_max = (x + 1) / n * 360.0 - 180.0
    lat_min = math.degrees(math.atan(math.sinh(math.pi * (1 - 2 * (y + 1) / n))))
    lat_max = math.degrees(math.atan(math.sinh(math.pi * (1 - 2 * y / n))))
    return lon_min, lat_min, lon_max, lat_max
