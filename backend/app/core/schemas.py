"""
Shared Pydantic schemas used across the API.
"""

from datetime import date
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple

from pydantic import BaseModel, Field, field_validator, model_validator


# ── Enumerations ──────────────────────────────────────────────────────────────

class IndexType(str, Enum):
    NDVI  = "NDVI"    # Normalized Difference Vegetation Index
    NDWI  = "NDWI"    # Normalized Difference Water Index
    EVI   = "EVI"     # Enhanced Vegetation Index
    SAVI  = "SAVI"    # Soil-Adjusted Vegetation Index
    NDMI  = "NDMI"    # Normalized Difference Moisture Index


class ColorMap(str, Enum):
    RDYLGN  = "RdYlGn"    # Red→Yellow→Green  (NDVI)
    BLUES   = "Blues"     # Blues              (NDWI)
    VIRIDIS = "viridis"   # Viridis            (EVI)
    BRBG    = "BrBG"      # Brown→Blue-Green   (NDMI)
    SPECTRAL= "Spectral"  # Spectral           (generic)


# ── Geometry ──────────────────────────────────────────────────────────────────

class BoundingBox(BaseModel):
    """Simple lat/lon bounding box."""
    min_lon: float = Field(..., ge=-180, le=180)
    min_lat: float = Field(..., ge=-90,  le=90)
    max_lon: float = Field(..., ge=-180, le=180)
    max_lat: float = Field(..., ge=-90,  le=90)

    @field_validator("max_lon")
    @classmethod
    def max_lon_gt_min(cls, v, info):
        if info.data.get("min_lon") is not None and v <= info.data["min_lon"]:
            raise ValueError("max_lon must be greater than min_lon")
        return v

    @field_validator("max_lat")
    @classmethod
    def max_lat_gt_min(cls, v, info):
        if info.data.get("min_lat") is not None and v <= info.data["min_lat"]:
            raise ValueError("max_lat must be greater than min_lat")
        return v


class GeoJSONGeometry(BaseModel):
    """Accepts Polygon or MultiPolygon GeoJSON geometry."""
    type: str
    coordinates: List[Any]


class AOI(BaseModel):
    """Area of Interest — either a bbox or a GeoJSON geometry."""
    bbox: Optional[BoundingBox] = None
    geometry: Optional[GeoJSONGeometry] = None

    model_config = {"arbitrary_types_allowed": True}

    @model_validator(mode="after")
    def bbox_or_geometry_required(self):
        if self.bbox is None and self.geometry is None:
            raise ValueError("Provide either bbox or geometry")
        return self


# ── Request / Response models ─────────────────────────────────────────────────

class IndexRequest(BaseModel):
    aoi: AOI
    start_date: date
    end_date: date
    index: IndexType = IndexType.NDVI
    cloud_cover_max: int = Field(30, ge=0, le=100)
    resolution: int = Field(10, ge=10, le=60)   # metres per pixel


class TimeseriesRequest(BaseModel):
    aoi: AOI
    start_date: date
    end_date: date
    indices: List[IndexType] = [IndexType.NDVI]
    cloud_cover_max: int = Field(30, ge=0, le=100)
    temporal_resolution: str = "16D"            # e.g. '16D', '1M'


class TimeseriesPoint(BaseModel):
    date: str
    value: Optional[float]
    valid_pixels: int


class TimeseriesResponse(BaseModel):
    index: str
    unit: str
    data: List[TimeseriesPoint]


class SceneMetadata(BaseModel):
    scene_id: str
    date: str
    cloud_cover: float
    tile_id: str
    preview_url: Optional[str] = None


class IndexResponse(BaseModel):
    index: str
    date_range: Tuple[str, str]
    scene_count: int
    scenes: List[SceneMetadata]
    tile_url: str                               # XYZ tile endpoint
    stats: Dict[str, float]
    colormap: str
    value_range: Tuple[float, float]


class AreaStats(BaseModel):
    index: str
    date: str
    mean: float
    median: float
    std: float
    min: float
    max: float
    valid_pixel_pct: float
    area_km2: float
    histogram: Dict[str, Any]
