"""
Colormap rendering: float32 index arrays → RGBA PNG bytes.

Uses matplotlib colormaps for professional-grade colour scales.
"""

import io
from typing import Optional, Tuple

import numpy as np
from PIL import Image

# Try matplotlib; fall back to a simple linear interpolation if unavailable
try:
    import matplotlib
    matplotlib.use("Agg")  # Non-interactive backend
    import matplotlib.pyplot as plt
    import matplotlib.colors as mcolors
    HAS_MPL = True
except ImportError:
    HAS_MPL = False


# ── Colormap definitions ──────────────────────────────────────────────────────
# (name → list of (value, RGBA) stops for the fallback renderer)

SIMPLE_COLORMAPS = {
    "RdYlGn": [
        (-1.0, (215, 25,  28,  255)),
        (-0.2, (253, 174, 97,  255)),
        ( 0.0, (255, 255, 191, 255)),
        ( 0.4, (166, 217, 106, 255)),
        ( 1.0, (26,  150, 65,  255)),
    ],
    "Blues": [
        (-1.0, (247, 251, 255, 50)),
        ( 0.0, (198, 219, 239, 180)),
        ( 0.5, (66,  146, 198, 230)),
        ( 1.0, (8,   48,  107, 255)),
    ],
    "viridis": [
        (-1.0, (68,  1,   84,  255)),
        (-0.3, (59,  82,  139, 255)),
        ( 0.1, (33,  145, 140, 255)),
        ( 0.5, (94,  201, 98,  255)),
        ( 1.0, (253, 231, 37,  255)),
    ],
    "YlGn": [
        (-1.5, (255, 255, 229, 50)),
        ( 0.0, (194, 230, 153, 200)),
        ( 0.5, (49,  163, 84,  255)),
        ( 1.5, (0,   104, 55,  255)),
    ],
    "BrBG": [
        (-1.0, (84,  48,  5,   255)),
        (-0.3, (193, 120, 43,  255)),
        ( 0.0, (246, 232, 195, 255)),
        ( 0.3, (128, 205, 193, 255)),
        ( 1.0, (1,   133, 113, 255)),
    ],
}


def index_to_png(
    arr: np.ndarray,
    colormap_name: str = "RdYlGn",
    value_range: Tuple[float, float] = (-1.0, 1.0),
    alpha_nan: int = 0,
) -> bytes:
    """
    Convert a 2-D float32 index array to an RGBA PNG, returned as bytes.

    NaN pixels are rendered fully transparent.
    """
    lo, hi = value_range

    if HAS_MPL:
        return _mpl_render(arr, colormap_name, lo, hi, alpha_nan)
    else:
        return _simple_render(arr, colormap_name, lo, hi, alpha_nan)


def _mpl_render(arr, cmap_name, lo, hi, alpha_nan) -> bytes:
    """High-quality matplotlib render."""
    cmap = plt.get_cmap(cmap_name).copy()
    cmap.set_bad(alpha=0)          # NaN → transparent

    norm = mcolors.Normalize(vmin=lo, vmax=hi, clip=True)
    rgba = cmap(norm(np.ma.masked_invalid(arr)))   # (H, W, 4)  float [0,1]
    rgba_u8 = (rgba * 255).astype(np.uint8)

    img = Image.fromarray(rgba_u8, mode="RGBA")
    buf = io.BytesIO()
    img.save(buf, format="PNG", optimize=True)
    return buf.getvalue()


def _simple_render(arr, cmap_name, lo, hi, alpha_nan) -> bytes:
    """Pure-NumPy fallback renderer (no matplotlib dependency)."""
    stops = SIMPLE_COLORMAPS.get(cmap_name, SIMPLE_COLORMAPS["RdYlGn"])
    stop_vals   = np.array([s[0] for s in stops], dtype=np.float32)
    stop_colors = np.array([s[1] for s in stops], dtype=np.float32)

    h, w = arr.shape
    rgba = np.zeros((h, w, 4), dtype=np.uint8)

    # Normalise to [0, 1] across stops range
    clipped = np.clip(arr, lo, hi)
    nan_mask = ~np.isfinite(arr)

    for c in range(4):
        channel = np.interp(clipped.ravel(), stop_vals, stop_colors[:, c])
        rgba[:, :, c] = channel.reshape(h, w).astype(np.uint8)

    rgba[nan_mask, 3] = alpha_nan

    img = Image.fromarray(rgba, mode="RGBA")
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()


def colormap_legend_png(
    colormap_name: str = "RdYlGn",
    value_range: Tuple[float, float] = (-1.0, 1.0),
    width: int = 300,
    height: int = 40,
) -> bytes:
    """Generate a horizontal colormap legend bar as PNG."""
    gradient = np.linspace(value_range[0], value_range[1], width, dtype=np.float32)
    bar = np.tile(gradient, (height, 1))
    return index_to_png(bar, colormap_name, value_range)
