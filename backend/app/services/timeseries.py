"""
Time-series service: compute mean index value over AOI for each available date.
"""

import logging
from datetime import date, timedelta
from typing import List

import numpy as np

from app.core.schemas import AOI, IndexType, TimeseriesPoint
from app.services.sentinel import fetch_band_data, build_evalscript, generate_demo_index, search_scenes
from app.services.indices import compute_index, array_stats

logger = logging.getLogger(__name__)


async def compute_timeseries(
    aoi: AOI,
    start_date: date,
    end_date: date,
    index_name: str,
    cloud_cover_max: int = 30,
    temporal_resolution: str = "16D",
) -> List[TimeseriesPoint]:
    """
    Return a list of (date, mean_index_value) points for the AOI.
    Uses 16-day composite windows by default to match Sentinel-2 revisit time.
    """

    # Build list of date windows
    windows = _date_windows(start_date, end_date, temporal_resolution)

    points: List[TimeseriesPoint] = []

    for win_start, win_end in windows:
        try:
            evalscript = build_evalscript(index_name)
            band_data = await fetch_band_data(
                aoi, evalscript, win_start, win_end,
                resolution=60,  # Use 60 m for speed in timeseries
                width=128, height=128,
            )

            if band_data is None:
                # Demo mode — generate synthetic value with seasonal pattern
                index_arr = _demo_timeseries_value(win_start, index_name)
                valid_pixels = 128 * 128
            else:
                from app.services.sentinel import _unpack_bands
                bands = _unpack_bands(index_name, band_data)
                index_arr = compute_index(index_name, bands)
                valid_pixels = int(np.sum(np.isfinite(index_arr)))

            stats = array_stats(index_arr) if isinstance(index_arr, np.ndarray) else {"mean": index_arr}
            mean_val = stats.get("mean")

            points.append(TimeseriesPoint(
                date=win_start.isoformat(),
                value=round(float(mean_val), 4) if mean_val is not None else None,
                valid_pixels=valid_pixels,
            ))

        except Exception as e:
            logger.warning(f"Timeseries point failed for {win_start}: {e}")
            points.append(TimeseriesPoint(date=win_start.isoformat(), value=None, valid_pixels=0))

    return points


def _date_windows(start: date, end: date, resolution: str) -> List[tuple]:
    """Split date range into temporal windows."""
    days = 16
    if resolution == "1M":
        days = 30
    elif resolution == "8D":
        days = 8

    windows = []
    current = start
    while current <= end:
        win_end = min(current + timedelta(days=days - 1), end)
        windows.append((current, win_end))
        current += timedelta(days=days)
    return windows


def _demo_timeseries_value(d: date, index_name: str) -> float:
    """
    Produce a plausible seasonal index value for demo mode.
    Simulates a temperate vegetation cycle.
    """
    import math
    doy = d.timetuple().tm_yday  # Day of year (1-365)

    if index_name.upper() in ("NDVI", "EVI", "SAVI"):
        # Peak in northern-hemisphere summer ~DOY 180
        base = 0.55 + 0.30 * math.sin(math.pi * (doy - 60) / 200)
        noise = (hash(str(d)) % 100) / 1000
        return round(max(0.05, min(0.95, base + noise)), 4)

    elif index_name.upper() == "NDWI":
        base = -0.1 + 0.15 * math.cos(math.pi * doy / 183)
        noise = (hash(str(d)) % 100) / 2000
        return round(max(-0.5, min(0.5, base + noise)), 4)

    elif index_name.upper() == "NDMI":
        base = 0.1 + 0.20 * math.sin(math.pi * (doy - 80) / 200)
        noise = (hash(str(d)) % 100) / 1500
        return round(max(-0.3, min(0.8, base + noise)), 4)

    return 0.0
