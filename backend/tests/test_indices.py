"""
Unit tests for index computation service.
Run with: pytest tests/ -v
"""

import numpy as np
import pytest

from app.services.indices import ndvi, ndwi, evi, savi, ndmi, compute_index, array_stats, INDEX_META
from app.services.colormap import index_to_png


# ── Index formula tests ───────────────────────────────────────────────────────

class TestNDVI:
    def test_healthy_vegetation(self):
        nir = np.array([[0.8]], dtype=np.float32)
        red = np.array([[0.1]], dtype=np.float32)
        result = ndvi(nir, red)
        assert result[0, 0] == pytest.approx((0.8 - 0.1) / (0.8 + 0.1), abs=1e-5)

    def test_range(self):
        nir = np.random.rand(64, 64).astype(np.float32)
        red = np.random.rand(64, 64).astype(np.float32)
        result = ndvi(nir, red)
        valid = result[np.isfinite(result)]
        assert np.all(valid >= -1.0) and np.all(valid <= 1.0)

    def test_zero_denominator_is_nan(self):
        nir = np.array([[0.0]], dtype=np.float32)
        red = np.array([[0.0]], dtype=np.float32)
        result = ndvi(nir, red)
        assert np.isnan(result[0, 0])


class TestNDWI:
    def test_water(self):
        green = np.array([[0.15]], dtype=np.float32)
        nir   = np.array([[0.05]], dtype=np.float32)
        result = ndwi(green, nir)
        assert result[0, 0] > 0  # Water should be positive

    def test_vegetation_negative(self):
        green = np.array([[0.1]], dtype=np.float32)
        nir   = np.array([[0.6]], dtype=np.float32)
        result = ndwi(green, nir)
        assert result[0, 0] < 0  # Vegetation should be negative


class TestEVI:
    def test_output_range(self):
        nir  = np.random.rand(32, 32).astype(np.float32)
        red  = np.random.rand(32, 32).astype(np.float32) * 0.3
        blue = np.random.rand(32, 32).astype(np.float32) * 0.1
        result = evi(nir, red, blue)
        valid = result[np.isfinite(result)]
        assert np.all(valid >= -1.0) and np.all(valid <= 1.0)


class TestComputeIndex:
    def test_dispatch_all_indices(self):
        bands = {
            'B02': np.ones((16, 16), dtype=np.float32) * 0.05,
            'B03': np.ones((16, 16), dtype=np.float32) * 0.10,
            'B04': np.ones((16, 16), dtype=np.float32) * 0.08,
            'B08': np.ones((16, 16), dtype=np.float32) * 0.40,
            'B8A': np.ones((16, 16), dtype=np.float32) * 0.38,
            'B11': np.ones((16, 16), dtype=np.float32) * 0.15,
        }
        for name in INDEX_META.keys():
            result = compute_index(name, bands)
            assert result.shape == (16, 16), f"Wrong shape for {name}"
            assert result.dtype == np.float32, f"Wrong dtype for {name}"

    def test_unknown_index_raises(self):
        with pytest.raises(ValueError):
            compute_index('FAKE', {})


class TestArrayStats:
    def test_basic_stats(self):
        arr = np.array([[0.1, 0.2], [0.3, 0.4]], dtype=np.float32)
        stats = array_stats(arr)
        assert stats['mean']   == pytest.approx(0.25, abs=1e-5)
        assert stats['min']    == pytest.approx(0.10, abs=1e-5)
        assert stats['max']    == pytest.approx(0.40, abs=1e-5)
        assert stats['valid_pct'] == 100.0

    def test_nan_handling(self):
        arr = np.array([[0.5, np.nan], [0.3, np.nan]], dtype=np.float32)
        stats = array_stats(arr)
        assert stats['valid_pct'] == pytest.approx(50.0, abs=1e-3)
        assert stats['mean'] == pytest.approx(0.4, abs=1e-5)

    def test_all_nan(self):
        arr = np.full((4, 4), np.nan, dtype=np.float32)
        stats = array_stats(arr)
        assert stats['valid_pct'] == 0.0
        assert stats['mean'] is None


class TestColormap:
    def test_png_output(self):
        arr = np.linspace(-1, 1, 256, dtype=np.float32).reshape(16, 16)
        png = index_to_png(arr, 'RdYlGn', (-1.0, 1.0))
        assert isinstance(png, bytes)
        assert len(png) > 100
        assert png[:4] == b'\x89PNG'  # Valid PNG magic bytes

    def test_nan_transparent(self):
        from PIL import Image
        import io
        arr = np.full((8, 8), np.nan, dtype=np.float32)
        png = index_to_png(arr, 'RdYlGn', (-1.0, 1.0), alpha_nan=0)
        img = Image.open(io.BytesIO(png))
        rgba = np.array(img.convert('RGBA'))
        assert np.all(rgba[:, :, 3] == 0)  # All alpha=0
