"""
Simple two-level cache: in-memory LRU + optional disk cache for tiles.
"""

import hashlib
import json
import logging
import os
import time
from functools import lru_cache
from pathlib import Path
from typing import Any, Optional

logger = logging.getLogger(__name__)

CACHE_DIR = Path(os.getenv("TILE_CACHE_DIR", "/tmp/sentinel_tile_cache"))
CACHE_DIR.mkdir(parents=True, exist_ok=True)

# ── In-memory dict cache (for small objects like stats / timeseries) ──────────
_mem_cache: dict[str, tuple[Any, float]] = {}


def cache_key(*args, **kwargs) -> str:
    """Stable SHA-1 key from arbitrary JSON-serialisable arguments."""
    data = json.dumps({"args": args, "kwargs": kwargs}, sort_keys=True, default=str)
    return hashlib.sha1(data.encode()).hexdigest()


def mem_set(key: str, value: Any, ttl: int = 3600) -> None:
    _mem_cache[key] = (value, time.time() + ttl)


def mem_get(key: str) -> Optional[Any]:
    entry = _mem_cache.get(key)
    if entry is None:
        return None
    value, expires_at = entry
    if time.time() > expires_at:
        del _mem_cache[key]
        return None
    return value


# ── Disk tile cache ───────────────────────────────────────────────────────────

def tile_path(layer: str, z: int, x: int, y: int) -> Path:
    return CACHE_DIR / layer / str(z) / str(x) / f"{y}.png"


def tile_exists(layer: str, z: int, x: int, y: int, max_age: int = 86400) -> bool:
    p = tile_path(layer, z, x, y)
    if not p.exists():
        return False
    return (time.time() - p.stat().st_mtime) < max_age


def tile_read(layer: str, z: int, x: int, y: int) -> Optional[bytes]:
    p = tile_path(layer, z, x, y)
    try:
        return p.read_bytes()
    except Exception:
        return None


def tile_write(layer: str, z: int, x: int, y: int, data: bytes) -> None:
    p = tile_path(layer, z, x, y)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_bytes(data)
