"""
/api/stats — compute area statistics for a given index / AOI / date.
"""

import numpy as np
from datetime import date
from fastapi import APIRouter, Query
from typing import Optional

from app.core.schemas import AOI, BoundingBox, AreaStats
from app.services.sentinel import generate_demo_index, fetch_band_data, build_evalscript
from app.services.indices import compute_index, array_stats, INDEX_META

router = APIRouter()


@router.post("/area", response_model=AreaStats)
async def area_statistics(
    aoi: AOI,
    index: str,
    start_date: date,
    end_date: date,
    cloud_cover_max: int = Query(30, ge=0, le=100),
):
    """
    Compute statistics (mean, median, std, min, max) for an index
    over the specified AOI and date range.
    """
    index = index.upper()

    evalscript = build_evalscript(index)
    band_data = await fetch_band_data(
        aoi, evalscript, start_date, end_date,
        resolution=30, width=256, height=256,
    )

    if band_data is None:
        index_arr = generate_demo_index(index, 256, 256)
    else:
        from app.services.sentinel import _unpack_bands
        bands = _unpack_bands(index, band_data)
        index_arr = compute_index(index, bands)

    stats = array_stats(index_arr)

    # Build histogram (20 bins across value range)
    lo, hi = INDEX_META[index]["range"]
    valid = index_arr[np.isfinite(index_arr)]
    counts, edges = np.histogram(valid, bins=20, range=(lo, hi))
    histogram = {
        "bins":   edges[:-1].round(3).tolist(),
        "counts": counts.tolist(),
    }

    # Estimate area (rough: assume 10 m pixels, 256×256 grid)
    area_km2 = round((256 * 256 * 100) / 1e6, 2)

    return AreaStats(
        index=index,
        date=start_date.isoformat(),
        mean=round(stats["mean"] or 0, 4),
        median=round(stats["median"] or 0, 4),
        std=round(stats["std"] or 0, 4),
        min=round(stats["min"] or 0, 4),
        max=round(stats["max"] or 0, 4),
        valid_pixel_pct=round(stats["valid_pct"] or 0, 1),
        area_km2=area_km2,
        histogram=histogram,
    )
