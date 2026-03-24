"""
Application configuration — reads from environment variables / .env file.
"""

from functools import lru_cache
from typing import List

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    # ── Sentinel Hub ─────────────────────────────────────────────────────────
    # Obtain credentials at https://www.sentinel-hub.com/
    SENTINELHUB_CLIENT_ID: str = ""
    SENTINELHUB_CLIENT_SECRET: str = ""
    SENTINELHUB_INSTANCE_ID: str = ""          # For WMS/WMTS
    SENTINELHUB_BASE_URL: str = "https://services.sentinel-hub.com"

    # ── Copernicus Dataspace (alternative / free) ─────────────────────────────
    # Register at https://dataspace.copernicus.eu/
    COPERNICUS_CLIENT_ID: str = "cdse-public"  # Public STAC access
    COPERNICUS_STAC_URL: str = "https://catalogue.dataspace.copernicus.eu/stac"
    COPERNICUS_OGC_URL: str = "https://sh.dataspace.copernicus.eu"

    # ── Google Earth Engine (optional) ───────────────────────────────────────
    GEE_SERVICE_ACCOUNT: str = ""
    GEE_KEY_FILE: str = ""                     # Path to JSON key file
    USE_GEE: bool = False                      # Toggle GEE backend

    # ── App settings ──────────────────────────────────────────────────────────
    ALLOWED_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:5173",
        "https://m-dai.vercel.app",
        "https://*.vercel.app",
        "https://*.netlify.app",
    ]
    CACHE_TTL_SECONDS: int = 3600            # 1 hour tile cache
    MAX_AOI_AREA_KM2: float = 5000.0         # Guard against huge requests
    DEFAULT_CLOUD_COVER: int = 30            # Max cloud cover % for scene search
    TILE_SIZE: int = 512                     # Pixels per map tile
    MAX_CONCURRENT_REQUESTS: int = 4


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
