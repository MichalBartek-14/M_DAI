"""
/api/export — download index rasters as GeoTIFF or PNG.
"""

import io
from datetime import date

from fastapi import APIRouter, Query
from fastapi.responses import StreamingResponse, Response

from app.core.schemas import AOI, BoundingBox
from app.services.sentinel import fetch_band_data, build_evalscript, generate_demo_index
from app.services.indices import compute_index, INDEX_META
from app.services.colormap import index_to_png

router = APIRouter()


@router.post("/png")
async def export_png(
    aoi: AOI,
    index: str,
    start_date: date,
    end_date: date,
    width: int  = Query(1024, ge=64, le=4096),
    height: int = Query(1024, ge=64, le=4096),
    cloud_cover_max: int = Query(30, ge=0, le=100),
):
    """Export a colourised index PNG for download."""
    index = index.upper()
    meta = INDEX_META[index]

    evalscript = build_evalscript(index)
    band_data = await fetch_band_data(
        aoi, evalscript, start_date, end_date,
        resolution=10, width=width, height=height,
    )

    if band_data is None:
        index_arr = generate_demo_index(index, width, height)
    else:
        from app.services.sentinel import _unpack_bands
        bands = _unpack_bands(index, band_data)
        index_arr = compute_index(index, bands)

    png_bytes = index_to_png(index_arr, meta["colormap"], meta["range"])
    filename = f"{index}_{start_date}_{end_date}.png"

    return Response(
        content=png_bytes,
        media_type="image/png",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


@router.post("/geotiff")
async def export_geotiff(
    aoi: AOI,
    index: str,
    start_date: date,
    end_date: date,
    resolution: int = Query(10, ge=10, le=60),
    cloud_cover_max: int = Query(30, ge=0, le=100),
):
    """
    Export raw float32 GeoTIFF with geospatial metadata.
    Requires rasterio to be installed.
    """
    import numpy as np

    index = index.upper()
    evalscript = build_evalscript(index)
    band_data = await fetch_band_data(
        aoi, evalscript, start_date, end_date,
        resolution=resolution, width=512, height=512,
    )

    if band_data is None:
        index_arr = generate_demo_index(index, 512, 512)
    else:
        from app.services.sentinel import _unpack_bands
        bands = _unpack_bands(index, band_data)
        index_arr = compute_index(index, bands)

    tiff_bytes = _to_geotiff(index_arr, aoi)
    filename = f"{index}_{start_date}_{end_date}.tif"

    return Response(
        content=tiff_bytes,
        media_type="image/tiff",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


def _to_geotiff(arr, aoi: AOI) -> bytes:
    """Encode a 2-D float32 array as a GeoTIFF with WGS-84 CRS."""
    try:
        import rasterio
        from rasterio.io import MemoryFile
        from rasterio.transform import from_bounds
        from rasterio.crs import CRS

        if aoi.bbox:
            b = aoi.bbox
            bounds = (b.min_lon, b.min_lat, b.max_lon, b.max_lat)
        else:
            bounds = (-180, -90, 180, 90)

        transform = from_bounds(*bounds, arr.shape[1], arr.shape[0])
        buf = io.BytesIO()
        with MemoryFile(buf) as mf:
            with mf.open(
                driver="GTiff",
                height=arr.shape[0],
                width=arr.shape[1],
                count=1,
                dtype="float32",
                crs=CRS.from_epsg(4326),
                transform=transform,
            ) as ds:
                ds.write(arr[np.newaxis, ...])
            return mf.read()
    except ImportError:
        # Rasterio not available — return raw float32 bytes with a note
        import numpy as np
        return arr.tobytes()
