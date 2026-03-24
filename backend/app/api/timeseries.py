"""
/api/timeseries — return time-series data for selected AOI and indices.
"""

from fastapi import APIRouter
from typing import Dict, List

from app.core.schemas import TimeseriesRequest, TimeseriesResponse, TimeseriesPoint
from app.services.timeseries import compute_timeseries
from app.services.indices import INDEX_META

router = APIRouter()


@router.post("/", response_model=Dict[str, TimeseriesResponse])
async def get_timeseries(body: TimeseriesRequest):
    """
    Compute and return time-series of mean index values over the AOI.
    Returns a dict keyed by index name.
    """
    results: Dict[str, TimeseriesResponse] = {}

    for index_type in body.indices:
        name = index_type.value
        points = await compute_timeseries(
            aoi=body.aoi,
            start_date=body.start_date,
            end_date=body.end_date,
            index_name=name,
            cloud_cover_max=body.cloud_cover_max,
            temporal_resolution=body.temporal_resolution,
        )
        meta = INDEX_META[name]
        results[name] = TimeseriesResponse(
            index=name,
            unit=meta["unit"],
            data=points,
        )

    return results
