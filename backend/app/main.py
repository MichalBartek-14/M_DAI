"""
Sentinel-2 Vegetation Dashboard — FastAPI Backend
Entry point for the application.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware

from app.api import indices, timeseries, tiles, stats, export
from app.core.config import settings

app = FastAPI(
    title="Sentinel-2 Vegetation Dashboard API",
    description="Compute and serve vegetation indices from Sentinel-2 imagery.",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
)

# ── Middleware ────────────────────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(GZipMiddleware, minimum_size=1000)

# ── Routers ───────────────────────────────────────────────────────────────────
app.include_router(indices.router,    prefix="/api/indices",    tags=["Indices"])
app.include_router(timeseries.router, prefix="/api/timeseries", tags=["Time-series"])
app.include_router(tiles.router,      prefix="/api/tiles",      tags=["Tiles"])
app.include_router(stats.router,      prefix="/api/stats",      tags=["Statistics"])
app.include_router(export.router,     prefix="/api/export",     tags=["Export"])


@app.get("/api/health", tags=["Health"])
async def health_check():
    return {"status": "ok", "version": "1.0.0"}
