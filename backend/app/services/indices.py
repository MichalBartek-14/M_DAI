"""
Spectral / vegetation index formulas.

All functions accept NumPy arrays of float32 band reflectances (0–1 scale)
and return a float32 index array with NaN where computation is invalid.

Sentinel-2 band mapping (10 / 20 m):
  B02 = Blue    (490 nm)
  B03 = Green   (560 nm)
  B04 = Red     (665 nm)
  B05 = Red Edge (705 nm)
  B08 = NIR broad (842 nm)   — 10 m
  B8A = NIR narrow (865 nm)  — 20 m
  B11 = SWIR1  (1610 nm)     — 20 m
  B12 = SWIR2  (2190 nm)     — 20 m
"""

from typing import Dict, Tuple

import numpy as np


def _safe_div(a: np.ndarray, b: np.ndarray) -> np.ndarray:
    """Divide a by b, returning NaN where b == 0."""
    with np.errstate(invalid="ignore", divide="ignore"):
        result = np.where(b == 0, np.nan, a / b)
    return result.astype(np.float32)


# ── Index functions ───────────────────────────────────────────────────────────

def ndvi(nir: np.ndarray, red: np.ndarray) -> np.ndarray:
    """
    NDVI = (NIR - Red) / (NIR + Red)
    Range: [-1, 1]  — vegetation > 0.2, dense vegetation > 0.6
    Uses B08 (NIR) and B04 (Red).
    """
    return _safe_div(nir - red, nir + red)


def ndwi(green: np.ndarray, nir: np.ndarray) -> np.ndarray:
    """
    NDWI = (Green - NIR) / (Green + NIR)   [McFeeters 1996]
    Range: [-1, 1]  — water > 0, vegetation < 0
    Uses B03 (Green) and B08 (NIR).
    """
    return _safe_div(green - nir, green + nir)


def evi(nir: np.ndarray, red: np.ndarray, blue: np.ndarray,
        G: float = 2.5, C1: float = 6.0, C2: float = 7.5, L: float = 1.0) -> np.ndarray:
    """
    EVI = G * (NIR - Red) / (NIR + C1*Red - C2*Blue + L)
    Range: [-1, 1]  — less saturation than NDVI in dense canopies
    Uses B08, B04, B02.
    """
    denom = nir + C1 * red - C2 * blue + L
    return _safe_div(G * (nir - red), denom).clip(-1, 1).astype(np.float32)


def savi(nir: np.ndarray, red: np.ndarray, L: float = 0.5) -> np.ndarray:
    """
    SAVI = (NIR - Red) / (NIR + Red + L) * (1 + L)
    L=0.5 is the standard value.
    Range: [-1.5, 1.5]
    Uses B08, B04.
    """
    denom = nir + red + L
    return (_safe_div((nir - red), denom) * (1 + L)).astype(np.float32)


def ndmi(nir: np.ndarray, swir1: np.ndarray) -> np.ndarray:
    """
    NDMI = (NIR - SWIR1) / (NIR + SWIR1)
    Range: [-1, 1]  — high moisture > 0.4
    Uses B8A (NIR narrow) and B11 (SWIR1).
    """
    return _safe_div(nir - swir1, nir + swir1)


# ── Registry ──────────────────────────────────────────────────────────────────

INDEX_META: Dict[str, Dict] = {
    "NDVI": {
        "label":   "Normalized Difference Vegetation Index",
        "range":   (-1.0, 1.0),
        "colormap":"RdYlGn",
        "unit":    "dimensionless",
        "bands":   ["B08", "B04"],
        "description": "Measures live green vegetation. Values > 0.5 indicate dense, healthy vegetation.",
    },
    "NDWI": {
        "label":   "Normalized Difference Water Index",
        "range":   (-1.0, 1.0),
        "colormap":"Blues",
        "unit":    "dimensionless",
        "bands":   ["B03", "B08"],
        "description": "Highlights open water bodies. Values > 0 indicate water presence.",
    },
    "EVI": {
        "label":   "Enhanced Vegetation Index",
        "range":   (-1.0, 1.0),
        "colormap":"viridis",
        "unit":    "dimensionless",
        "bands":   ["B08", "B04", "B02"],
        "description": "Improved vegetation index that reduces atmospheric distortion and soil noise.",
    },
    "SAVI": {
        "label":   "Soil-Adjusted Vegetation Index",
        "range":   (-1.5, 1.5),
        "colormap":"YlGn",
        "unit":    "dimensionless",
        "bands":   ["B08", "B04"],
        "description": "Minimises soil brightness influence. Useful for arid / sparsely vegetated areas.",
    },
    "NDMI": {
        "label":   "Normalized Difference Moisture Index",
        "range":   (-1.0, 1.0),
        "colormap":"BrBG",
        "unit":    "dimensionless",
        "bands":   ["B8A", "B11"],
        "description": "Sensitive to moisture content in vegetation canopy. High values → well-watered.",
    },
}


def compute_index(
    index_name: str,
    bands: Dict[str, np.ndarray],
) -> np.ndarray:
    """
    Dispatch to the correct index function given a dict of band arrays.
    Band keys: B02, B03, B04, B08, B8A, B11, B12.
    """
    n = index_name.upper()
    if n == "NDVI":
        return ndvi(bands["B08"], bands["B04"])
    elif n == "NDWI":
        return ndwi(bands["B03"], bands["B08"])
    elif n == "EVI":
        return evi(bands["B08"], bands["B04"], bands["B02"])
    elif n == "SAVI":
        return savi(bands["B08"], bands["B04"])
    elif n == "NDMI":
        return ndmi(bands["B8A"], bands["B11"])
    else:
        raise ValueError(f"Unknown index: {index_name}")


def array_stats(arr: np.ndarray) -> Dict[str, float]:
    """Compute descriptive statistics, ignoring NaN pixels."""
    valid = arr[np.isfinite(arr)]
    if valid.size == 0:
        return {"mean": None, "median": None, "std": None, "min": None, "max": None, "valid_pct": 0.0}
    return {
        "mean":      float(np.mean(valid)),
        "median":    float(np.median(valid)),
        "std":       float(np.std(valid)),
        "min":       float(np.min(valid)),
        "max":       float(np.max(valid)),
        "valid_pct": float(valid.size / arr.size * 100),
    }
