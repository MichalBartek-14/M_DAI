"""
/api/indices — compute and return index metadata + tile URL.
"""

from datetime import date
from typing import Optional

from fastapi import APIRouter, Query, HTTPException
from fastapi.responses import JSONResponse

from app.core.schemas import IndexRequest, IndexResponse, IndexType, AOI, BoundingBox
from app.services.sentinel import search_scenes, generate_demo_index
from app.services.indices import INDEX_META, array_stats

router = APIRouter()


@router.post("/compute", response_model=IndexResponse)
async def compute_index(body: IndexRequest):
    """
    Given an AOI and date range, return scene metadata and a tile URL
    for the requested vegetation index.
    """
    scenes = await search_scenes(
        aoi=body.aoi,
        start_date=body.start_date,
        end_date=body.end_date,
        cloud_cover_max=body.cloud_cover_max,
    )

    meta = INDEX_META[body.index.value]

    # Build the XYZ tile endpoint URL (consumed by the frontend map)
    tile_url = (
        f"/api/tiles/{body.index.value}"
        f"?start={body.start_date.isoformat()}"
        f"&end={body.end_date.isoformat()}"
        f"&bbox={_bbox_str(body.aoi)}"
        f"&cloud={body.cloud_cover_max}"
        f"&res={body.resolution}"
        f"&z={{z}}&x={{x}}&y={{y}}"
    )

    # Generate quick stats from demo/cached data
    demo_arr = generate_demo_index(body.index.value, 128, 128)
    stats = array_stats(demo_arr)

    return IndexResponse(
        index=body.index.value,
        date_range=(body.start_date.isoformat(), body.end_date.isoformat()),
        scene_count=len(scenes),
        scenes=scenes,
        tile_url=tile_url,
        stats=stats,
        colormap=meta["colormap"],
        value_range=meta["range"],
    )


@router.get("/meta")
async def index_metadata():
    """Return metadata for all supported indices."""
    return INDEX_META


@router.get("/meta/{index_name}")
async def single_index_metadata(index_name: str):
    """Return metadata for a specific index."""
    name = index_name.upper()
    if name not in INDEX_META:
        raise HTTPException(404, f"Index '{index_name}' not found")
    return INDEX_META[name]


def _bbox_str(aoi: AOI) -> str:
    if aoi.bbox:
        b = aoi.bbox
        return f"{b.min_lon},{b.min_lat},{b.max_lon},{b.max_lat}"
    return "auto"
